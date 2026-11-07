import React, { useEffect, useState } from 'react';
import { useAppStore } from './store/useAppStore';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { HomeView } from './components/HomeView';
import { Timeline } from './components/Timeline';
import { ReportView } from './components/ReportView';
import { ComparisonTable } from './components/ComparisonTable';
import { ScorecardView } from './components/ScorecardView';
import { SourcesView } from './components/SourcesView';
import { AskChat } from './components/AskChat';
import { ToastContainer } from './components/ToastContainer';
import { 
  FileText, 
  Table, 
  BarChart3, 
  Database, 
  MessageSquare, 
  AlertCircle, 
  ArrowLeft, 
  Calendar, 
  Layers, 
  ChevronDown, 
  ChevronUp 
} from 'lucide-react';

export const App: React.FC = () => {
  const { 
    currentRun, 
    events, 
    activeTab, 
    setActiveTab, 
    fetchRuns, 
    resetToHome,
    theme 
  } = useAppStore();

  const [showTimeline, setShowTimeline] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    fetchRuns();
  }, [theme, fetchRuns]);

  const isRunning = currentRun 
    ? currentRun.status !== 'completed' && currentRun.status !== 'failed' && currentRun.status !== 'cancelled'
    : false;

  useEffect(() => {
    if (isRunning) {
      setShowTimeline(true);
    }
  }, [isRunning]);

  const sourcesCount = currentRun?.sources?.length || currentRun?.report?.sources?.length || 0;
  const findingsCount = currentRun?.findings?.length || currentRun?.report?.findings?.length || 0;
  const runId = currentRun?.run_id || currentRun?.id || '';

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-brand-500/20 selection:text-brand-600">
      <Navbar />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />

        <main className="flex-1 overflow-y-auto relative">
          {!currentRun ? (
            <HomeView />
          ) : (
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6">
              {/* Run Header */}
              <div className="flex flex-col space-y-3 pb-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <button
                    onClick={resetToHome}
                    className="inline-flex items-center text-xs font-medium text-muted-foreground hover:text-foreground transition-colors group"
                  >
                    <ArrowLeft className="w-3.5 h-3.5 mr-1 group-hover:-translate-x-0.5 transition-transform" />
                    <span>Back to Research Prompt</span>
                  </button>

                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${
                      currentRun.status === 'completed' 
                        ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
                        : isRunning
                        ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border-brand-500/20 animate-pulse'
                        : 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20'
                    }`}>
                      {currentRun.status}
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-muted border border-border text-muted-foreground">
                      {currentRun.options?.depth || 'standard'}
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground leading-snug">
                    {currentRun.query}
                  </h1>
                  <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                    <span className="flex items-center">
                      <Calendar className="w-3.5 h-3.5 mr-1" />
                      {new Date(currentRun.created_at).toLocaleString()}
                    </span>
                    {currentRun.options?.focus_areas && currentRun.options.focus_areas.length > 0 && (
                      <span className="hidden sm:inline-flex items-center">
                        <Layers className="w-3.5 h-3.5 mr-1" />
                        {currentRun.options.focus_areas.join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Error Banner if Failed */}
              {currentRun.status === 'failed' && (
                <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-300 flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-red-500" />
                  <div className="space-y-1">
                    <h4 className="text-sm font-semibold">Research Run Encountered an Issue</h4>
                    <p className="text-xs leading-relaxed">
                      {currentRun.error || currentRun.error_message || 'The research agent pipeline halted prematurely. Please verify API keys or try running again.'}
                    </p>
                  </div>
                </div>
              )}

              {/* Agent Progress Stepper / Timeline */}
              <div className="rounded-xl border border-border bg-card/60 backdrop-blur-sm overflow-hidden shadow-sm">
                <div 
                  className="px-4 py-3 bg-muted/30 border-b border-border flex items-center justify-between cursor-pointer select-none"
                  onClick={() => setShowTimeline(!showTimeline)}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Agent Orchestration Pipeline
                    </span>
                    {isRunning && (
                      <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
                    )}
                  </div>
                  <button className="text-muted-foreground hover:text-foreground">
                    {showTimeline ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>

                {showTimeline && (
                  <div className="p-4 sm:p-5">
                    <Timeline
                      status={currentRun.status}
                      events={events.length > 0 ? events : (currentRun.events || [])}
                      sourcesCount={sourcesCount}
                      findingsCount={findingsCount}
                      startTime={currentRun.created_at}
                    />
                  </div>
                )}
              </div>

              {/* Tabs Navigation */}
              {currentRun.report && (
                <div className="space-y-6">
                  <div className="flex items-center space-x-1 border-b border-border pb-1 overflow-x-auto scrollbar-none">
                    <button
                      onClick={() => setActiveTab('report')}
                      className={`inline-flex items-center px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                        activeTab === 'report'
                          ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      <FileText className="w-4 h-4 mr-1.5" />
                      <span>Executive Report</span>
                    </button>

                    <button
                      onClick={() => setActiveTab('comparison')}
                      className={`inline-flex items-center px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                        activeTab === 'comparison'
                          ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      <Table className="w-4 h-4 mr-1.5" />
                      <span>Comparison Matrix</span>
                    </button>

                    <button
                      onClick={() => setActiveTab('scorecard')}
                      className={`inline-flex items-center px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                        activeTab === 'scorecard'
                          ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      <BarChart3 className="w-4 h-4 mr-1.5" />
                      <span>Scorecard & Analytics</span>
                    </button>

                    <button
                      onClick={() => setActiveTab('sources')}
                      className={`inline-flex items-center px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                        activeTab === 'sources'
                          ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      <Database className="w-4 h-4 mr-1.5" />
                      <span>Sources & Evidence</span>
                      {sourcesCount > 0 && (
                        <span className="ml-1.5 px-1.5 py-0.2 rounded-full bg-brand-500/20 text-brand-600 dark:text-brand-400 text-[10px]">
                          {sourcesCount}
                        </span>
                      )}
                    </button>

                    <button
                      onClick={() => setActiveTab('ask')}
                      className={`inline-flex items-center px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                        activeTab === 'ask'
                          ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      <MessageSquare className="w-4 h-4 mr-1.5" />
                      <span>Ask Research AI</span>
                    </button>
                  </div>

                  {/* Active Tab Panel */}
                  <div className="pt-2 animate-in fade-in duration-150">
                    {activeTab === 'report' && (
                      <ReportView 
                        report={currentRun.report} 
                        findings={currentRun.findings || currentRun.report.findings || []} 
                      />
                    )}

                    {activeTab === 'comparison' && (
                      <ComparisonTable
                        comparisonData={currentRun.report.comparison_table || currentRun.report.comparison_matrix || {}}
                        findings={currentRun.findings || currentRun.report.findings || []}
                        sources={currentRun.sources || currentRun.report.sources || []}
                      />
                    )}

                    {activeTab === 'scorecard' && (
                      <ScorecardView 
                        profiles={currentRun.report.profiles || currentRun.report.competitor_profiles || []} 
                      />
                    )}

                    {activeTab === 'sources' && (
                      <SourcesView 
                        sources={currentRun.sources || currentRun.report.sources || []} 
                      />
                    )}

                    {activeTab === 'ask' && (
                      <AskChat 
                        runId={runId} 
                        sources={currentRun.sources || currentRun.report.sources || []} 
                      />
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      <ToastContainer />
    </div>
  );
};
export default App;
