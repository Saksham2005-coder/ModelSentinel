import { useState, useEffect, useRef, useCallback } from 'react';
import { Search as SearchIcon, FileText, AlertTriangle, Shield, GitPullRequest, Activity } from 'lucide-react';
import { Input } from './Input';
import { useNavigate } from 'react-router-dom';
import { fetchApi } from '@/services/api/client';

interface SearchResult {
  id: string;
  type: 'model' | 'incident' | 'navigation' | 'pr' | 'slo';
  title: string;
  subtitle?: string;
  url: string;
}

const NAVIGATION_RESULTS: SearchResult[] = [
  { id: 'nav-1', type: 'navigation', title: 'Dashboard', url: '/dashboard' },
  { id: 'nav-2', type: 'navigation', title: 'Models', url: '/models' },
  { id: 'nav-3', type: 'navigation', title: 'Incidents', url: '/incidents' },
  { id: 'nav-4', type: 'navigation', title: 'Repositories', url: '/repository' },
  { id: 'nav-5', type: 'navigation', title: 'Workflows', url: '/workflows' },
  { id: 'nav-6', type: 'navigation', title: 'SLOs', url: '/slo' },
  { id: 'nav-7', type: 'navigation', title: 'Alerts', url: '/alerts' },
  { id: 'nav-8', type: 'navigation', title: 'Pull Requests', url: '/pull-requests' },
  { id: 'nav-9', type: 'navigation', title: 'Deployments', url: '/deployments' },
  { id: 'nav-10', type: 'navigation', title: 'Engineering Intelligence', url: '/engineering-intelligence' },
  { id: 'nav-11', type: 'navigation', title: 'Incident Memory', url: '/incident-memory' },
  { id: 'nav-12', type: 'navigation', title: 'Regression', url: '/regression-tests' },
];

export function GlobalSearch() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Ctrl+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelect = useCallback((result: SearchResult) => {
    setIsOpen(false);
    setQuery('');
    navigate(result.url);
  }, [navigate]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') {
        setIsOpen(false);
        inputRef.current?.blur();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter' && results[selectedIndex]) {
        e.preventDefault();
        handleSelect(results[selectedIndex]);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, handleSelect]);

  // Debounced Search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const localResults = NAVIGATION_RESULTS.filter(n => 
          n.title.toLowerCase().includes(query.toLowerCase())
        );

        // Fetch remote data (gracefully degrade if endpoints don't support explicit search)
        const [modelsRes, incidentsRes, reposRes, prsRes, depsRes, wfsRes, slosRes, alertsRes] = await Promise.all([
          fetchApi<Record<string, unknown>[]>('/models/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/incidents/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/repositories/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/pull-requests/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/deployments/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/workflows/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/slo/').then(data => ({ data })).catch(() => ({ data: [] })),
          fetchApi<Record<string, unknown>[]>('/alerts/').then(data => ({ data })).catch(() => ({ data: [] }))
        ]);

        const remoteModels: SearchResult[] = (modelsRes.data || [])
          .filter((m: Record<string, unknown>) => String(m.name || '').toLowerCase().includes(query.toLowerCase()))
          .slice(0, 3)
          .map((m: Record<string, unknown>) => ({
            id: m.id as string, type: 'model' as const, title: m.name as string, subtitle: m.version as string, url: `/models/${m.id}`
          }));

        const remoteIncidents: SearchResult[] = (incidentsRes.data || [])
          .filter((i: Record<string, unknown>) => String(i.title || '').toLowerCase().includes(query.toLowerCase()))
          .slice(0, 3)
          .map((i: Record<string, unknown>) => ({
            id: i.id as string, type: 'incident' as const, title: i.title as string, subtitle: i.severity as string, url: `/incidents/${i.id}`
          }));

        const extractId = (obj: Record<string, unknown>) => obj.id || obj.name || 'unknown';

        const mapRemote = (res: { data?: Record<string, unknown>[] }, type: SearchResult['type'], urlPrefix: string, titleField: string, subtitleField?: string) => {
          return (res.data || [])
            .filter((x: Record<string, unknown>) => String(x[titleField] || x.id || '').toLowerCase().includes(query.toLowerCase()))
            .slice(0, 2)
            .map((x: Record<string, unknown>) => ({
              id: extractId(x), type: type, title: String(x[titleField] || x.id || ''), 
              subtitle: subtitleField ? String(x[subtitleField] || '') : undefined, 
              url: `${urlPrefix}${extractId(x)}`
            }));
        };

        const remoteRepos = mapRemote(reposRes, 'navigation', '/repository', 'name');
        const remotePRs = mapRemote(prsRes, 'pr', '/pull-requests/', 'title', 'status');
        const remoteDeps = mapRemote(depsRes, 'navigation', '/deployment-gates/', 'id', 'environment');
        const remoteWfs = mapRemote(wfsRes, 'navigation', '/workflows/', 'name', 'status');
        const remoteSlos = mapRemote(slosRes, 'slo', '/slo', 'name');
        const remoteAlerts = mapRemote(alertsRes, 'incident', '/alerts', 'summary', 'severity');

        setResults([...localResults, ...remoteModels, ...remoteIncidents, ...remoteRepos, ...remotePRs, ...remoteDeps, ...remoteWfs, ...remoteSlos, ...remoteAlerts]);
        setSelectedIndex(0);
      } catch (err) {
        console.error("Search failed", err);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getIcon = (type: string) => {
    switch(type) {
      case 'model': return <Activity className="w-4 h-4 text-brand" />;
      case 'incident': return <AlertTriangle className="w-4 h-4 text-status-danger" />;
      case 'navigation': return <FileText className="w-4 h-4 text-text-secondary" />;
      case 'pr': return <GitPullRequest className="w-4 h-4 text-status-info" />;
      default: return <Shield className="w-4 h-4 text-text-secondary" />;
    }
  };

  return (
    <div className="relative w-full max-w-lg" ref={containerRef}>
      <div className="relative">
        <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-text-muted" />
        <Input 
          ref={inputRef}
          type="search" 
          placeholder="Search models, incidents, or PRs... (Ctrl+K)" 
          className="pl-9 bg-surface border-border-strong w-full transition-shadow focus:ring-2 focus:ring-brand/20"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
        />
        {isLoading && <div className="absolute right-3 top-2.5 h-4 w-4 rounded-full border-2 border-brand border-t-transparent animate-spin" />}
      </div>

      {isOpen && query.trim() && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-background-elevated border border-border rounded-lg shadow-xl overflow-hidden z-50 max-h-96 overflow-y-auto">
          {results.length > 0 ? (
            <div className="py-2">
              {results.map((result, idx) => (
                <button
                  key={`${result.type}-${result.id}`}
                  className={`w-full text-left px-4 py-3 flex items-start gap-3 transition-colors ${
                    idx === selectedIndex ? 'bg-surface-hover border-l-2 border-brand' : 'hover:bg-surface border-l-2 border-transparent'
                  }`}
                  onClick={() => handleSelect(result)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                >
                  <div className="mt-0.5">{getIcon(result.type)}</div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-text-primary">{result.title}</span>
                    {result.subtitle && <span className="text-xs text-text-muted">{result.subtitle}</span>}
                  </div>
                  <div className="ml-auto text-[10px] uppercase tracking-wider text-text-muted font-bold mt-1">
                    {result.type}
                  </div>
                </button>
              ))}
            </div>
          ) : !isLoading ? (
            <div className="p-4 text-center text-sm text-text-muted">
              No matching models, incidents, repositories, or pages.
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
