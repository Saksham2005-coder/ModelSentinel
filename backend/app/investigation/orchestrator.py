import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.incident import Incident
from app.models.investigation import Investigation, InvestigationEvent, InvestigationHypothesis, InvestigationEvidence
from app.investigation.tool_registry import registry
from app.investigation.schemas import InvestigationPlan, HypothesisBase, InvestigationConclusion
from app.ai.service import get_llm_provider

logger = logging.getLogger(__name__)

class InvestigationOrchestrator:
    def __init__(self, db: Session, investigation_id: str):
        self.db = db
        self.investigation_id = investigation_id
        self.provider = get_llm_provider()
        self.inv = self.db.query(Investigation).filter(Investigation.id == self.investigation_id).first()
        if not self.inv:
            raise ValueError(f"Investigation {self.investigation_id} not found")
        self.incident = self.db.query(Incident).filter(Incident.id == self.inv.incident_id).first()
        self.evidence_cache: Dict[str, InvestigationEvidence] = {}

    def _add_event(self, event_type: str, title: str, message: str, status: str = "success", metadata: Optional[Dict] = None):
        event = InvestigationEvent(
            investigation_id=self.investigation_id,
            event_type=event_type,
            title=title,
            message=message,
            status=status,
            metadata_json=metadata
        )
        self.db.add(event)
        self.db.commit()
        logger.info(f"Investigation Event: {title} - {message}")

    def _get_deterministic_tools(self) -> List[str]:
        tools = ["get_incident_context", "get_monitoring_run", "get_model_version"]
        cat = self.incident.category if self.incident else ""
        if cat in ["performance_degradation", "prediction_drift", "concept_drift"]:
            tools.extend(["get_performance_metrics", "get_prediction_drift", "get_feature_drift", "get_segment_analysis"])
        elif cat == "data_quality":
            tools.extend(["get_data_quality"])
        elif cat == "feature_drift":
            tools.extend(["get_feature_drift", "get_segment_analysis"])
        else:
            tools.extend(["get_performance_metrics", "get_feature_drift", "get_data_quality"])
        
        valid_tools = [t["function"]["name"] for t in registry.get_tool_schemas()]
        logger.info(f"DEBUG tools: {tools}")
        logger.info(f"DEBUG valid_tools: {valid_tools}")
        return list(set(tools) & set(valid_tools))

    def _execute_tool(self, tool_name: str, kwargs: dict = None, source: str = "deterministic") -> dict:
        if kwargs is None:
            kwargs = {}
        try:
            from app.models.monitoring import MonitoringRun
            run = self.db.query(MonitoringRun).filter(MonitoringRun.model_version_id == self.incident.model_version_id).order_by(MonitoringRun.created_at.desc()).first()
            run_id = run.id if run else None
            
            context = {"incident_id": self.incident.id, "run_id": run_id, "db": self.db}
            res = registry.execute(tool_name, kwargs, context)
            
            event_type = "tool_completed" if source == "deterministic" else "ai_tool_completed"
            title_prefix = "Deterministic Tool" if source == "deterministic" else "AI Tool"
            self._add_event(event_type, f"{title_prefix} Executed: {tool_name}", f"Gathered data from {tool_name}.", metadata={"result": res})
            
            ev = InvestigationEvidence(
                investigation_id=self.investigation_id,
                evidence_type="tool_result",
                source_type=tool_name,
                title=f"Result of {tool_name}",
                value_json=res,
                relationship_type="context",
                explanation=f"Gathered via {source} tool execution."
            )
            self.db.add(ev)
            self.db.commit()
            self.evidence_cache[ev.id] = ev
            return res
        except Exception as e:
            event_type = "tool_failed" if source == "deterministic" else "ai_tool_failed"
            self._add_event(event_type, f"Tool Failed: {tool_name}", str(e), status="error")
            return {"error": str(e)}

    def run(self):
        try:
            self.inv.status = "running"
            self.inv.started_at = datetime.now(timezone.utc)
            self.db.commit()
            
            self._add_event("status_change", "Investigation Started", "The AI investigation engine has started.")

            from app.services.reliability_service import reliability_service
            inv_event = reliability_service.emit_event(
                db=self.db,
                model_id=self.incident.model_id,
                model_version_id=self.incident.model_version_id,
                event_type="INVESTIGATION_STARTED",
                source_type="investigation",
                source_id=self.investigation_id,
                title="AI Investigation Started",
                summary="AI investigation engine launched to find root cause.",
                status="running"
            )
            # Link to incident
            inc_event = reliability_service.find_event_by_source(self.db, "incident", self.incident.id, "INCIDENT_CREATED")
            if inc_event:
                reliability_service.link_events(self.db, inc_event.id, inv_event.id, "RESULTED_IN")

            # 1. LOAD INCIDENT
            if not self.incident:
                raise ValueError("Incident not found")
            self._add_event("context_loaded", "Incident Loaded", f"Loaded incident {self.incident.id} context.")

            # 2. DETERMINISTIC EVIDENCE COLLECTION
            tools_to_run = self._get_deterministic_tools()
            for tool_name in tools_to_run:
                self._execute_tool(tool_name, source="deterministic")

            # 3. OPTIONAL AI TOOL CALLING
            evidence_block = "Available Evidence:\n"
            for ev_id, ev in self.evidence_cache.items():
                evidence_block += f"Evidence ID: {ev_id}\nSource: {ev.source_type}\nData: {json.dumps(ev.value_json)}\n\n"

            tools = registry.get_tool_schemas()
            prompt = f"Incident: {self.incident.title}\nCategory: {self.incident.category}\n\n{evidence_block}\nDo you need to run any additional tools from the registry? Only request if absolutely necessary."
            system = "You are an AI ML investigator. Call tools to gather more evidence, or respond with a normal message if you have enough evidence."
            
            try:
                msg = self.provider.request_tool_calls(prompt, system, tools)
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_name = tc.function.name
                        try:
                            kwargs = json.loads(tc.function.arguments)
                        except:
                            kwargs = {}
                            
                        valid_tools = [t["function"]["name"] for t in tools]
                        if tool_name not in valid_tools:
                            self._add_event("ai_tool_failed", f"Invalid Tool Requested: {tool_name}", "Tool not in registry.", status="error")
                            continue
                            
                        self._add_event("ai_tool_requested", f"AI Requested Tool: {tool_name}", f"AI requested {tool_name} execution.")
                        self._execute_tool(tool_name, kwargs, source="ai_requested")
            except Exception as e:
                logger.warning(f"AI tool calling failed or not supported by provider: {e}")
                self._add_event("ai_tool_error", "AI Tool Call Failed", str(e), status="error")
                
            # Rebuild evidence block
            evidence_block = "Available Evidence:\n"
            for ev_id, ev in self.evidence_cache.items():
                evidence_block += f"Evidence ID: {ev_id}\nSource: {ev.source_type}\nData: {json.dumps(ev.value_json)}\n\n"

            # 4. GENERATE HYPOTHESES & EVALUATE
            tool_catalog_str = json.dumps(tools, indent=2)
            hypo_prompt = f"Incident: {self.incident.title}\nCategory: {self.incident.category}\n\n{evidence_block}\nGenerate 2 to 5 hypotheses for what caused this incident. Evaluate them against the provided evidence IDs. Only use the IDs provided."
            
            from pydantic import BaseModel
            class HypothesesList(BaseModel):
                hypotheses: List[HypothesisBase]

            system_hypo = "You are an AI ML investigator. Output a list of hypotheses evaluated strictly against the provided evidence IDs. Unsupported hypotheses MUST have status 'insufficient_evidence'."
            
            try:
                hypotheses_res: HypothesesList = self.provider.generate_structured(hypo_prompt, system_hypo, HypothesesList)
            except Exception as e:
                self._add_event("hypotheses_failed", "Hypothesis Generation Failed", str(e), status="error")
                raise e
            
            self._add_event("hypotheses_generated", "Hypotheses Generated", f"Generated {len(hypotheses_res.hypotheses)} hypotheses.")

            # 5. HYPOTHESIS VALIDATION
            has_supported = False
            for idx, h in enumerate(hypotheses_res.hypotheses):
                # Validate evidence IDs
                valid_assessments = []
                for assessment in h.assessments:
                    if assessment.evidence_id in self.evidence_cache:
                        valid_assessments.append(assessment)
                
                # If no valid evidence, mark as insufficient_evidence
                if not valid_assessments and h.status in ["supported", "plausible"]:
                    h.status = "insufficient_evidence"
                    h.evidence_strength = "insufficient"
                    
                if h.status in ["supported", "plausible"]:
                    has_supported = True

                db_hypo = InvestigationHypothesis(
                    investigation_id=self.investigation_id,
                    title=h.title,
                    description=h.description,
                    status=h.status,
                    rank=idx + 1,
                    evidence_strength=h.evidence_strength
                )
                self.db.add(db_hypo)
                self.db.commit()

                for assessment in valid_assessments:
                    ev = self.evidence_cache[assessment.evidence_id]
                    new_ev = InvestigationEvidence(
                        investigation_id=self.investigation_id,
                        hypothesis_id=db_hypo.id,
                        evidence_type=ev.evidence_type,
                        source_type=ev.source_type,
                        title=ev.title,
                        value_json=ev.value_json,
                        relationship_type=assessment.relationship,
                        explanation=assessment.explanation
                    )
                    self.db.add(new_ev)
            self.db.commit()
            
            self._add_event("hypothesis_evaluated", "Hypotheses Evaluated", "Linked evidence to hypotheses and validated.")

            # 6. GENERATE CONCLUSION
            conc_prompt = f"Based on the hypotheses generated, provide a final conclusion.\nIncident: {self.incident.title}\n"
            system_conc = "Output a final conclusion."
            conclusion: InvestigationConclusion = self.provider.generate_structured(conc_prompt, system_conc, InvestigationConclusion)
            
            self.inv.summary = conclusion.summary
            
            primary_hypo = self.db.query(InvestigationHypothesis).filter(
                InvestigationHypothesis.investigation_id == self.investigation_id,
                InvestigationHypothesis.status.in_(["supported", "plausible"])
            ).order_by(InvestigationHypothesis.rank).first()
            
            if primary_hypo:
                self.inv.primary_hypothesis_id = primary_hypo.id
                
            self._add_event("conclusion_generated", "Conclusion Generated", "Investigation concluded.", metadata=conclusion.model_dump())

            if has_supported:
                self.inv.status = "completed"
                self._add_event("investigation_completed", "Investigation Completed", "Completed with sufficient evidence.")
                
                from app.services.reliability_service import reliability_service
                rc_event = reliability_service.emit_event(
                    db=self.db,
                    model_id=self.incident.model_id,
                    model_version_id=self.incident.model_version_id,
                    event_type="ROOT_CAUSE_IDENTIFIED",
                    source_type="investigation",
                    source_id=self.investigation_id,
                    title="Root Cause Identified",
                    summary=self.inv.summary or "Root cause found by AI investigation.",
                    status="success"
                )
                inv_event_start = reliability_service.find_event_by_source(self.db, "investigation", self.investigation_id, "INVESTIGATION_STARTED")
                if inv_event_start:
                    reliability_service.link_events(self.db, inv_event_start.id, rc_event.id, "RESULTED_IN")
            else:
                self.inv.status = "completed_with_insufficient_evidence"
                self._add_event("investigation_completed", "Investigation Completed (Insufficient Evidence)", "Completed but lacked evidence to support hypotheses.")

            self.inv.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            
        except Exception as e:
            logger.exception("Investigation failed")
            self.inv.status = "failed"
            self.inv.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self._add_event("investigation_failed", "Investigation Failed", str(e), status="error")
