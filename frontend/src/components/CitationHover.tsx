import React, { useState } from "react";
import { SourceItem, Finding } from "../types";
import { ExternalLink, FileText, Globe } from "lucide-react";

interface CitationHoverProps {
  id: number;
  source?: SourceItem;
  findings?: Finding[];
}

export const CitationHover: React.FC<CitationHoverProps> = ({ id, source, findings }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Find supporting quote from findings matching this source
  const matchingFinding = findings?.find(
    (f) =>
      (source?.url && f.source_url === source.url) ||
      (source?.doc_name && f.doc_name === source.doc_name)
  );

  return (
    <span
      className="relative inline-block mx-0.5 align-baseline"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-mono font-medium rounded bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 hover:text-indigo-300 dark:bg-indigo-500/20 dark:text-indigo-300 border border-indigo-500/30 transition-colors cursor-pointer"
        aria-label={`Citation source ${id}`}
      >
        [{id}]
      </button>

      {isOpen && (
        <div
          role="tooltip"
          className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 p-3 text-left bg-dark-surface dark:bg-[#12151C] light:bg-white text-gray-200 dark:text-gray-200 light:text-gray-900 rounded-xl shadow-xl border border-dark-border dark:border-white/10 light:border-black/10 text-xs backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
        >
          <div className="flex items-center gap-2 mb-1.5 font-medium text-indigo-400">
            {source?.source_type === "doc" ? (
              <FileText className="w-3.5 h-3.5" />
            ) : (
              <Globe className="w-3.5 h-3.5" />
            )}
            <span className="truncate">Source [{id}]: {source?.title || "Referenced Source"}</span>
          </div>

          {source?.domain && (
            <div className="text-[11px] text-gray-400 dark:text-gray-400 light:text-gray-500 mb-1">
              Domain: <span className="font-mono text-gray-300">{source.domain}</span>
            </div>
          )}

          {source?.doc_name && (
            <div className="text-[11px] text-gray-400 mb-1">
              Document: <span className="font-mono text-gray-300">{source.doc_name}</span> (p.{source.page || 1})
            </div>
          )}

          {matchingFinding?.evidence_quote && (
            <div className="mt-2 p-2 rounded bg-black/30 dark:bg-black/30 light:bg-gray-100 border border-white/5 light:border-black/5 italic text-gray-300 dark:text-gray-300 light:text-gray-700">
              "{matchingFinding.evidence_quote}"
            </div>
          )}

          {source?.url && (
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2.5 inline-flex items-center gap-1 text-[11px] font-medium text-indigo-400 hover:text-indigo-300 hover:underline"
            >
              Open live source <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      )}
    </span>
  );
};
