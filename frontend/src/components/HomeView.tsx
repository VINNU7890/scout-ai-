import React, { useState } from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  Compass, 
  SlidersHorizontal, 
  Target, 
  ShieldCheck, 
  Zap,
  Globe2,
  BookOpen
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { DocumentUploadZone } from './DocumentUploadZone';
import { ResearchOptions } from '../types';

const EXAMPLE_QUERIES = [
  {
    title: 'BitDelta India vs Rivals',
    query: 'BitDelta India vs CoinDCX, CoinSwitch, ZebPay, and Mudrex: Compliance, fees, features, and GTM strategy',
    depth: 'standard' as const,
    focus: ['Regulatory & Compliance', 'Pricing & Monetization', 'Product Features', 'Go-To-Market']
  },
  {
    title: 'Notion vs Obsidian & Coda',
    query: 'Notion vs Obsidian and Coda for enterprise engineering knowledge bases and AI workspaces',
    depth: 'standard' as const,
    focus: ['Product Features', 'Architecture & Security', 'Pricing & Monetization']
  },
  {
    title: 'Stripe vs Adyen in LATAM',
    query: 'Stripe vs Adyen in LATAM: Local acquiring licenses, payment methods (PIX, OXXO), and fee structures',
    depth: 'deep' as const,
    focus: ['Regulatory & Compliance', 'Pricing & Monetization', 'Go-To-Market']
  },
  {
    title: 'Linear vs Jira',
    query: 'Linear vs Jira for high-velocity software engineering teams: Developer experience, integrations, and pricing',
    depth: 'quick' as const,
    focus: ['Product Features', 'Go-To-Market']
  }
];

const AVAILABLE_FOCUS_AREAS = [
  'Pricing & Monetization',
  'Regulatory & Compliance',
  'Product Features',
  'Go-To-Market',
  'Financials & Valuation',
  'Architecture & Security'
];

