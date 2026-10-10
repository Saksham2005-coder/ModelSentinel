import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { ReliabilityApi, ReliabilityEvent } from '../../services/api/reliability';
import CausalGraphModal from '../../components/reliability/CausalGraphModal';

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const seconds = Math.floor((now - then) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const ReliabilityTimelinePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [events, setEvents] = useState<ReliabilityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const loadTimeline = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await ReliabilityApi.getTimeline(id);
      setEvents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadTimeline();
    }
  }, [id, loadTimeline]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'TELEMETRY_RECEIVED': return '📥';
      case 'MONITORING_COMPLETED': return '⏱️';
      case 'DEGRADATION_DETECTED': return '📉';
      case 'INCIDENT_CREATED': return '🚨';
      case 'INVESTIGATION_STARTED': return '🔍';
      case 'ROOT_CAUSE_IDENTIFIED': return '💡';
      case 'PATCH_PROPOSED': return '📝';
      case 'VALIDATION_COMPLETED': return '🧪';
      case 'REGRESSION_LEARNED': return '🧠';
      case 'PULL_REQUEST_CREATED': return '🔗';
      case 'DEPLOYMENT_COMPLETED': return '🚀';
      case 'VERIFICATION_COMPLETED': return '✅';
      default: return '⚪';
    }
  };

  const getEventColor = (type: string) => {
    if (['DEGRADATION_DETECTED', 'INCIDENT_CREATED'].includes(type)) return 'bg-red-500/10 border-red-500/20 text-red-400';
    if (['ROOT_CAUSE_IDENTIFIED', 'PATCH_PROPOSED', 'VALIDATION_COMPLETED', 'DEPLOYMENT_COMPLETED', 'VERIFICATION_COMPLETED'].includes(type)) return 'bg-green-500/10 border-green-500/20 text-green-400';
    if (['INVESTIGATION_STARTED', 'REGRESSION_LEARNED'].includes(type)) return 'bg-blue-500/10 border-blue-500/20 text-blue-400';
    return 'bg-background-secondary border-border-strong text-text-primary';
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary flex items-center">
          <span className="mr-2">⏳</span> Reliability Timeline
        </h1>
        <button
          onClick={loadTimeline}
          className="px-4 py-2 bg-background-secondary text-text-primary rounded hover:bg-background-elevated transition"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64 text-text-secondary">Loading timeline...</div>
      ) : events.length === 0 ? (
        <div className="bg-background-secondary border border-border-strong rounded-lg p-8 text-center text-text-secondary">
          No reliability events found for this model.
        </div>
      ) : (
        <div className="relative border-l-2 border-border-strong ml-4 pl-8 space-y-8">
          {events.map((event) => (
            <div key={event.id} className="relative">
              {/* Timeline marker */}
              <div className="absolute -left-11 top-1 w-6 h-6 rounded-full bg-background-primary border-2 border-gray-600 flex items-center justify-center text-xs shadow-lg shadow-black/50">
                {getEventIcon(event.event_type)}
              </div>
              
              <div className={`border rounded-lg p-5 ${getEventColor(event.event_type)} backdrop-blur-sm transition-all hover:border-gray-500`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="text-lg font-semibold">{event.title}</h3>
                    <div className="text-sm opacity-70 mt-1">{event.event_type}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{timeAgo(event.occurred_at)}</div>
                    <div className="text-xs opacity-50 mt-1">{new Date(event.occurred_at).toLocaleString()}</div>
                  </div>
                </div>
                
                {event.summary && (
                  <p className="mt-3 opacity-90">{event.summary}</p>
                )}
                
                {event.event_type === 'ROOT_CAUSE_IDENTIFIED' && event.metadata_json && (
                  <div className="mt-4 bg-black/20 p-4 rounded-lg border border-white/10 text-sm">
                    <div className="grid grid-cols-2 gap-4">
                      {!!(event.metadata_json as Record<string, unknown>).category && (
                        <div>
                          <span className="opacity-60 text-xs uppercase tracking-wider block mb-1">Category</span>
                          <span className="font-medium text-brand-hover">{String((event.metadata_json as Record<string, unknown>).category)}</span>
                        </div>
                      )}
                      {!!(event.metadata_json as Record<string, unknown>).explanation && (
                        <div className="col-span-2">
                          <span className="opacity-60 text-xs uppercase tracking-wider block mb-1">Explanation</span>
                          <span>{String((event.metadata_json as Record<string, unknown>).explanation)}</span>
                        </div>
                      )}
                      {!!(event.metadata_json as Record<string, unknown>).evidence && (
                        <div className="col-span-2">
                          <span className="opacity-60 text-xs uppercase tracking-wider block mb-1">Evidence</span>
                          <pre className="bg-black/40 p-2 rounded text-xs overflow-x-auto whitespace-pre-wrap">
                            {typeof (event.metadata_json as Record<string, unknown>).evidence === 'string' 
                              ? (event.metadata_json as Record<string, unknown>).evidence as React.ReactNode
                              : JSON.stringify((event.metadata_json as Record<string, unknown>).evidence, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => setSelectedEventId(event.id)}
                    className="px-3 py-1.5 bg-black/30 hover:bg-black/50 border border-white/10 rounded text-sm transition"
                  >
                    View Causal Graph
                  </button>
                  <div className="px-3 py-1.5 bg-black/20 rounded text-sm font-mono opacity-70">
                    {event.source_type}: {event.source_id.slice(0, 8)}...
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedEventId && id && (
        <CausalGraphModal
          modelId={id}
          eventId={selectedEventId}
          onClose={() => setSelectedEventId(null)}
        />
      )}
    </div>
  );
};

export default ReliabilityTimelinePage;
