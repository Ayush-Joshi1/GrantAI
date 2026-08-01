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

function delay<T>(value: T, ms = 250): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

const fallback = {
  recommend(payload: RecommendRequest): Promise<RecommendResponse> {
    return delay({
      answer: "Demo grant recommendations for a Bengaluru AI healthcare startup.",
      sources: [
        {
          grant_name: "Startup India Scheme Guidelines",
          organization: "Department for Promotion of Industry and Internal Trade",
          source_document: "Startup India portal",
          page_number: 6
        }
      ],
      results: [
        {
          grant_id: "dst-seed-deeptech",
          title: "DST Seed Support for Deep Tech",
          score: 0.92,
          reason: "Strong alignment to AI healthcare, innovation potential, and Karnataka location."
        },
        {
          grant_id: "msme-innovation-incubation",
          title: "MSME Innovation & Incubation",
          score: 0.84,
          reason: "Great fit for early-stage startups with product-market validation."
        },
        {
          grant_id: "state-startup-policy-incentives",
          title: "State Startup Policy Incentives",
          score: 0.78,
          reason: "Local subsidy and support programs matched to Bengaluru founders."
        }
      ]
    });
  },

  checkEligibility(): Promise<EligibilityCheckResponse> {
    return delay({
      eligibility_status: "likely_eligible",
      answer: "Based on the provided startup profile, this grant appears likely eligible with a few documentation gaps.",
      analysis: "The startup fits the sector, stage, and regional requirements. Missing items are primarily financial and registration documents.",
      reasons: ["Sector match", "Startup stage aligns with scheme criteria", "Location is within a supported state"],
      missing_requirements: ["Udyam registration", "audited FY statements"],
      recommendations: ["Complete Udyam registration", "Upload latest audited financials"],
      sources: [
        {
          grant_name: "DST Seed Support Terms",
          organization: "Department of Science & Technology",
          source_document: null,
          page_number: null
        }
      ],
      decision: "eligible",
      confidence: 0.82,
      missing_info: ["turnover details", "patent status"]
    });
  },

  generateProposal(): Promise<ProposalGenerateResponse> {
    return delay({
      proposal_id: "demo-proposal-001",
      status: "ready",
      answer: "A draft proposal has been generated for your AI healthcare startup. Review the sections below for customization.",
      executive_summary: "AarogyaAI Labs is building AI workflow automation for clinics to improve patient care and operational efficiency.",
      problem_statement: "India’s primary healthcare providers face manual documentation, delayed triage, and limited clinical decision support.",
      solution: "An AI-powered platform that automates intake, triage, and reporting while ensuring regulatory compliance.",
      implementation_plan: "Phase 1: pilot with 2 clinics in Bengaluru. Phase 2: integrate clinical workflows and evidence-based models.",
      budget: "₹45 lakhs total: ₹18L product development, ₹12L pilot operations, ₹10L regulatory compliance, ₹5L contingency.",
      timeline: "Month 1-3: pilot deployment, Month 4-6: validation and documentation, Month 7-9: scale-up.",
      expected_impact: "Improve clinic efficiency by 30%, reduce patient wait time, and enable measurable outcomes for healthtech innovation.",
      cover_letter: "We are excited to apply for DST Seed Support with a focus on scalable AI solutions for Indian healthcare.",
      sources: [
        {
          grant_name: "DST Seed Support Application Guide",
          organization: "Department of Science & Technology",
          source_document: "Grant guidelines",
          page_number: 10
        }
      ]
    });
  },

  getDeadline(): Promise<DeadlineResponse> {
    return delay({
      deadline_status: "known",
      deadline: "2026-09-30",
      days_remaining: 62,
      important_dates: ["EOI due 2026-09-15", "Final submission 2026-09-30"],
      recommended_action: "Finalize the proposal and supporting documents two weeks before the deadline.",
      answer: "The deadline is confirmed for September 30, 2026. Start document preparation now.",
      analysis: "A proactive timetable is recommended to avoid last-minute compliance checks.",
      sources: [
        {
          grant_name: "DST Seed Support Timeline",
          organization: "Department of Science & Technology",
          source_document: "Official timeline document",
          page_number: 2
        }
      ]
    });
  },

  getNotifications(): Promise<NotificationResponse> {
    return delay({
      notification_type: "deadline_reminder",
      priority: "high",
      title: "Proposal due in 62 days",
      message: "Begin your final review and upload essential documents to keep the submission on schedule.",
      answer: "Set reminders for compliance review, document upload, and executive summary approval.",
      recommended_schedule: "Review draft in 10 days, collect attachments in 20 days.",
      sources: [
        {
          grant_name: "Submission checklist",
          organization: "Grant support team",
          source_document: null,
          page_number: null
        }
      ]
    });
  },

  chatTurn(payload: ChatTurnRequest): Promise<ChatTurnResponse> {
    const reply = payload.message.includes("eligibility")
      ? "This startup is likely eligible for relevant AI healthcare grants. Upload your documents to improve the assessment."
      : payload.message.includes("proposal")
      ? "I can generate a draft proposal section for your grant application. Share more details about your team and timeline."
      : "I’m ready to help find grants, explain eligibility, and draft proposal sections for your AI healthcare startup.";

    return delay({
      session_id: payload.session_id ?? "demo-session",
      reply
    });
  }
};

export const grantApi = {
  async recommend(payload: RecommendRequest) {
    try {
      return await postJson<RecommendResponse>("/recommend", payload);
    } catch (error) {
      console.warn("Recommend API failed, using fallback", error);
      return fallback.recommend(payload);
    }
  },

  async checkEligibility(payload: EligibilityCheckRequest) {
    try {
      return await postJson<EligibilityCheckResponse>("/eligibility/check", payload);
    } catch (error) {
      console.warn("Eligibility API failed, using fallback", error);
      return fallback.checkEligibility();
    }
  },

  async generateProposal(payload: ProposalGenerateRequest) {
    try {
      return await postJson<ProposalGenerateResponse>("/proposal/generate", payload);
    } catch (error) {
      console.warn("Proposal API failed, using fallback", error);
      return fallback.generateProposal();
    }
  },

  async getDeadline(payload: DeadlineRequest) {
    try {
      return await postJson<DeadlineResponse>("/deadline", payload);
    } catch (error) {
      console.warn("Deadline API failed, using fallback", error);
      return fallback.getDeadline();
    }
  },

  async getNotifications(payload: NotificationRequest) {
    try {
      return await postJson<NotificationResponse>("/notifications", payload);
    } catch (error) {
      console.warn("Notifications API failed, using fallback", error);
      return fallback.getNotifications();
    }
  },

  async chatTurn(payload: ChatTurnRequest) {
    try {
      return await postJson<ChatTurnResponse>("/chat/turn", payload);
    } catch (error) {
      console.warn("Chat turn API failed, using fallback", error);
      return fallback.chatTurn(payload);
    }
  }
};
