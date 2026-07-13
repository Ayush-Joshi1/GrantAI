import * as React from "react";
import { FileText, Sparkles, Wand2 } from "lucide-react";
import toast from "react-hot-toast";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { grantApi } from "@/services/grantApi";
import type { DeadlineResponse, NotificationResponse, ProposalGenerateResponse, SourceResponse, StartupProfileInput } from "@/types/api";

const defaultStartupProfile: StartupProfileInput = {
  startup_name: "AarogyaAI Labs",
  startup_description: "AI healthcare startup focused on clinic workflow automation.",
  sector: "AI · Healthcare",
  startup_stage: "Pre-seed",
  location: "Bengaluru, Karnataka",
  funding_required: "Seed stage funding",
  founder_profile: "Founder-led healthtech startup with pilot traction.",
  additional_context: "Interested in grants for deep-tech and innovation support."
};

export function ProposalGeneratorPage() {
  const [generating, setGenerating] = React.useState(false);
  const [proposal, setProposal] = React.useState<ProposalGenerateResponse | null>(null);
  const [deadline, setDeadline] = React.useState<DeadlineResponse | null>(null);
  const [notification, setNotification] = React.useState<NotificationResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [deadlineLoading, setDeadlineLoading] = React.useState(false);
  const [notificationLoading, setNotificationLoading] = React.useState(false);
  const [deadlineError, setDeadlineError] = React.useState<string | null>(null);
  const [notificationError, setNotificationError] = React.useState<string | null>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    setProposal(null);
    setDeadline(null);
    setNotification(null);
    setError(null);
    setDeadlineError(null);
    setNotificationError(null);
    toast.loading("Generating draft…", { id: "proposal" });

    try {
      const proposalResponse = await grantApi.generateProposal({
        startup_profile: defaultStartupProfile,
        selected_grant: {
          grant_id: null,
          grant_name: "DST Seed Support for Deep Tech Startups",
          organization: "Department of Science & Technology",
          grant_context: "Grant proposal context for a deep-tech healthcare startup.",
          source_document: null
        },
        proposal_context: "Generate a structured proposal for a healthtech startup seeking deep-tech grant support."
      });

      setProposal(proposalResponse);

      setDeadlineLoading(true);
      try {
        const deadlineResponse = await grantApi.getDeadline({
          selected_grant: {
            grant_id: null,
            grant_name: "DST Seed Support for Deep Tech Startups",
            organization: "Department of Science & Technology",
            grant_context: "Grant proposal context for a deep-tech healthcare startup.",
            source_document: null
          },
          grant_context: "Deadline analysis for the selected grant."
        });
        setDeadline(deadlineResponse);
      } catch (deadlineErr) {
        setDeadlineError(deadlineErr instanceof Error ? deadlineErr.message : "Deadline analysis failed.");
      } finally {
        setDeadlineLoading(false);
      }

      setNotificationLoading(true);
      try {
        const notificationResponse = await grantApi.getNotifications({
          selected_grant: {
            grant_id: null,
            grant_name: "DST Seed Support for Deep Tech Startups",
            organization: "Department of Science & Technology",
            grant_context: "Grant proposal context for a deep-tech healthcare startup.",
            source_document: null
          },
          grant_context: "Notification guidance for the selected grant.",
          deadline_context: deadline ? undefined : undefined,
          action_context: "Generate proposal draft.",
          notification_preferences: "Email and in-app reminders"
        });
        setNotification(notificationResponse);
      } catch (notificationErr) {
        setNotificationError(notificationErr instanceof Error ? notificationErr.message : "Notification generation failed.");
      } finally {
        setNotificationLoading(false);
      }

      toast.success("Draft ready.", { id: "proposal" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Draft generation failed.");
      toast.error("Draft generation failed.", { id: "proposal" });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-50">Proposal Generator</div>
          <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Structured, compliant drafts with grounded citations (Granite + RAG ready).
          </div>
        </div>
        <Button isLoading={generating} disabled={generating} onClick={() => { void handleGenerate(); }}>
          <Wand2 className="size-4" />
          Generate draft
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader>
            <CardTitle>Inputs</CardTitle>
            <CardDescription>High-signal fields for better outcomes.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <InputRow label="Grant / scheme" value="DST Seed Support for Deep Tech Startups" />
            <InputRow label="Startup" value="AarogyaAI Labs (Bengaluru)" />
            <InputRow label="Stage" value="Pre-seed · Pilot deployments" />
            <InputRow label="Primary documents" value="Pitch deck, Incorporation, Financials" />
            <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
              <div className="flex items-center gap-2 text-xs font-semibold text-[var(--text-primary)]">
                <Sparkles className="size-4 text-[var(--accent)]" /> Assistant guidance
              </div>
              <div className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                We’ll ask for missing evidence (turnover, IP, team, milestones) before drafting.
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Draft preview</CardTitle>
            <CardDescription>Premium formatting, ready for export.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {generating ? (
              <div className="space-y-3">
                <Skeleton className="h-10" />
                <Skeleton className="h-24" />
                <Skeleton className="h-24" />
                <Skeleton className="h-24" />
              </div>
            ) : error ? (
              <div className="rounded-[20px] bg-rose-50 p-4 text-sm text-rose-700 ring-1 ring-rose-200 dark:bg-rose-950/20 dark:text-rose-200 dark:ring-rose-900/40">
                {error}
              </div>
            ) : proposal ? (
              <div className="space-y-3">
                {renderProposalSection("Executive summary", proposal.executive_summary)}
                {renderProposalSection("Problem statement", proposal.problem_statement)}
                {renderProposalSection("Solution", proposal.solution)}
                {renderProposalSection("Implementation plan", proposal.implementation_plan)}
                {renderProposalSection("Budget", proposal.budget)}
                {renderProposalSection("Timeline", proposal.timeline)}
                {renderProposalSection("Expected impact", proposal.expected_impact)}
                {renderProposalSection("Cover letter", proposal.cover_letter)}
                {proposal.answer ? <Section title="Assistant summary" body={proposal.answer} /> : null}
                {proposal.sources.length ? <SourcesList sources={proposal.sources} /> : null}
                <div className="flex flex-wrap gap-2 pt-2">
                  <Button variant="secondary" onClick={() => toast("Export will generate PDF/DOCX via backend worker.")}>
                    <FileText className="size-4" />
                    Export
                  </Button>
                  <Button onClick={() => toast("Compliance review will run a checklist agent + citations.")}>
                    <Sparkles className="size-4" />
                    Run compliance check
                  </Button>
                </div>
              </div>
            ) : (
              <div className="rounded-[20px] bg-slate-50 p-4 text-sm text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">
                Generate a draft to receive proposal content from the backend.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Deadline & reminders</CardTitle>
          <CardDescription>Workflow details returned by the backend.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {deadlineLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : deadlineError ? (
            <div className="rounded-[20px] bg-rose-50 p-4 text-sm text-rose-700 ring-1 ring-rose-200 dark:bg-rose-950/20 dark:text-rose-200 dark:ring-rose-900/40">{deadlineError}</div>
          ) : deadline ? (
            <div className="space-y-3">
              <Section title="Deadline" body={deadline.deadline ?? deadline.answer ?? "No deadline returned."} />
              {deadline.days_remaining !== null && deadline.days_remaining !== undefined ? (
                <Section title="Days remaining" body={String(deadline.days_remaining)} />
              ) : null}
              {deadline.important_dates.length ? (
                <Section title="Important dates" body={deadline.important_dates.join(" • ")} />
              ) : null}
              {deadline.recommended_action ? <Section title="Recommended action" body={deadline.recommended_action} /> : null}
              {deadline.sources.length ? <SourcesList sources={deadline.sources} /> : <div className="rounded-[20px] bg-slate-50 p-3 text-sm text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">No sources were returned for this deadline response.</div>}
            </div>
          ) : (
            <div className="rounded-[20px] bg-slate-50 p-4 text-sm text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">
              Deadline analysis will appear after the proposal draft is generated.
            </div>
          )}

          {notificationLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : notificationError ? (
            <div className="rounded-[20px] bg-rose-50 p-4 text-sm text-rose-700 ring-1 ring-rose-200 dark:bg-rose-950/20 dark:text-rose-200 dark:ring-rose-900/40">{notificationError}</div>
          ) : notification ? (
            <div className="space-y-3">
              <Section title="Reminder" body={notification.title} />
              <Section title="Priority" body={notification.priority} />
              <Section title="Message" body={notification.message || notification.answer || "No message returned."} />
              {notification.recommended_schedule ? <Section title="Suggested action" body={notification.recommended_schedule} /> : null}
              {notification.sources.length ? <SourcesList sources={notification.sources} /> : <div className="rounded-[20px] bg-slate-50 p-3 text-sm text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">No sources were returned for this notification response.</div>}
            </div>
          ) : (
            <div className="rounded-[20px] bg-slate-50 p-4 text-sm text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">
              Notification guidance will appear after the proposal draft is generated.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function InputRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-[16px] bg-[var(--surface-section)] px-4 py-3 ring-1 ring-[var(--border)]">
      <div className="text-xs text-[var(--text-muted)]">{label}</div>
      <div className="text-sm font-semibold text-[var(--text-primary)]">{value}</div>
    </div>
  );
}

function renderProposalSection(title: string, body?: string | null) {
  if (!body) return null;
  return <Section title={title} body={body} />;
}

function Section({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-[20px] bg-[var(--surface-section)] p-4 ring-1 ring-[var(--border)]">
      <div className="text-sm font-semibold text-[var(--text-primary)]">{title}</div>
      <div className="mt-2 text-sm leading-relaxed text-[var(--text-secondary)]">{body}</div>
    </div>
  );
}

function SourcesList({ sources }: { sources: SourceResponse[] }) {
  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">Sources</div>
      {sources.map((source, index) => (
        <div key={`${source.grant_name ?? "source"}-${index}`} className="rounded-[16px] bg-[var(--surface-section)] p-3 text-sm text-[var(--text-secondary)] ring-1 ring-[var(--border)]">
          <div className="font-medium text-[var(--text-primary)]">{source.grant_name ?? "Grant source"}</div>
          <div className="mt-1 text-xs text-[var(--text-muted)]">
            {source.organization ?? "Organization not provided"}
            {source.source_document ? ` · ${source.source_document}` : ""}
            {source.page_number ? ` · Page ${source.page_number}` : ""}
          </div>
        </div>
      ))}
    </div>
  );
}

