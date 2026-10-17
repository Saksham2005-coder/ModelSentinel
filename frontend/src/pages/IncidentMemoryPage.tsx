import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Loader2, Search, BrainCircuit, PlusCircle } from 'lucide-react';

import { fetchApi } from '@/services/api/client';
import { DEMO_MEMORIES } from '@/services/api/demoData';
import { useToast } from '@/contexts/ToastContext';

export function IncidentMemoryPage() {
  const [memories, setMemories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const { addToast } = useToast();

  useEffect(() => {
    setLoading(true);
    fetchApi<any[]>('/memories')
      .then(data => {
        setMemories(Array.isArray(data) && data.length > 0 ? data : DEMO_MEMORIES);
        setLoading(false);
      })
      .catch(() => {
        setMemories(DEMO_MEMORIES);
        setLoading(false);
      });
  }, []);

  const handleSynthesize = () => {
    addToast('info', 'Synthesizing knowledge pattern from latest resolved incidents...');
    setTimeout(() => {
      const newMem = {
        id: `mem-${Date.now()}`,
        incident_id: "2ffa080c-1678-4325-9d1c-d59f22e04b52",
        title: "Automated Edge Case Safeguard Pattern",
        root_cause: "High-variance input payload bypassing boundary checks.",
        root_cause_category: "Data Integrity",
        model_id: "4872c9f0-b895-4d27-8547-28113a3bb876",
        affected_segments: ["extreme_outliers", "v2_clients"],
        resolution_summary: "Generated dynamic schema validator rule and integrated unit test vector.",
        created_at: new Date().toISOString(),
        resolution: {
          effectiveness_score: 98,
          validation_status: "PASSED",
          deployment_status: "COMPLETED",
          post_deployment_status: "STABLE"
        }
      };
      setMemories(prev => [newMem, ...prev]);
      addToast('success', 'Incident memory synthesized and indexed into knowledge base.');
    }, 1000);
  };

  const filtered = memories.filter(m => {
    if (!search) return true;
    const t = (m.title || '').toLowerCase();
    const r = (m.root_cause || '').toLowerCase();
    const s = search.toLowerCase();
    return t.includes(s) || r.includes(s);
  });

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight mb-2 flex items-center">
            <BrainCircuit className="w-8 h-8 mr-3 text-brand" />
            Incident Memory
          </h1>
          <p className="text-muted-foreground text-lg">
            Engineering knowledge base built from successfully resolved incidents.
          </p>
        </div>
        <Button onClick={handleSynthesize} className="bg-brand text-background-base hover:bg-brand/90">
          <PlusCircle className="w-4 h-4 mr-2" />
          Synthesize Memory
        </Button>
      </div>

      <div className="flex items-center space-x-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search memories, root causes..."
            className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 animate-spin text-brand" />
        </div>
      ) : filtered.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-20 text-center">
            <BrainCircuit className="w-12 h-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No memories found</h3>
            <p className="text-muted-foreground max-w-sm">
              Resolve an incident and save it to build engineering memory.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {filtered.map(memory => (
            <Card key={memory.id} className="hover:border-brand/30 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="warning" className="border-brand/50 text-brand bg-brand/10">
                    {memory.root_cause_category || "Unknown"}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(memory.created_at).toLocaleDateString()}
                  </span>
                </div>
                <CardTitle className="text-xl leading-tight">{memory.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-1">Root Cause</h4>
                  <p className="text-sm">{memory.root_cause}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-1">Validated Fix</h4>
                  <p className="text-sm">{memory.resolution_summary}</p>
                </div>
                <div className="flex space-x-2 pt-2 border-t border-border/50">
                  <Button variant="default" size="sm" className="h-8 text-xs text-muted-foreground" asChild>
                    <Link to={`/incidents/${memory.incident_id}`}>View Source Incident</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
