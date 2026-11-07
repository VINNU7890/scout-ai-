import React, { useEffect, useState } from "react";
import { Check, Clock, Database, FileSearch, Layers, Sparkles, ShieldCheck, XCircle } from "lucide-react";
import { RunEventPayload, StageName } from "../types";

interface TimelineProps {
  status: string;
  events: RunEventPayload[];
  sourcesCount: number;
  findingsCount: number;
  onCancel?: () => void;
  startTime?: string;
}

interface StageConfig {
  key: StageName;
  label: string;
  icon: React.ReactNode;
}

const STAGES: StageConfig[] = [
  { key: "plan", label: "Plan & Target Setup", icon: <Layers className="w-4 h-4" /> },
  { key: "web_research", label: "Web Intelligence", icon: <FileSearch className="w-4 h-4" /> },
  { key: "doc_research", label: "Document Vector RAG", icon: <Database className="w-4 h-4" /> },
  { key: "analyze", label: "Strategic Synthesis", icon: <Sparkles className="w-4 h-4" /> },
  { key: "write", label: "Drafting Executive Brief", icon: <Layers className="w-4 h-4" /> },
  { key: "verify", label: "Citation & Fact Verifier", icon: <ShieldCheck className="w-4 h-4" /> },
];

export const Timeline: React.FC<TimelineProps> = ({
  status,
  events,
  sourcesCount,
  findingsCount,
  onCancel,
  startTime,
}) => {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (status === "completed" || status === "failed" || status === "cancelled") return;

    const start = startTime ? new Date(startTime).getTime() : Date.now();
    const timer = setInterval(() => {
      setElapsedSeconds(Math.max(0, Math.floor((Date.now() - start) / 1000)));
    }, 1000);

    return () => clearInterval(timer);
  }, [status, startTime]);

  const formatElapsed = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const remaining = sec % 60;
    return `${mins}:${remaining < 10 ? "0" : ""}${remaining}`;
  };

  // Determine current active stage from events or status
  const currentStage: StageName = (() => {
    if (status === "completed") return "done";
    for (let i = events.length - 1; i >= 0; i--) {
      if (events[i].stage && events[i].stage !== "init") {
        return events[i].stage;
      }
    }
    return "plan";
  })();

  const isStageCompleted = (stageKey: StageName) => {
    if (status === "completed") return true;
    const stageOrder: StageName[] = ["plan", "web_research", "doc_research", "analyze", "write", "verify", "done"];
    const currentIndex = stageOrder.indexOf(currentStage);
    const targetIndex = stageOrder.indexOf(stageKey);
    return targetIndex < currentIndex;
  };

  const isStageActive = (stageKey: StageName) => {
    if (status === "completed" || status === "cancelled" || status === "failed") return false;
    return currentStage === stageKey;
  };

  return (
    <div className="flex flex-col h-full bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 p-5 shadow-sm">
      {/* Header with Stats */}
      <div className="flex items-center justify-between pb-4 border-b border-white/5 dark:border-white/5 light:border-black/5">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          <h2 className="text-sm font-semibold tracking-wide uppercase text-gray-400 dark:text-gray-400 light:text-gray-500">
            Agent Timeline
          </h2>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-gray-400">
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>{formatElapsed(elapsedSeconds)}</span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-3 my-4">
        <div className="p-3 rounded-xl bg-black/20 dark:bg-black/20 light:bg-gray-50 border border-white/5 dark:border-white/5 light:border-black/5">
          <span className="text-[11px] text-gray-400">Sources Read</span>
          <div className="text-xl font-mono font-semibold text-indigo-400">{sourcesCount}</div>
        </div>
        <div className="p-3 rounded-xl bg-black/20 dark:bg-black/20 light:bg-gray-50 border border-white/5 dark:border-white/5 light:border-black/5">
          <span className="text-[11px] text-gray-400">Verified Findings</span>
          <div className="text-xl font-mono font-semibold text-teal-400">{findingsCount}</div>
        </div>
      </div>

      {/* Vertical Stepper */}
      <div
        className="flex-1 overflow-y-auto space-y-4 pr-1 py-1"
        role="region"
        aria-label="Agent execution progress"
        aria-live="polite"
      >
        {STAGES.map((stage, idx) => {
          const completed = isStageCompleted(stage.key);
          const active = isStageActive(stage.key);
          const stageEvents = events.filter((e) => e.stage === stage.key);

          return (
            <div key={stage.key} className="relative flex gap-3 text-sm">
              {/* Connector line */}
              {idx < STAGES.length - 1 && (
                <div
                  className={`absolute left-[13px] top-7 bottom-[-16px] w-[2px] transition-colors duration-300 ${
                    completed ? "bg-indigo-500" : "bg-white/10 dark:bg-white/10 light:bg-black/10"
                  }`}
                />
              )}

              {/* Status Circle */}
              <div
                className={`relative z-10 flex items-center justify-center w-7 h-7 rounded-full shrink-0 transition-all duration-300 ${
                  completed
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/20"
                    : active
                    ? "bg-gradient-to-tr from-indigo-500 to-purple-600 text-white ring-4 ring-indigo-500/20 animate-pulse shadow-lg shadow-indigo-500/40"
                    : "bg-white/5 dark:bg-white/5 light:bg-black/5 text-gray-500 border border-white/10"
                }`}
              >
                {completed ? <Check className="w-3.5 h-3.5" /> : stage.icon}
              </div>

              {/* Stage content */}
              <div className="flex-1 pt-0.5">
                <div className="flex items-center justify-between">
                  <span
                    className={`font-medium ${
                      active
                        ? "text-indigo-400 font-semibold"
                        : completed
                        ? "text-gray-200 dark:text-gray-200 light:text-gray-800"
                        : "text-gray-500"
                    }`}
                  >
                    {stage.label}
                  </span>
                  {active && (
                    <span className="text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                      Active
                    </span>
                  )}
                </div>

                {/* Sub-steps streaming list */}
                {stageEvents.length > 0 && (
                  <div className="mt-2 space-y-1.5 pl-2 border-l border-white/5 dark:border-white/5 light:border-black/5">
                    {stageEvents.slice(-4).map((e, eIdx) => (
                      <div
                        key={e.id || eIdx}
                        className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600 flex items-start gap-1.5 font-sans animate-in fade-in slide-in-from-left-1 duration-150"
                      >
                        <span className="text-indigo-400 shrink-0">›</span>
                        <span className="truncate">{e.message}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Cancel button if actively running */}
      {status !== "completed" && status !== "failed" && status !== "cancelled" && onCancel && (
        <div className="pt-4 mt-2 border-t border-white/5 dark:border-white/5 light:border-black/5">
          <button
            type="button"
            onClick={onCancel}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors cursor-pointer"
          >
            <XCircle className="w-3.5 h-3.5" />
            Cancel Research Run
          </button>
        </div>
      )}
    </div>
  );
};
