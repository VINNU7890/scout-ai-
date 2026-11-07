export type StageName =
  | "init"
  | "plan"
  | "web_research"
  | "doc_research"
  | "analyze"
  | "write"
  | "verify"
  | "done";

export type RunStatus =
  | "queued"
  | "planning"
  | "researching"
  | "analyzing"
  | "writing"
  | "verifying"
  | "completed"
  | "failed"
  | "cancelled";

export interface Finding {
  entity: string;
  aspect: string;
  claim: string;
  evidence_quote: string;
  source_url?: string;
  doc_name?: string;
  page?: number;
  source_type: "web" | "doc";
  retrieved_at: string;
  confidence: "low" | "med" | "high";
}

export interface SourceItem {
  id: number;
  title: string;
  url?: string;
  doc_name?: string;
  page?: number;
  domain?: string;
  source_type: "web" | "doc";
  retrieved_at: string;
  supported_claims: string[];
}

export interface CompetitorProfile {
  entity: string;
  strengths: string[];
  weaknesses: string[];
  positioning: string;
  pricing_notes: string;
  trust_signals: string[];
  gtm_tactics: string[];
  aspect_scores: Record<string, number>;
  aspect_rationales: Record<string, string>;
}

export interface GtmAction {
  priority: "High" | "Medium" | "Low";
  title: string;
  action: string;
  rationale_and_evidence: string;
}

export interface SWOTAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface VerificationIssue {
  claim: string;
  source_ref: string;
  reason: string;
  severity: "warning" | "unsupported";
}

export interface VerificationResult {
  passed: boolean;
  issues: VerificationIssue[];
  summary: string;
}

export interface Report {
  title: string;
  executive_summary: string;
  key_takeaways: string[];
  comparison_table: Record<string, Record<string, string>>;
  comparison_matrix?: Record<string, Record<string, string>>;
  profiles: CompetitorProfile[];
  competitor_profiles?: CompetitorProfile[];
  swot: SWOTAnalysis;
  gaps_and_opportunities: string[];
  recommended_gtm_actions: GtmAction[];
  methodology_and_limitations: string;
  sources: SourceItem[];
  markdown_content: string;
  raw_markdown?: string;
  findings?: Finding[];
  warnings?: string[];
}

export interface ResearchPlan {
  entities: string[];
  aspects: string[];
  sub_questions: Record<string, string[]>;
  assumptions: string[];
}

export interface ResearchOptions {
  depth: "quick" | "standard" | "deep";
  max_sources_per_entity?: number;
  include_docs?: boolean;
  include_internal_docs?: boolean;
  focus_areas: string[];
  competitors?: string[];
}

export interface RunEventPayload {
  id: number;
  run_id: string;
  event: string;
  stage: StageName;
  message: string;
  data?: any;
  timestamp: string;
}

export interface RunResponse {
  id: string;
  run_id: string;
  query: string;
  status: RunStatus;
  options: ResearchOptions;
  plan?: ResearchPlan;
  report?: Report;
  findings: Finding[];
  sources: SourceItem[];
  events?: RunEventPayload[];
  verification?: VerificationResult;
  error?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface RunListItem {
  id: string;
  query: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface UploadedDocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  chunk_count: number;
  created_at: string;
}

export type DocumentUploadResponse = UploadedDocumentItem;

export interface HealthResponse {
  status: string;
  gemini_configured?: boolean;
  gemini_model?: string;
  search_provider?: string;
  demo_mode?: boolean;
}
