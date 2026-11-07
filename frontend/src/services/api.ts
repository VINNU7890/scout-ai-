import {
  HealthResponse,
  ResearchOptions,
  RunEventPayload,
  RunListItem,
  RunResponse,
  SourceItem,
  UploadedDocumentItem,
} from "../types";

const API_BASE = "/api";

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export const getHealth = checkHealth;

export async function createRun(
  query: string,
  options: Partial<ResearchOptions> = {},
  documentIds: string[] = []
): Promise<{ run_id: string; id: string }> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      options,
      document_ids: documentIds,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || "Failed to start research run");
  }
  const data = await res.json();
  return { ...data, id: data.run_id };
}

export async function getRun(runId: string): Promise<RunResponse> {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  if (!res.ok) throw new Error(`Run ${runId} not found`);
  const data = await res.json();
  const normalized: RunResponse = {
    ...data,
    id: data.run_id || data.id,
    error: data.error_message || data.error,
  };
  if (normalized.report) {
    normalized.report.raw_markdown = normalized.report.markdown_content;
    normalized.report.comparison_matrix = normalized.report.comparison_table;
    normalized.report.competitor_profiles = normalized.report.profiles;
  }
  return normalized;
}

export async function listRuns(): Promise<RunListItem[]> {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error("Failed to load past research runs");
  return res.json();
}

export async function cancelRun(runId: string): Promise<void> {
  await fetch(`${API_BASE}/runs/${runId}/cancel`, { method: "POST" });
}

export async function deleteRun(runId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/runs/${runId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete run");
}

export async function askQuestion(
  runId: string,
  question: string
): Promise<{
  answer: string;
  citations: SourceItem[];
  follow_up_suggestions: string[];
}> {
  const res = await fetch(`${API_BASE}/runs/${runId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || "Failed to get answer");
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<UploadedDocumentItem> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || "Document upload failed");
  }
  return res.json();
}

export async function listDocuments(): Promise<UploadedDocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("Failed to list documents");
  return res.json();
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${docId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete document");
}

export async function exportReport(
  runId: string,
  format: "markdown" | "pdf" | "docx"
): Promise<void> {
  const fmt = format === "markdown" ? "md" : format;
  const res = await fetch(`${API_BASE}/runs/${runId}/export?format=${fmt}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `Failed to export ${format}`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const ext = format === "markdown" ? "md" : format;
  a.download = `scoutai_report_${runId}.${ext}`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export function subscribeToStream(
  runId: string,
  onEvent: (event: RunEventPayload) => void,
  onFinish?: (status: string) => void,
  onError?: (err: Error) => void,
  lastEventId?: number
): () => void {
  let url = `${API_BASE}/runs/${runId}/stream`;
  if (lastEventId) {
    url += `?last_id=${lastEventId}`;
  }

  const eventSource = new EventSource(url);

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
    } catch (err) {
      console.warn("Could not parse SSE message", err);
    }
  };

  const registerCustomEvent = (name: string) => {
    eventSource.addEventListener(name, (e: any) => {
      try {
        const data = JSON.parse(e.data);
        if (name === "run_completed" || name === "completed") {
          onFinish?.("completed");
          eventSource.close();
        } else if (name === "run_cancelled" || name === "cancelled") {
          onFinish?.("cancelled");
          eventSource.close();
        } else if (name === "error" || name === "failed") {
          onFinish?.("failed");
          eventSource.close();
        } else {
          onEvent(data);
        }
      } catch (err) {
        console.warn(`Error in event ${name}`, err);
      }
    });
  };

  [
    "run_started",
    "node_started",
    "step",
    "finding_added",
    "node_finished",
    "warning",
    "error",
    "report_ready",
    "run_completed",
    "run_cancelled",
    "completed",
    "cancelled",
    "failed",
  ].forEach(registerCustomEvent);

  eventSource.onerror = (e) => {
    console.warn("SSE connection notice", e);
    onError?.(new Error("SSE connection error"));
  };

  return () => {
    eventSource.close();
  };
}

export const subscribeToEvents = subscribeToStream;
