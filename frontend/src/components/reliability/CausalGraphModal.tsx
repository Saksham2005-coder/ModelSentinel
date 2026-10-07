import React, { useEffect, useState } from 'react';
import { ReliabilityApi, CausalGraph } from '../../services/api/reliability';

interface Props {
  modelId: string;
  eventId: string;
  onClose: () => void;
}

const CausalGraphModal: React.FC<Props> = ({ modelId, eventId, onClose }) => {
  const [graph, setGraph] = useState<CausalGraph | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const data = await ReliabilityApi.getIncidentGraph(modelId, eventId);
        setGraph(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, [modelId, eventId]);

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-6 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b border-gray-800 bg-gray-900/50">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>🕸️</span> Causal Incident Graph
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white transition bg-gray-800 hover:bg-gray-700 p-2 rounded-lg"
          >
            ✕
          </button>
        </div>
        
        <div className="flex-1 p-6 overflow-auto bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CjxyZWN0IHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgZmlsbD0ibm9uZSIvPgo8Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMDUpIi8+Cjwvc3ZnPg==')]">
          {loading ? (
            <div className="flex justify-center items-center h-full text-gray-400">Loading causal graph...</div>
          ) : graph && graph.nodes.length > 0 ? (
            <SimpleGraphRenderer graph={graph} focusId={eventId} />
          ) : (
            <div className="flex justify-center items-center h-full text-gray-500">
              No causal connections found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// A very simple hierarchical renderer for the causal graph
export const SimpleGraphRenderer: React.FC<{ graph: CausalGraph; focusId?: string }> = ({ graph, focusId }) => {
  // Sort nodes chronologically
  const sortedNodes = [...graph.nodes].sort((a, b) => new Date(a.occurred_at).getTime() - new Date(b.occurred_at).getTime());
  
  return (
    <div className="flex flex-col items-center gap-8 py-8 min-h-full">
      {sortedNodes.map((node) => {
        const isFocused = node.id === focusId;
        const incomingEdges = graph.edges.filter(e => e.to_id === node.id);
        
        return (
          <div key={node.id} className="flex flex-col items-center">
            {incomingEdges.map(edge => (
              <div key={edge.id} className="flex flex-col items-center mb-2">
                <div className="text-xs text-gray-500 bg-gray-900 px-2 py-0.5 rounded-full mb-1 border border-gray-800">
                  {edge.type}
                </div>
                <div className="w-px h-8 bg-gradient-to-b from-gray-600 to-gray-400"></div>
                <div className="w-2 h-2 bg-gray-400 rotate-45 transform translate-y-[-4px]"></div>
              </div>
            ))}
            
            <div className={`
              w-96 p-4 rounded-xl border-2 shadow-lg transition-all
              ${isFocused ? 'bg-indigo-900/40 border-indigo-500 shadow-indigo-500/20' : 'bg-gray-800 border-gray-700 hover:border-gray-500'}
            `}>
              <div className="flex justify-between items-start mb-2">
                <div className="font-semibold text-white">{node.title}</div>
                <div className="text-xs bg-black/40 px-2 py-1 rounded text-gray-300">{node.event_type}</div>
              </div>
              {node.summary && <div className="text-sm text-gray-400 mt-2">{node.summary}</div>}
              <div className="mt-3 text-xs text-gray-500 font-mono flex justify-between">
                <span>{node.source_type}</span>
                <span>{new Date(node.occurred_at).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CausalGraphModal;
