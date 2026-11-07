import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, 
  Search, 
  History, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  PanelLeftClose, 
  PanelLeft,
  Trash2
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { getHealth, deleteRun } from '../services/api';

export const Sidebar: React.FC = () => {
  const { 
    runs, 
    currentRun, 
    fetchRun, 
    fetchRuns,
    resetToHome,
    addToast 
  } = useAppStore();

  const [isOpen, setIsOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [healthStatus, setHealthStatus] = useState<{ status: string; demo_mode?: boolean } | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealthStatus)
      .catch(() => setHealthStatus({ status: 'unreachable' }));
  }, []);

  const filteredRuns = runs.filter(r => 
    r.query.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatTimestamp = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await deleteRun(id);
      addToast('Deleted research run', 'info');
      fetchRuns();
      if (currentRun && (currentRun.id === id || currentRun.run_id === id)) {
        resetToHome();
      }
    } catch {
      addToast('Failed to delete run', 'error');
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/40 z-30 lg:hidden backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Floating Toggle when Closed */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed top-20 left-4 z-40 p-2 rounded-xl bg-card border border-border shadow-md hover:bg-muted text-foreground transition-all"
          title="Open history sidebar"
        >
          <PanelLeft className="w-5 h-5 text-muted-foreground" />
        </button>
      )}

      {/* Sidebar Container */}
      <aside 
        className={`fixed lg:static top-0 left-0 h-full z-40 bg-card/95 backdrop-blur-md border-r border-border transition-all duration-300 flex flex-col ${
          isOpen ? 'w-80 translate-x-0' : '-translate-x-full lg:w-0 lg:translate-x-0 overflow-hidden border-none'
        }`}
      >
        {/* Top Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          <div className="flex items-center space-x-2 text-foreground font-semibold text-sm">
            <History className="w-4 h-4 text-brand-500" />
            <span>Research History</span>
          </div>
          <button 
            onClick={() => setIsOpen(false)}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted"
            title="Collapse sidebar"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>

        {/* Action Button: New Research */}
        <div className="p-3 border-b border-border">
          <button
            onClick={() => {
              resetToHome();
              if (window.innerWidth < 1024) setIsOpen(false);
            }}
            className="w-full py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold flex items-center justify-center space-x-2 shadow-sm transition-all shadow-brand-500/20 active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Research</span>
          </button>
        </div>

        {/* Search Filter */}
        <div className="px-3 py-2 border-b border-border">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter past runs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-background border border-border text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>

        {/* Runs List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin">
          {filteredRuns.length === 0 ? (
            <div className="py-12 text-center text-xs text-muted-foreground">
              {searchTerm ? 'No matching research runs' : 'No research runs yet'}
            </div>
          ) : (
            filteredRuns.map((r) => {
              const currentId = currentRun ? (currentRun.run_id || currentRun.id) : null;
              const isSelected = currentId === r.id;
              const isRunning = r.status !== 'completed' && r.status !== 'failed' && r.status !== 'cancelled';

              return (
                <div
                  key={r.id}
                  onClick={() => {
                    fetchRun(r.id);
                    if (window.innerWidth < 1024) setIsOpen(false);
                  }}
                  className={`group relative p-2.5 rounded-xl cursor-pointer text-left transition-all ${
                    isSelected 
                      ? 'bg-brand-500/10 border border-brand-500/30 text-brand-900 dark:text-brand-100 shadow-sm' 
                      : 'hover:bg-muted/60 text-foreground border border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs font-medium line-clamp-2 leading-relaxed flex-1">
                      {r.query}
                    </p>
                    <div className="mt-0.5 shrink-0 flex items-center space-x-1">
                      {r.status === 'completed' && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                      )}
                      {isRunning && (
                        <Clock className="w-3.5 h-3.5 text-brand-500 animate-spin" />
                      )}
                      {r.status === 'failed' && (
                        <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                      )}
                      <button
                        onClick={(e) => handleDelete(e, r.id)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 text-muted-foreground transition-opacity"
                        title="Delete run"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  <div className="mt-2 flex items-center justify-between text-[10px] text-muted-foreground">
                    <span>{formatTimestamp(r.created_at)}</span>
                    <span className="capitalize px-1.5 py-0.5 rounded bg-muted/80 text-[9px] font-mono">
                      {r.status}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer: Health & Demo Badge */}
        <div className="p-3 border-t border-border bg-muted/20 text-xs">
          <div className="flex items-center justify-between text-[11px] text-muted-foreground">
            <div className="flex items-center space-x-1.5">
              <span className={`w-2 h-2 rounded-full ${
                healthStatus?.status === 'ok' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
              }`} />
              <span className="font-medium">
                {healthStatus?.status === 'ok' ? 'API Connected' : 'Connecting...'}
              </span>
            </div>
            {healthStatus?.demo_mode && (
              <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 font-semibold text-[9px] border border-amber-500/20">
                DEMO MODE
              </span>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};
