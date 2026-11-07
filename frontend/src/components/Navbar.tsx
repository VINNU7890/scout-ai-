import React, { useState } from 'react';
import { 
  Bot, 
  Download, 
  Share2, 
  RotateCcw, 
  Moon, 
  Sun, 
  FileText, 
  FileCode, 
  FileType, 
  Check, 
  ChevronDown
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { exportReport } from '../services/api';

export const Navbar: React.FC = () => {
  const { 
    currentRun, 
    theme, 
    toggleTheme, 
    addToast, 
    resetToHome,
    startResearch,
    uploadedDocuments 
  } = useAppStore();
  
  const [exportOpen, setExportOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const reportMarkdown = currentRun?.report?.markdown_content || currentRun?.report?.raw_markdown;

  const handleCopy = async () => {
    if (!reportMarkdown) {
      addToast('No report content to copy', 'error');
      return;
    }
    try {
      await navigator.clipboard.writeText(reportMarkdown);
      setCopied(true);
      addToast('Report copied to clipboard', 'success');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      addToast('Failed to copy to clipboard', 'error');
    }
  };

  const handleExport = async (format: 'markdown' | 'pdf' | 'docx') => {
    if (!currentRun) return;
    const runId = currentRun.run_id || currentRun.id;
    setIsExporting(true);
    setExportOpen(false);
    try {
      await exportReport(runId, format);
      addToast(`Downloaded ${format.toUpperCase()} report`, 'success');
    } catch (err: any) {
      addToast(err?.message || `Failed to export ${format}`, 'error');
    } finally {
      setIsExporting(false);
    }
  };

  const handleRerun = () => {
    if (!currentRun) return;
    startResearch(
      currentRun.query,
      currentRun.options,
      uploadedDocuments.map(d => d.id)
    );
    addToast('Re-running research...', 'info');
  };

  return (
    <header className="h-16 border-b border-border bg-card/60 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-4 sm:px-6">
      {/* Brand & Mode */}
      <div className="flex items-center space-x-3 cursor-pointer" onClick={resetToHome}>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
          <Bot className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
              Scout<span className="text-brand-500">AI</span>
            </span>
            <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20">
              Agent
            </span>
          </div>
          <span className="text-[11px] text-muted-foreground hidden sm:inline">
            Autonomous Competitor & Market Research
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {currentRun && currentRun.status === 'completed' && (
          <>
            {/* Re-run button */}
            <button
              onClick={handleRerun}
              title="Re-run research with same query"
              className="inline-flex items-center px-2.5 py-1.5 rounded-lg border border-border text-xs font-medium text-foreground hover:bg-muted transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5 sm:mr-1.5 text-muted-foreground" />
              <span className="hidden sm:inline">Re-run</span>
            </button>

            {/* Copy button */}
            <button
              onClick={handleCopy}
              className="inline-flex items-center px-2.5 py-1.5 rounded-lg border border-border text-xs font-medium text-foreground hover:bg-muted transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 sm:mr-1.5 text-emerald-500" />
                  <span className="hidden sm:inline text-emerald-600 dark:text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Share2 className="w-3.5 h-3.5 sm:mr-1.5 text-muted-foreground" />
                  <span className="hidden sm:inline">Copy MD</span>
                </>
              )}
            </button>

            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={() => setExportOpen(!exportOpen)}
                disabled={isExporting}
                className="inline-flex items-center px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-medium shadow-sm transition-colors disabled:opacity-50"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" />
                <span>Export</span>
                <ChevronDown className="w-3 h-3 ml-1 text-white/80" />
              </button>

              {exportOpen && (
                <div 
                  className="absolute right-0 mt-2 w-48 rounded-xl bg-card border border-border shadow-xl py-1 z-50 animate-in fade-in zoom-in-95 duration-100"
                  onMouseLeave={() => setExportOpen(false)}
                >
                  <button
                    onClick={() => handleExport('markdown')}
                    className="w-full flex items-center px-3 py-2 text-xs text-foreground hover:bg-muted text-left transition-colors"
                  >
                    <FileCode className="w-4 h-4 mr-2 text-brand-500" />
                    <span>Markdown (.md)</span>
                  </button>
                  <button
                    onClick={() => handleExport('pdf')}
                    className="w-full flex items-center px-3 py-2 text-xs text-foreground hover:bg-muted text-left transition-colors"
                  >
                    <FileType className="w-4 h-4 mr-2 text-red-500" />
                    <span>Executive PDF (.pdf)</span>
                  </button>
                  <button
                    onClick={() => handleExport('docx')}
                    className="w-full flex items-center px-3 py-2 text-xs text-foreground hover:bg-muted text-left transition-colors"
                  >
                    <FileText className="w-4 h-4 mr-2 text-blue-500" />
                    <span>Word Document (.docx)</span>
                  </button>
                </div>
              )}
            </div>
          </>
        )}

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="p-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
};
