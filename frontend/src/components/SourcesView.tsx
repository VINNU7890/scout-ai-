import React, { useState } from "react";
import { SourceItem } from "../types";
import { Search, Globe, FileText, ExternalLink, Calendar, CheckCircle2 } from "lucide-react";

interface SourcesViewProps {
  sources: SourceItem[];
}

export const SourcesView: React.FC<SourcesViewProps> = ({ sources = [] }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | "web" | "doc">("all");

  const filteredSources = sources.filter((s) => {
    const matchesSearch =
      s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.domain && s.domain.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (s.doc_name && s.doc_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      s.supported_claims.some((c) => c.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesType = typeFilter === "all" || s.source_type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="flex flex-col h-full bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 overflow-hidden shadow-sm">
      {/* Search and Filters Header */}
      <div className="p-4 border-b border-white/5 dark:border-white/5 light:border-black/5 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search sources, domains, or claims..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100 rounded-xl border border-white/10 light:border-black/10 text-gray-200 dark:text-gray-200 light:text-gray-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-1.5 p-1 bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100 rounded-xl text-xs font-medium self-start sm:self-auto">
          {(["all", "web", "doc"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTypeFilter(t)}
              className={`px-3 py-1 rounded-lg capitalize transition-colors cursor-pointer ${
                typeFilter === t
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              {t === "all" ? "All Sources" : t === "web" ? "Web Pages" : "Documents"}
            </button>
          ))}
        </div>
      </div>

      {/* Sources Grid List */}
      <div className="flex-1 overflow-y-auto p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredSources.length === 0 ? (
          <div className="col-span-full py-12 text-center text-gray-500 text-sm">
            No sources match your search or filter.
          </div>
        ) : (
          filteredSources.map((source) => (
            <div
              key={source.id}
              className="flex flex-col justify-between p-4 rounded-xl bg-dark-elevated dark:bg-[#181C25] light:bg-gray-50/70 border border-white/5 dark:border-white/5 light:border-black/5 hover:border-indigo-500/30 transition-all shadow-sm"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-5 h-5 rounded font-mono text-xs font-bold bg-indigo-500/20 text-indigo-400">
                      {source.id}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                        source.source_type === "doc"
                          ? "bg-teal-500/10 text-teal-400 border border-teal-500/20"
                          : "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                      }`}
                    >
                      {source.source_type === "doc" ? (
                        <FileText className="w-2.5 h-2.5" />
                      ) : (
                        <Globe className="w-2.5 h-2.5" />
                      )}
                      {source.source_type}
                    </span>
                  </div>

                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-indigo-400 p-1"
                      title="Open source URL"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>

                <h4 className="text-sm font-medium text-gray-200 dark:text-gray-200 light:text-gray-900 line-clamp-1 mb-1">
                  {source.title}
                </h4>

                {source.domain && (
                  <p className="text-xs font-mono text-gray-400 mb-2">
                    {source.domain}
                  </p>
                )}
                {source.doc_name && (
                  <p className="text-xs font-mono text-gray-400 mb-2">
                    {source.doc_name} (Page {source.page || 1})
                  </p>
                )}

                {/* Supported Claims count & list */}
                {source.supported_claims.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-white/5 dark:border-white/5 light:border-black/5">
                    <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider block mb-1.5">
                      Supported Claims ({source.supported_claims.length})
                    </span>
                    <ul className="space-y-1">
                      {source.supported_claims.slice(0, 2).map((claim, cIdx) => (
                        <li
                          key={cIdx}
                          className="flex items-start gap-1.5 text-xs text-gray-300 dark:text-gray-300 light:text-gray-700"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
                          <span className="line-clamp-2">{claim}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-2 flex items-center gap-1.5 text-[11px] font-mono text-gray-500">
                <Calendar className="w-3 h-3" />
                <span>Retrieved {source.retrieved_at ? source.retrieved_at.slice(0, 10) : "Recently"}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