export const HomeView: React.FC = () => {
  const { startResearch, isStartingRun, uploadedDocuments } = useAppStore();

  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState<'quick' | 'standard' | 'deep'>('standard');
  const [focusAreas, setFocusAreas] = useState<string[]>([
    'Pricing & Monetization',
    'Product Features',
    'Go-To-Market'
  ]);
  const [competitorsInput, setCompetitorsInput] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const toggleFocusArea = (area: string) => {
    if (focusAreas.includes(area)) {
      setFocusAreas(focusAreas.filter(a => a !== area));
    } else {
      setFocusAreas([...focusAreas, area]);
    }
  };

  const handleSelectExample = (ex: typeof EXAMPLE_QUERIES[0]) => {
    setQuery(ex.query);
    setDepth(ex.depth);
    setFocusAreas(ex.focus);
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isStartingRun) return;

    const competitorsList = competitorsInput
      .split(',')
      .map(c => c.trim())
      .filter(Boolean);

    const options: ResearchOptions = {
      depth,
      focus_areas: focusAreas,
      competitors: competitorsList.length > 0 ? competitorsList : undefined,
      include_internal_docs: uploadedDocuments.length > 0
    };

    startResearch(query.trim(), options, uploadedDocuments.map(d => d.id));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 sm:py-12 space-y-8 animate-in fade-in duration-300">
      {/* Hero Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-600 dark:text-brand-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Multi-Node Autonomous Research Agent</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
          Competitor & Market Intelligence, <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-brand-600 to-indigo-500 bg-clip-text text-transparent">
            Rigorous, Cited & Verified
          </span>
        </h1>
        <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
          Execute multi-agent autonomous web and document research with DuckDuckGo, vector RAG, 
          and LLM-as-judge verification against source evidence. Zero hallucinations allowed.
        </p>
      </div>

      {/* Main Research Card */}
      <div className="rounded-2xl border border-border bg-card p-4 sm:p-6 shadow-xl shadow-brand-500/5 space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. BitDelta India vs CoinDCX, CoinSwitch, ZebPay: Compliance, pricing, features, and GTM strategy..."
              rows={3}
              className="w-full p-4 rounded-xl bg-background border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm leading-relaxed resize-none transition-all"
            />
            <div className="absolute right-3 bottom-3 hidden sm:flex items-center space-x-1 text-[11px] text-muted-foreground/80 bg-muted/60 px-2 py-0.5 rounded border border-border">
              <span>Press</span>
              <kbd className="font-mono bg-card px-1 py-0.2 rounded border text-[10px]">Ctrl</kbd>
              <span>+</span>
              <kbd className="font-mono bg-card px-1 py-0.2 rounded border text-[10px]">Enter</kbd>
            </div>
          </div>

          {/* Example Chips */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center">
              <Compass className="w-3 h-3 mr-1 text-brand-500" />
              Suggested Scenarios:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {EXAMPLE_QUERIES.map((ex, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSelectExample(ex)}
                  className="text-xs px-2.5 py-1 rounded-lg bg-muted/70 hover:bg-muted text-foreground/90 border border-border/70 hover:border-brand-500/40 transition-all text-left"
                >
                  {ex.title}
                </button>
              ))}
            </div>
          </div>

          {/* Depth & Config Controls */}
          <div className="pt-2 border-t border-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            {/* Depth Selector */}
            <div className="flex items-center space-x-2">
              <span className="text-xs font-medium text-muted-foreground">Depth:</span>
              <div className="inline-flex rounded-lg border border-border p-0.5 bg-muted/30">
                {(['quick', 'standard', 'deep'] as const).map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setDepth(d)}
                    className={`px-3 py-1 rounded-md text-xs font-medium capitalize transition-all ${
                      depth === d 
                        ? 'bg-card text-brand-600 dark:text-brand-400 shadow-sm border border-border/80' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Toggle Advanced */}
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="inline-flex items-center text-xs font-medium text-brand-600 dark:text-brand-400 hover:underline"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 mr-1" />
              <span>{showAdvanced ? 'Hide filters & docs' : 'Customize focus areas & upload documents'}</span>
            </button>
          </div>

          {/* Expandable Advanced Options */}
          {showAdvanced && (
            <div className="pt-4 border-t border-border space-y-5 animate-in fade-in duration-200">
              {/* Focus Areas Chips */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-foreground flex items-center">
                  <Target className="w-3.5 h-3.5 mr-1 text-brand-500" />
                  Key Focus Areas
                </label>
                <div className="flex flex-wrap gap-2">
                  {AVAILABLE_FOCUS_AREAS.map((area) => {
                    const active = focusAreas.includes(area);
                    return (
                      <button
                        key={area}
                        type="button"
                        onClick={() => toggleFocusArea(area)}
                        className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                          active
                            ? 'bg-brand-500/10 border-brand-500/40 text-brand-700 dark:text-brand-300 font-medium'
                            : 'bg-muted/40 border-border text-muted-foreground hover:text-foreground'
                        }`}
                      >
                        {area}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Explicit Competitors List */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground flex items-center">
                  <Globe2 className="w-3.5 h-3.5 mr-1 text-brand-500" />
                  Explicit Competitor Names (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. BitDelta, CoinDCX, CoinSwitch, ZebPay"
                  value={competitorsInput}
                  onChange={(e) => setCompetitorsInput(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-background border border-border text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
                <p className="text-[11px] text-muted-foreground">
                  Leave empty to let the Planner node automatically detect competitors from your prompt.
                </p>
              </div>

              {/* Internal Document RAG Upload Zone */}
              <div className="space-y-2 pt-2">
                <label className="text-xs font-semibold text-foreground flex items-center">
                  <BookOpen className="w-3.5 h-3.5 mr-1 text-brand-500" />
                  Internal Documents RAG (Vector Knowledge Base)
                </label>
                <p className="text-[11px] text-muted-foreground">
                  Upload internal PDFs, DOCX, battlecards, or pricing guides to fuse internal knowledge with live web research.
                </p>
                <DocumentUploadZone />
              </div>
            </div>
          )}

          {/* Primary Action Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={!query.trim() || isStartingRun}
              className="w-full py-3 px-6 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-brand-700 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-brand-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-all transform active:scale-[0.99]"
            >
              {isStartingRun ? (
                <>
                  <Zap className="w-4 h-4 animate-spin" />
                  <span>Launching Autonomous Agent...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Start Autonomous Research</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
        <div className="p-4 rounded-xl border border-border bg-card/50 text-left space-y-1.5">
          <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center text-brand-500">
            <Zap className="w-4 h-4" />
          </div>
          <h3 className="text-xs font-bold text-foreground">LangGraph 6-Node Pipeline</h3>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            Planner, parallel Web & Doc researchers, Analyst, Writer, and Verifier running deterministically.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card/50 text-left space-y-1.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <h3 className="text-xs font-bold text-foreground">Grounded LLM-as-Judge</h3>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            Every factual assertion is cross-checked against source quotes (&le;25 words). Unsupported claims are rejected.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card/50 text-left space-y-1.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500">
            <Globe2 className="w-4 h-4" />
          </div>
          <h3 className="text-xs font-bold text-foreground">Multi-Format Export</h3>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            Download executive summaries and comparison tables as Markdown, ReportLab PDF, or Microsoft Word DOCX.
          </p>
        </div>
      </div>
    </div>
  );
};
