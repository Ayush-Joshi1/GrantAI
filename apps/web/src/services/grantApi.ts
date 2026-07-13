import type {
  DeadlineRequest,
  DeadlineResponse,
  EligibilityCheckRequest,
  EligibilityCheckResponse,
  NotificationRequest,
  NotificationResponse,
  ProposalGenerateRequest,
  ProposalGenerateResponse,
  RecommendRequest,
  RecommendResponse
} from "@/types/api";
import { postJson } from "./apiClient";

export interface ChatTurnRequest {
  session_id?: string | null;
  message: string;
}

export interface ChatTurnResponse {
  session_id: string;
  reply: string;
}

export const grantApi = {
  recommend(payload: RecommendRequest) {
    return postJson<RecommendResponse>("/recommend", payload);
  },

  checkEligibility(payload: EligibilityCheckRequest) {
    return postJson<EligibilityCheckResponse>("/eligibility/check", payload);
  },

  generateProposal(payload: ProposalGenerateRequest) {
    return postJson<ProposalGenerateResponse>("/proposal/generate", payload);
  },

  getDeadline(payload: DeadlineRequest) {
    return postJson<DeadlineResponse>("/deadline", payload);
  },

  getNotifications(payload: NotificationRequest) {
    return postJson<NotificationResponse>("/notifications", payload);
  },

  chatTurn(payload: ChatTurnRequest) {
    return postJson<ChatTurnResponse>("/chat/turn", payload);
  }
};
