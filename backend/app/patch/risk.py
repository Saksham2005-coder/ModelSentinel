from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

PROTECTED_PATHS = [
    ".env",
    "docker-compose.yml",
    "Dockerfile",
    ".git",
    "credentials",
    "secrets",
]

class RiskAnalyzer:
    @staticmethod
    def analyze(file_changes: List[Any], test_changes: List[str]) -> Dict[str, Any]:
        risk_score = 0
        reasons = []

        files_changed = len(file_changes)
        source_files = 0
        test_files = len(test_changes)
        config_files = 0
        total_additions = 0
        total_deletions = 0
        touches_protected = False

        for change in file_changes:
            path = change.file_path
            
            # Check protected
            if any(p in path for p in PROTECTED_PATHS):
                touches_protected = True
                reasons.append(f"Modifies protected path: {path}")

            if path.endswith('.py') and not path.startswith('tests/'):
                source_files += 1
            elif path.endswith(('.json', '.yml', '.yaml', '.ini', '.cfg')):
                config_files += 1
                reasons.append(f"Modifies configuration file: {path}")

            if change.additions:
                total_additions += change.additions
            if change.deletions:
                total_deletions += change.deletions

            if change.change_type == 'delete':
                reasons.append(f"Deletes file: {path}")

        # Basic scoring
        if files_changed > 5:
            reasons.append(f"High number of changed files ({files_changed})")
        if (total_additions + total_deletions) > 100:
            reasons.append(f"Large change size ({total_additions + total_deletions} lines)")

        # Determine level
        if touches_protected:
            level = "Restricted"
        elif files_changed > 5 or (total_additions + total_deletions) > 200 or config_files > 0:
            level = "High"
        elif source_files > 2 or (total_additions + total_deletions) > 50:
            level = "Moderate"
        else:
            level = "Low"

        return {
            "level": level,
            "reasons": reasons,
            "stats": {
                "files_changed": files_changed,
                "source_files": source_files,
                "test_files": test_files,
                "config_files": config_files,
                "additions": total_additions,
                "deletions": total_deletions
            }
        }
