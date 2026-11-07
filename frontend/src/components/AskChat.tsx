import React, { useState } from "react";
import { Send, Bot, User, Sparkles } from "lucide-react";
import { askQuestion } from "../services/api";
import { ChatMessage, useAppStore } from "../store/useAppStore";
import { CitationHover } from "./CitationHover";
import { SourceItem } from "../types";

interface AskChatProps {
  runId: string;
  sources?: SourceItem[];
}

export const AskChat: React.FC<AskChatProps> = ({ runId, sources = [] }) => {
  const { chatMessages, addChatMessage } = useAppStore();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const defaultSuggestions = [
    "Compare fee tiers across all competitors",
    "What are the primary compliance risks identified?",
    "Which entity has the strongest go-to-market moat?",
  ];

  const handleSend = async (questionText: string) => {
    const q = questionText.trim();
    if (!q || isLoading) return;

    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substring(2, 9),
      role: "user",
      content: q,
    };
    addChatMessage(userMsg);
    setInput("");
    setIsLoading(true);

    try {
      const response = await askQuestion(runId, q);
      const assistantMsg: ChatMessage = {
        id: Math.random().toString(36).substring(2, 9),
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        suggestions: response.follow_up_suggestions,
      };
      addChatMessage(assistantMsg);
    } catch (err: any) {
      addChatMessage({
        id: Math.random().toString(36).substring(2, 9),
        role: "assistant",
        content: `Error: ${err.message || "Failed to retrieve grounded answer."}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 overflow-hidden shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-white/5 dark:border-white/5 light:border-black/5 flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-gray-100 dark:text-gray-100 light:text-gray-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Interactive Report Intelligence
          </h3>
          <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-500 mt-0.5">
            Ask any follow-up question. Answers are strictly grounded in verified report findings and citations.
          </p>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {chatMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500">
            <Bot className="w-10 h-10 text-indigo-500/50 mb-3" />
            <p className="text-sm font-medium text-gray-300 dark:text-gray-300 light:text-gray-700">
              Explore deeper insights from this brief
            </p>
            <p className="text-xs text-gray-400 max-w-sm mt-1">
              Select an inquiry chip below or ask anything about competitive positioning, pricing, or regulatory filings.
            </p>

            <div className="flex flex-wrap justify-center gap-2 mt-6 max-w-md">
              {defaultSuggestions.map((sug, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSend(sug)}
                  className="px-3 py-1.5 rounded-xl text-xs font-medium bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100 text-gray-300 dark:text-gray-300 light:text-gray-800 border border-white/10 light:border-black/10 hover:border-indigo-500/40 hover:text-indigo-400 transition-all cursor-pointer"
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>
        ) : (
          chatMessages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3 text-sm ${
                msg.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-teal-500/20 text-teal-400 border border-teal-500/30"
                }`}
              >
                {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100 text-gray-200 dark:text-gray-200 light:text-gray-900 border border-white/5 light:border-black/5"
                }`}
              >
                <div>{msg.content}</div>

                {/* Inline Citations in assistant reply */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-white/10 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] uppercase font-mono text-gray-400">Sources:</span>
                    {msg.citations.map((c) => (
                      <CitationHover
                        key={c.id}
                        id={c.id}
                        source={sources.find((s) => s.id === c.id) || c}
                      />
                    ))}
                  </div>
                )}

                {/* Follow up suggestions */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-white/5 flex flex-wrap gap-1.5">
                    {msg.suggestions.map((sug, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleSend(sug)}
                        className="px-2 py-1 rounded-lg text-[11px] bg-black/20 hover:bg-black/40 text-indigo-300 border border-indigo-500/20 hover:border-indigo-500/50 transition-colors cursor-pointer"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-center gap-3 text-sm text-gray-400 animate-pulse">
            <div className="w-7 h-7 rounded-full bg-teal-500/20 flex items-center justify-center text-teal-400">
              <Bot className="w-4 h-4" />
            </div>
            <div className="px-3 py-2 rounded-xl bg-dark-elevated text-xs font-mono">
              Formulating grounded response...
            </div>
          </div>
        )}
      </div>

      {/* Input box */}
      <div className="p-4 border-t border-white/5 dark:border-white/5 light:border-black/5">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask a question about this research..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            className="flex-1 px-4 py-2.5 text-xs bg-dark-elevated dark:bg-[#181C25] light:bg-gray-100 rounded-xl border border-white/10 light:border-black/10 text-gray-200 dark:text-gray-200 light:text-gray-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white transition-colors cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
