import React, { useState, useEffect } from 'react';
import { RefreshCw, Code, GitBranch, Github, FileArchive, Search, Folder, File } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';



interface SearchResult {
  file_path: string;
  symbol_name: string;
  symbol_type: string;
  start_line: number;
}

interface Repository {
  id: string;
  name: string;
  status: string;
  source_type: string;
  current_commit?: string;
  indexed_at?: string;
}

export const RepositoryPage: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeRepo, setActiveRepo] = useState<Repository | null>(null);
  
  // Connect Git state
  const [gitUrl, setGitUrl] = useState('');
  const [repoName, setRepoName] = useState('');

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // File Viewer state
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');

  const fetchRepositories = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/repositories/');
      if (res.ok) {
        const data = await res.json();
        setRepositories(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRepositories();
    const interval = setInterval(fetchRepositories, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleConnectGit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!gitUrl || !repoName) return;
    
    const formData = new FormData();
    formData.append('name', repoName);
    formData.append('source_type', 'public_git');
    formData.append('url', gitUrl);

    try {
      await fetch('http://localhost:8000/api/v1/repositories/', {
        method: 'POST',
        body: formData
      });
      setGitUrl('');
      setRepoName('');
      fetchRepositories();
    } catch (e) {
      console.error(e);
    }
  };

  const handleUploadZip = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('name', file.name.replace('.zip', ''));
    formData.append('source_type', 'zip');
    formData.append('file', file);

    try {
      await fetch('http://localhost:8000/api/v1/repositories/', {
        method: 'POST',
        body: formData
      });
      fetchRepositories();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async () => {
    if (!activeRepo || !searchQuery) return;
    setSearchLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/repositories/${activeRepo.id}/search?q=${encodeURIComponent(searchQuery)}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleOpenFile = async (filePath: string) => {
    if (!activeRepo) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/repositories/${activeRepo.id}/files?file_path=${encodeURIComponent(filePath)}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedFile(filePath);
        setFileContent(data.content);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-100">Repository Intelligence</h2>
          <p className="text-slate-400 mt-2">Connect code repositories to link ML incidents to actual code changes.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchRepositories}>
            <RefreshCw className="mr-2 h-4 w-4" /> Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-slate-200 text-lg">Connected Repositories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {repositories.length === 0 && !loading ? (
                  <p className="text-slate-400 text-sm">No repositories connected.</p>
                ) : (
                  repositories.map(repo => (
                    <div 
                      key={repo.id} 
                      className={`p-3 rounded border cursor-pointer transition-colors ${activeRepo?.id === repo.id ? 'bg-indigo-900/50 border-indigo-500' : 'bg-slate-800 border-slate-700 hover:border-slate-600'}`}
                      onClick={() => setActiveRepo(repo)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2 text-slate-200 font-medium">
                          {repo.source_type === 'public_git' ? <Github className="h-4 w-4" /> : <FileArchive className="h-4 w-4" />}
                          {repo.name}
                        </div>
                        <Badge variant={repo.status === 'ready' ? 'success' : repo.status === 'failed' ? 'danger' : 'default'}>
                          {repo.status}
                        </Badge>
                      </div>
                      <div className="flex gap-4 text-xs text-slate-400">
                        {repo.current_commit && (
                          <div className="flex items-center gap-1">
                            <GitBranch className="h-3 w-3" />
                            {repo.current_commit.substring(0, 7)}
                          </div>
                        )}
                        {repo.indexed_at && (
                          <div>Indexed: {new Date(repo.indexed_at).toLocaleDateString()}</div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-slate-200 text-lg">Connect New Repository</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <form onSubmit={handleConnectGit} className="space-y-4">
                <div>
                  <label className="text-sm text-slate-400 mb-1 block">Repository Name</label>
                  <Input 
                    placeholder="e.g. modelsentinel-core" 
                    value={repoName} 
                    onChange={e => setRepoName(e.target.value)}
                    className="bg-slate-800 border-slate-700 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-sm text-slate-400 mb-1 block">Public Git URL</label>
                  <Input 
                    placeholder="https://github.com/user/repo.git" 
                    value={gitUrl} 
                    onChange={e => setGitUrl(e.target.value)}
                    className="bg-slate-800 border-slate-700 text-slate-200"
                  />
                </div>
                <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" disabled={!gitUrl || !repoName}>
                  <Github className="mr-2 h-4 w-4" /> Connect via Git
                </Button>
              </form>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-slate-800" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-slate-900 px-2 text-slate-500">Or</span>
                </div>
              </div>

              <div>
                <Button variant="outline" className="w-full relative" asChild>
                  <label className="cursor-pointer">
                    <FileArchive className="mr-2 h-4 w-4" /> Upload ZIP Archive
                    <input type="file" accept=".zip" className="hidden" onChange={handleUploadZip} />
                  </label>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-6">
          {!activeRepo ? (
            <div className="h-[600px] flex items-center justify-center border border-slate-800 border-dashed rounded-lg bg-slate-900/50">
              <div className="text-center text-slate-500">
                <Code className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select a repository to view code and intelligence</p>
              </div>
            </div>
          ) : (
            <>
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader className="pb-4 border-b border-slate-800">
                  <div className="flex gap-4">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                      <Input 
                        placeholder="Search for functions, features, or files..." 
                        className="pl-9 bg-slate-800 border-slate-700 text-slate-200"
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSearch()}
                      />
                    </div>
                    <Button onClick={handleSearch} disabled={searchLoading}>
                      Search
                    </Button>
                  </div>
                </CardHeader>
                {searchResults.length > 0 && (
                  <CardContent className="p-0 border-b border-slate-800">
                    <div className="max-h-48 overflow-y-auto p-4 space-y-2">
                      {searchResults.map((res, i) => (
                        <div 
                          key={i} 
                          className="flex justify-between items-center p-2 rounded bg-slate-800/50 hover:bg-slate-800 cursor-pointer text-sm"
                          onClick={() => handleOpenFile(res.file_path)}
                        >
                          <div className="flex items-center gap-2">
                            <Code className="h-4 w-4 text-indigo-400" />
                            <span className="text-slate-200 font-mono">{res.symbol_name}</span>
                            <span className="text-slate-500 text-xs">({res.symbol_type})</span>
                          </div>
                          <div className="text-slate-400 font-mono text-xs">
                            {res.file_path}:{res.start_line}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                )}
                
                <CardContent className="p-0">
                  <div className="flex h-[500px]">
                    {/* Left: Search Results or empty Tree (Placeholder) */}
                    <div className="w-1/3 border-r border-slate-800 bg-slate-900/50 p-4">
                       <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Workspace</h3>
                       <div className="text-sm text-slate-400 flex items-center gap-2 p-1">
                          <Folder className="h-4 w-4 text-indigo-400" />
                          {activeRepo.name}
                       </div>
                       {selectedFile && (
                          <div className="text-sm text-slate-300 flex items-center gap-2 p-1 ml-4 bg-slate-800 rounded">
                            <File className="h-4 w-4" />
                            {selectedFile.split('/').pop()}
                          </div>
                       )}
                       {!selectedFile && (
                         <div className="mt-8 text-center text-xs text-slate-600">
                           Search to open files
                         </div>
                       )}
                    </div>
                    
                    {/* Right: Code Viewer */}
                    <div className="w-2/3 bg-[#0d1117] overflow-auto">
                      {selectedFile ? (
                        <div className="p-4">
                          <div className="flex justify-between items-center mb-4 border-b border-slate-800 pb-2">
                            <div className="text-sm font-mono text-slate-400">{selectedFile}</div>
                          </div>
                          <pre className="text-xs font-mono text-slate-300">
                            <code>{fileContent}</code>
                          </pre>
                        </div>
                      ) : (
                        <div className="h-full flex items-center justify-center text-slate-600 text-sm">
                          No file selected
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
