import { create } from "zustand";
import { 
  RunEventPayload, 
  RunResponse, 
  RunListItem,
  SourceItem, 
  ResearchOptions,
  DocumentUploadResponse 
} from "../types";
import { 
  createRun, 
  getRun, 
  listRuns, 
  subscribeToEvents 
} from "../services/api";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: SourceItem[];
  suggestions?: string[];
}

export interface Toast {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
}

interface AppState {
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light") => void;
  toggleTheme: () => void;

  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  runs: RunListItem[];
  activeRunId: string | null;
  activeRun: RunResponse | null;
  currentRun: RunResponse | null;
  isStartingRun: boolean;

  uploadedDocuments: DocumentUploadResponse[];
  addUploadedDocument: (doc: DocumentUploadResponse) => void;
  removeUploadedDocument: (id: string) => void;
  clearUploadedDocuments: () => void;

  events: RunEventPayload[];
  addEvent: (event: RunEventPayload) => void;
  clearEvents: () => void;

  activeTab: "report" | "comparison" | "scorecard" | "sources" | "ask";
  setActiveTab: (tab: "report" | "comparison" | "scorecard" | "sources" | "ask") => void;

  chatMessages: ChatMessage[];
  addChatMessage: (msg: ChatMessage) => void;
  clearChat: () => void;

  toasts: Toast[];
  addToast: (messageOrToast: string | Omit<Toast, "id">, type?: Toast["type"]) => void;
  removeToast: (id: string) => void;

  // Actions
  fetchRuns: () => Promise<void>;
  fetchRun: (id: string) => Promise<void>;
  startResearch: (query: string, options: ResearchOptions, docIds?: string[]) => Promise<void>;
  resetToHome: () => void;
  setActiveRun: (run: RunResponse | null) => void;
  setActiveRunId: (id: string | null) => void;
}

let activeEventSourceCleanup: (() => void) | null = null;

export const useAppStore = create<AppState>((set, get) => ({
  theme: (localStorage.getItem("scoutai_theme") as "dark" | "light") || "dark",
  setTheme: (theme) => {
    localStorage.setItem("scoutai_theme", theme);
    document.documentElement.classList.toggle("dark", theme === "dark");
    set({ theme });
  },
  toggleTheme: () => {
    const next = get().theme === "dark" ? "light" : "dark";
    localStorage.setItem("scoutai_theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
    set({ theme: next });
  },

  sidebarOpen: true,
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  runs: [],
  activeRunId: null,
  activeRun: null,
  currentRun: null,
  isStartingRun: false,

  uploadedDocuments: [],
  addUploadedDocument: (doc) => set((s) => ({ uploadedDocuments: [...s.uploadedDocuments, doc] })),
  removeUploadedDocument: (id) => set((s) => ({ uploadedDocuments: s.uploadedDocuments.filter(d => d.id !== id) })),
  clearUploadedDocuments: () => set({ uploadedDocuments: [] }),

  events: [],
  addEvent: (event) => set((s) => ({ events: [...s.events, event] })),
  clearEvents: () => set({ events: [] }),

  activeTab: "report",
  setActiveTab: (activeTab) => set({ activeTab }),

  chatMessages: [],
  addChatMessage: (msg) => set((s) => ({ chatMessages: [...s.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),

  toasts: [],
  addToast: (messageOrToast, type = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    const toastObj: Toast = typeof messageOrToast === "string" 
      ? { id, message: messageOrToast, type } 
      : { id, message: messageOrToast.message, type: messageOrToast.type };

    set((s) => ({ toasts: [...s.toasts, toastObj] }));
    setTimeout(() => {
      get().removeToast(id);
    }, 4500);
  },
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),

  setActiveRunId: (id) => {
    set({ activeRunId: id, events: [], chatMessages: [] });
  },

  setActiveRun: (run) => {
    set({ 
      activeRun: run, 
      currentRun: run, 
      activeRunId: run ? run.id : null 
    });
  },

  resetToHome: () => {
    if (activeEventSourceCleanup) {
      activeEventSourceCleanup();
      activeEventSourceCleanup = null;
    }
    set({
      activeRun: null,
      currentRun: null,
      activeRunId: null,
      events: [],
      chatMessages: [],
      activeTab: "report"
    });
  },

  fetchRuns: async () => {
    try {
      const data = await listRuns();
      set({ runs: data });
    } catch {
      // ignore on startup if offline
    }
  },

  fetchRun: async (id: string) => {
    try {
      if (activeEventSourceCleanup) {
        activeEventSourceCleanup();
        activeEventSourceCleanup = null;
      }
      const run = await getRun(id);
      set({
        activeRunId: id,
        activeRun: run,
        currentRun: run,
        events: run.events || [],
        chatMessages: []
      });

      // If run is still progressing, attach SSE
      const isProgressing = run.status !== "completed" && run.status !== "failed" && run.status !== "cancelled";
      if (isProgressing) {
        const cleanup = subscribeToEvents(
          id,
          (event: RunEventPayload) => {
            get().addEvent(event);
            if (event.event === "run_completed" || event.stage === "done") {
              get().fetchRun(id);
              get().fetchRuns();
            }
          },
          () => {
            get().fetchRun(id);
            get().fetchRuns();
          }
        );
        activeEventSourceCleanup = cleanup;
      }
    } catch (err: any) {
      get().addToast(err?.message || "Failed to load research run", "error");
    }
  },

  startResearch: async (query: string, options: ResearchOptions, docIds?: string[]) => {
    if (activeEventSourceCleanup) {
      activeEventSourceCleanup();
      activeEventSourceCleanup = null;
    }
    set({ isStartingRun: true, events: [], chatMessages: [] });

    try {
      const result = await createRun(query, options, docIds);
      const runId = result.run_id || result.id;
      
      // Fetch initial run
      await get().fetchRun(runId);
      set({ isStartingRun: false, activeTab: "report" });
      get().fetchRuns();

      // Subscribe to SSE events
      const cleanup = subscribeToEvents(
        runId,
        (event: RunEventPayload) => {
          get().addEvent(event);
          if (event.event === "run_completed" || event.stage === "done" || event.stage === "verify") {
            get().fetchRun(runId);
            get().fetchRuns();
          }
        },
        () => {
          get().fetchRun(runId);
          get().fetchRuns();
        }
      );
      activeEventSourceCleanup = cleanup;
    } catch (err: any) {
      set({ isStartingRun: false });
      get().addToast(err?.message || "Failed to start research run", "error");
    }
  }
}));
