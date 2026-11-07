import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Report, Finding } from "../types";
import { CitationHover } from "./CitationHover";
import { ShieldCheck, AlertTriangle } from "lucide-react";

interface ReportViewProps {
  report: Report;
  findings?: Finding[];
}

export const ReportView: React.FC<ReportViewProps> = ({ report, findings = [] }) => {
  const sourcesMap = useMemo(() => {
    const map = new Map<number, (typeof report.sources)[0]>();
    report.sources?.forEach((s) => map.set(s.id, s));
    return map;
  }, [report.sources]);

  const hasIssues = report.warnings && report.warnings.length > 0;

  // Custom text renderer that identifies citation markers like [1], [2], [1, 3] and replaces with CitationHover
  const renderTextWithCitations = (text: string) => {
    const regex = /\[(\d+(?:\s*,\s*\d+)*)\]/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }

      const indices = match[1].split(",").map((s) => parseInt(s.trim(), 10));
      indices.forEach((id, idx) => {
        const source = sourcesMap.get(id);
        parts.push(
          <CitationHover
            key={`${match!.index}-${idx}-${id}`}
            id={id}
            source={source}
            findings={findings}
          />
        );
      });

      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  const tocItems = [
    { title: "Executive Summary", id: "executive-summary" },
    { title: "Key Takeaways", id: "key-takeaways" },
    { title: "Comparison Matrix", id: "comparison-matrix" },
    { title: "Competitor Profiles", id: "competitor-profiles" },
    { title: "SWOT Analysis", id: "swot-analysis" },
    { title: "Gaps & Opportunities", id: "market-gaps--opportunities" },
    { title: "Recommended GTM Actions", id: "recommended-gtm-actions" },
    { title: "Methodology & Limitations", id: "methodology--limitations" },
    { title: "Sources & Citations", id: "sources--citations" },
  ];

  return (
    <div className="flex gap-6 h-full overflow-y-auto pr-1">
      {/* Main Report Column */}
      <div className="flex-1 min-w-0 bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 p-6 sm:p-8 shadow-sm">
        {/* Verification Banner */}
        <div
          className={`mb-6 p-4 rounded-xl border flex items-start gap-3 transition-colors ${
            hasIssues
              ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
              : "bg-teal-500/10 border-teal-500/30 text-teal-300"
          }`}
        >
          {hasIssues ? (
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          ) : (
            <ShieldCheck className="w-5 h-5 text-teal-400 shrink-0 mt-0.5" />
          )}
          <div className="flex-1 text-xs">
            <div className="font-semibold text-sm">
              {hasIssues
                ? `${report.warnings?.length} Claims Flagged for Review`
                : "Report Fully Verified"}
            </div>
            <p className="mt-0.5 opacity-90">
              {hasIssues
                ? "The automated LLM-as-judge fact-checking pass detected potential claim discrepancies against source quotes."
                : "Every factual claim in this report has been verified against extracted quotes with zero hallucinations detected."}
            </p>
            {hasIssues && (
              <ul className="mt-2 space-y-1 list-disc pl-4 text-[11px]">
                {report.warnings?.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Markdown Rendered Report with custom citation handling */}
        <div className="prose dark:prose-invert prose-indigo max-w-none text-xs sm:text-sm leading-relaxed">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => {
                if (typeof children === "string") {
                  return <p className="my-3 text-gray-300 dark:text-gray-300 light:text-gray-700 leading-relaxed">{renderTextWithCitations(children)}</p>;
                }
                return <p className="my-3 text-gray-300 dark:text-gray-300 light:text-gray-700 leading-relaxed">{children}</p>;
              },
              li: ({ children }) => {
                if (typeof children === "string") {
                  return <li className="my-1 text-gray-300 dark:text-gray-300 light:text-gray-700">{renderTextWithCitations(children)}</li>;
                }
                return <li className="my-1 text-gray-300 dark:text-gray-300 light:text-gray-700">{children}</li>;
              },
              h1: ({ children }) => (
                <h1 className="text-xl sm:text-2xl font-bold text-gray-100 dark:text-gray-100 light:text-gray-900 mt-2 mb-4 tracking-tight border-b border-white/10 pb-3">
                  {children}
                </h1>
              ),
              h2: ({ children }) => {
                const text = String(children);
                const id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-");
                return (
                  <h2
                    id={id}
                    className="text-base sm:text-lg font-semibold text-gray-100 dark:text-gray-100 light:text-gray-900 mt-6 mb-3 scroll-mt-6"
                  >
                    {children}
                  </h2>
                );
              },
              h3: ({ children }) => (
                <h3 className="text-sm sm:text-base font-medium text-indigo-400 mt-4 mb-2">
                  {children}
                </h3>
              ),
              table: ({ children }) => (
                <div className="overflow-x-auto my-4 rounded-xl border border-white/10">
                  <table className="w-full border-collapse text-left text-xs">{children}</table>
                </div>
              ),
              th: ({ children }) => (
                <th className="p-2.5 bg-dark-elevated text-gray-300 font-semibold border-b border-white/10 font-mono">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="p-2.5 border-b border-white/5 text-gray-300">
                  {typeof children === "string" ? renderTextWithCitations(children) : children}
                </td>
              ),
            }}
          >
            {report.markdown_content || `# ${report.title}\n\n${report.executive_summary}`}
          </ReactMarkdown>
        </div>
      </div>

      {/* Sticky Table of Contents sidebar on desktop */}
      <div className="hidden lg:block w-56 shrink-0">
        <div className="sticky top-0 p-4 rounded-2xl bg-dark-surface dark:bg-[#12151C] light:bg-white border border-dark-border dark:border-white/10 light:border-black/10">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 block mb-3 font-mono">
            Table of Contents
          </span>
          <nav className="space-y-1.5 text-xs">
            {tocItems.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className="block text-gray-400 hover:text-indigo-400 hover:translate-x-1 transition-all py-1 truncate"
              >
                {item.title}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
};
