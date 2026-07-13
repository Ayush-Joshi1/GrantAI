export interface SourceResponse {
  grant_name: string | null;
  organization: string | null;
  source_document: string | null;
  page_number: number | null;
}

export interface StartupProfileInput {
  startup_name: string | null;
  startup_description: string | null;
  sector: string | null;
  startup_stage: string | null;
  location: string | null;
  funding_required: string | null;
  founder_profile: string | null;
  additional_context: string | null;
}

export interface SelectedGrantInput {
  grant_id: string | null;
  grant_name: string | null;
  organization: string | null;
  grant_context: string | null;
  source_document: string | null;
}

export type EligibilityStatus =
  | "eligible"
  | "likely_eligible"
  | "not_eligible"
  | "insufficient_information";

export type DeadlineStatus = "known" | "unknown";

export type NotificationType =
  | "funding_action"
  | "deadline_reminder"
  | "general_update";

export type NotificationPriority = "low" | "medium" | "high";

export interface RecommendRequest {
  query?: string | null;
  limit: number;
  startup_profile?: StartupProfileInput | null;
}

export interface RecommendedGrant {
  grant_id: string;
  title: string;
  score: number;
  reason: string;
}

export interface RecommendResponse {
  answer: string;
  sources: SourceResponse[];
  results: RecommendedGrant[];
}

export interface EligibilityCheckRequest {
  grant_id?: string | null;
  startup_profile_id?: string | null;
  answers?: Record<string, string>;
  selected_grant?: SelectedGrantInput | null;
  startup_profile?: StartupProfileInput | null;
  additional_answers?: Record<string, string>;
  additional_context?: string | null;
}

export interface EligibilityCheckResponse {
  eligibility_status: EligibilityStatus;
  answer?: string | null;
  analysis?: string | null;
  reasons: string[];
  missing_requirements: string[];
  recommendations: string[];
  sources: SourceResponse[];
  decision?: "eligible" | "not_eligible" | "unknown" | null;
  confidence?: number | null;
  missing_info: string[];
}

export interface ProposalGenerateRequest {
  grant_id?: string | null;
  startup_profile_id?: string | null;
  notes?: string | null;
  selected_grant?: SelectedGrantInput | null;
  startup_profile?: StartupProfileInput | null;
  proposal_context?: string | null;
}

export interface ProposalGenerateResponse {
  proposal_id?: string | null;
  status?: string | null;
  answer?: string | null;
  executive_summary?: string | null;
  problem_statement?: string | null;
  solution?: string | null;
  implementation_plan?: string | null;
  budget?: string | null;
  timeline?: string | null;
  expected_impact?: string | null;
  cover_letter?: string | null;
  sources: SourceResponse[];
}

export interface DeadlineRequest {
  selected_grant?: SelectedGrantInput | null;
  grant_context?: string | null;
}

export interface DeadlineResponse {
  deadline_status: DeadlineStatus;
  deadline?: string | null;
  days_remaining?: number | null;
  important_dates: string[];
  recommended_action?: string | null;
  answer?: string | null;
  analysis?: string | null;
  sources: SourceResponse[];
}

export interface NotificationRequest {
  selected_grant?: SelectedGrantInput | null;
  grant_context?: string | null;
  deadline_context?: string | null;
  action_context?: string | null;
  notification_preferences?: string | null;
}

export interface NotificationResponse {
  notification_type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;
  answer?: string | null;
  recommended_schedule?: string | null;
  sources: SourceResponse[];
}
