/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Loader2, Search, BrainCircuit } from 'lucide-react';

export function IncidentMemoryPage() {
  const [memories, setMemories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/memories')
      .then(res => res.json())
      .then(data => {
        setMemories(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = memories.filter(m => 
    m.title?.toLowerCase().includes(search.toLowerCase()) ||
    m.root_cause?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold tracking-tight mb-2 flex items-center">
            <BrainCircuit className="w-8 h-8 mr-3 text-amber-500" />
            Incident Memory
          </h1>
          <p className="text-muted-foreground text-lg">
            Engineering knowledge base built from successfully resolved incidents.
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search memories, root causes..."
            className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-amber-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
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
            <Card key={memory.id} className="hover:border-amber-500/30 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="warning" className="border-amber-500/50 text-amber-500 bg-amber-500/10">
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
                    <a href={`/incidents/${memory.incident_id}`}>View Source Incident</a>
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
