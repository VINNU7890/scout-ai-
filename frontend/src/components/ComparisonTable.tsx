import React, { useState } from "react";
import { Finding, SourceItem } from "../types";
import { X, ExternalLink } from "lucide-react";

interface ComparisonTableProps {
  comparisonData: Record<string, Record<string, string>>;
  findings?: Finding[];
  sources?: SourceItem[];
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({
  comparisonData,
  findings = [],
}) => {
  const [selectedCell, setSelectedCell] = useState<{
    aspect: string;
    entity: string;
    text: string;
  } | null>(null);

  if (!comparisonData || Object.keys(comparisonData).length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No comparison data generated yet.
      </div>
    );
  }

  // Extract unique entities from the rows
  const entities: string[] = [];
  Object.values(comparisonData).forEach((row) => {
    Object.keys(row).forEach((ent) => {
      if (!entities.includes(ent)) {
        entities.push(ent);
      }
    });
  });

  const aspects = Object.keys(comparisonData);

  // Find supporting evidence for selected cell
  const matchingFindings = selectedCell
    ? findings.filter(
        (f) =>
          f.entity.toLowerCase() === selectedCell.entity.toLowerCase() &&
          f.aspect.toLowerCase() === selectedCell.aspect.toLowerCase()
      )
    : [];

  return (
    <div className="relative flex flex-col h-full overflow-hidden bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10">
      <div className="p-4 border-b border-white/5 dark:border-white/5 light:border-black/5 flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-gray-100 dark:text-gray-100 light:text-gray-900">
            Cross-Entity Aspect Matrix
          </h3>
          <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-500 mt-0.5">
            Click any cell to inspect source evidence and verbatim citations.
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse min-w-[650px]">
          <thead className="sticky top-0 z-20 bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100 text-xs font-mono uppercase tracking-wider text-gray-400 dark:text-gray-400 light:text-gray-600 border-b border-white/10 light:border-black/10">
            <tr>
              <th className="p-3.5 pl-5 font-semibold sticky left-0 z-30 bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100">
                Aspect
              </th>
              {entities.map((entity) => (
                <th key={entity} className="p-3.5 font-semibold">
                  {entity}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 dark:divide-white/5 light:divide-black/5 text-xs">
            {aspects.map((aspect) => {
              const row = comparisonData[aspect] || {};
              return (
                <tr
                  key={aspect}
                  className="hover:bg-white/[0.02] dark:hover:bg-white/[0.02] light:hover:bg-gray-50/50 transition-colors"
                >
                  <td className="p-3.5 pl-5 font-medium text-gray-300 dark:text-gray-300 light:text-gray-700 sticky left-0 z-10 bg-dark-surface dark:bg-[#12151C] light:bg-white border-r border-white/5 light:border-black/5">
                    {aspect}
                  </td>
                  {entities.map((entity) => {
                    const val = row[entity] || "Not found";
                    const isNotFound = val.toLowerCase().includes("not found");

                    return (
                      <td
                        key={entity}
                        onClick={() => setSelectedCell({ aspect, entity, text: val })}
                        className="p-3.5 cursor-pointer hover:bg-indigo-500/10 transition-colors"
                      >
                        <span
                          className={`line-clamp-2 ${
                            isNotFound
                              ? "text-gray-600 dark:text-gray-600 light:text-gray-400 italic"
                              : "text-gray-300 dark:text-gray-300 light:text-gray-800"
                          }`}
                        >
                          {val}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Detail Modal / Drawer for Cell Evidence */}
      {selectedCell && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-lg bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 p-6 shadow-2xl">
            <div className="flex items-start justify-between pb-3 border-b border-white/10 light:border-black/10">
              <div>
                <span className="text-xs font-mono uppercase text-indigo-400">
                  {selectedCell.aspect}
                </span>
                <h4 className="text-lg font-semibold text-gray-100 dark:text-gray-100 light:text-gray-900 mt-0.5">
                  {selectedCell.entity}
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setSelectedCell(null)}
                className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-white/10"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="my-4 text-sm text-gray-300 dark:text-gray-300 light:text-gray-700 leading-relaxed">
              {selectedCell.text}
            </div>

            {matchingFindings.length > 0 && (
              <div className="mt-4 pt-3 border-t border-white/5 dark:border-white/5 light:border-black/5">
                <h5 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                  Verified Quotes & Sources
                </h5>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {matchingFindings.map((f, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-black/30 dark:bg-black/30 light:bg-gray-100 border border-white/5 text-xs"
                    >
                      <div className="italic text-gray-300 dark:text-gray-300 light:text-gray-800">
                        "{f.evidence_quote}"
                      </div>
                      <div className="mt-1 flex items-center gap-1.5 text-[11px] text-indigo-400 font-mono">
                        {f.source_url ? (
                          <a
                            href={f.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 hover:underline"
                          >
                            {f.source_url.replace(/^https?:\/\//, "").slice(0, 35)}...
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : (
                          <span>Doc: {f.doc_name} (p.{f.page || 1})</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-5 text-right">
              <button
                type="button"
                onClick={() => setSelectedCell(null)}
                className="px-4 py-1.5 rounded-xl text-xs font-medium bg-white/10 hover:bg-white/15 text-gray-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
