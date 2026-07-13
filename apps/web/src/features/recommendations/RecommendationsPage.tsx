import * as React from "react";
import { Filter, Sparkles } from "lucide-react";
import toast from "react-hot-toast";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { grantApi } from "@/services/grantApi";
import type { EligibilityCheckResponse, SourceResponse, StartupProfileInput } from "@/types/api";

type Grant = {
  title: string;
  ministry: string;
  amount: string;
  deadline: string;
  tags: string[];
  fit: "High" | "Medium";
  reason: string;
  score: number;
};

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

export function RecommendationsPage() {
  const [open, setOpen] = React.useState(false);
  const [selected, setSelected] = React.useState<Grant | null>(null);
  const [grants, setGrants] = React.useState<Grant[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [recommendationSummary, setRecommendationSummary] = React.useState("");
  const [recommendationSources, setRecommendationSources] = React.useState<SourceResponse[]>([]);
  const [eligibilityLoading, setEligibilityLoading] = React.useState(false);
  const [eligibilityError, setEligibilityError] = React.useState<string | null>(null);
  const [eligibilityResult, setEligibilityResult] = React.useState<EligibilityCheckResponse | null>(null);

  const loadRecommendations = React.useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await grantApi.recommend({
        query: "Recommend suitable grants for an AI healthcare startup in Bengaluru",
        limit: 5,
        startup_profile: defaultStartupProfile
      });

      setRecommendationSummary(response.answer);
      setRecommendationSources(response.sources);
      setGrants(
        response.results.map((result) => ({
          title: result.title,
          ministry: result.reason,
          amount: `Score ${result.score.toFixed(2)}`,
          deadline: "See recommendation details",
          tags: ["AI", "Grant recommendation"],
          fit: result.score >= 0.7 ? "High" : "Medium",
          reason: result.reason,
          score: result.score
        }))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load recommendations right now.");
      setGrants([]);
      setRecommendationSummary("");
      setRecommendationSources([]);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void loadRecommendations();
  }, [loadRecommendations]);

  const handleOpenGrant = (grant: Grant) => {
    setSelected(grant);
    setEligibilityError(null);
    setEligibilityResult(null);
    setOpen(true);
  };

  const handleCheckEligibility = async () => {
    if (!selected) return;

    setEligibilityLoading(true);
    setEligibilityError(null);
    setEligibilityResult(null);

    try {
      const response = await grantApi.checkEligibility({
        startup_profile: defaultStartupProfile,
        selected_grant: {
          grant_id: null,
          grant_name: selected.title,
          organization: selected.ministry,
          grant_context: selected.reason,
          source_document: null
        }
      });
      setEligibilityResult(response);
    } catch (err) {
      setEligibilityError(err instanceof Error ? err.message : "Eligibility check failed.");
    } finally {
      setEligibilityLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-50">Recommendations</div>
          <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            AI-ranked grants aligned to your profile + government requirements.
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={() => { void loadRecommendations(); toast.success("Refreshing recommendations"); }} disabled={loading} isLoading={loading}>
            <Filter className="size-4" />
            Refresh
          </Button>
          <Button onClick={() => { void loadRecommendations(); toast.success("Recommendations reloaded"); }} disabled={loading} isLoading={loading}>
            <Sparkles className="size-4" />
            Refresh ranking
          </Button>
        </div>
      </div>

      {recommendationSummary ? (
        <Card>
          <CardHeader>
            <CardTitle>Recommendation summary</CardTitle>
            <CardDescription>Response from the backend recommendation service.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-[20px] bg-slate-50 p-4 text-sm text-slate-700 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">
              {recommendationSummary}
            </div>
            {recommendationSources.length ? (
              <div className="space-y-2">
                <div className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Sources</div>
                {recommendationSources.map((source, index) => (
                  <div key={`${source.grant_name ?? "source"}-${index}`} className="rounded-[16px] bg-slate-50 p-3 text-sm text-slate-700 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:text-slate-300 dark:ring-slate-700">
                    <div className="font-medium text-slate-900 dark:text-slate-100">{source.grant_name ?? "Grant source"}</div>
                    <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">
                      {source.organization ?? "Organization not provided"}
                      {source.source_document ? ` · ${source.source_document}` : ""}
                      {source.page_number ? ` · Page ${source.page_number}` : ""}
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      {loading ? (
        <div className="grid gap-4 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={`recommendation-skeleton-${index}`} className="h-40" />
          ))}
        </div>
      ) : error ? (
        <Card>
          <CardContent className="py-6 text-sm text-slate-600 dark:text-slate-300">{error}</CardContent>
        </Card>
      ) : grants.length === 0 ? (
        <Card>
          <CardContent className="py-6 text-sm text-slate-600 dark:text-slate-300">No grant recommendations were returned. Try refreshing to fetch the latest ranking.</CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          {grants.map((g) => (
            <button key={g.title} type="button" className="text-left" onClick={() => handleOpenGrant(g)}>
              <Card className="h-full p-5 transition hover:-translate-y-0.5 hover:shadow-[0_18px_45px_rgba(15,23,42,0.08)]">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-slate-900 dark:text-slate-50">{g.title}</div>
                    <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">{g.ministry}</div>
                  </div>
                  <FitPill fit={g.fit} />
                </div>

                <div className="mt-4 grid gap-2">
                  <Meta label="Score" value={g.score.toFixed(2)} />
                  <Meta label="Reason" value={g.reason} />
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {g.tags.map((t) => (
                    <span key={t} className="rounded-full bg-[var(--accent)]/15 px-2.5 py-1 text-[11px] font-semibold text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30">
                      {t}
                    </span>
                  ))}
                </div>
              </Card>
            </button>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Why these recommendations?</CardTitle>
          <CardDescription>Signals used by the ranking model (transparent by design).</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <Signal title="Profile fit" desc="Sector + stage + location + incorporation date." />
          <Signal title="Grant constraints" desc="Deadlines, documents, compliance requirements." />
          <Signal title="RAG evidence" desc="Official guideline citations support each decision." />
        </CardContent>
      </Card>

      <Modal open={open} title={selected?.title ?? "Grant details"} description={selected ? `${selected.ministry}` : undefined} onClose={() => { setOpen(false); setSelected(null); setEligibilityError(null); setEligibilityResult(null); }} footer={<><Button variant="secondary" onClick={() => { setOpen(false); setSelected(null); setEligibilityError(null); setEligibilityResult(null); }}>Close</Button><Button isLoading={eligibilityLoading} disabled={eligibilityLoading} onClick={() => { void handleCheckEligibility(); }}>Check eligibility</Button></>}>
        {selected ? (
          <div className="space-y-3 text-sm text-slate-700 dark:text-slate-200">
            <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
              <div className="text-xs font-semibold text-slate-900 dark:text-slate-50">Why it fits</div>
              <div className="mt-2 text-sm text-slate-600 dark:text-slate-300">{selected.reason}</div>
            </div>
            <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
              <div className="text-xs font-semibold text-slate-900 dark:text-slate-50">Eligibility result</div>
              {eligibilityLoading ? (
                <div className="mt-3 space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              ) : eligibilityError ? (
                <div className="mt-2 text-sm text-rose-600 dark:text-rose-300">{eligibilityError}</div>
              ) : eligibilityResult ? (
                <div className="mt-2 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                  <div className="font-medium text-slate-900 dark:text-slate-100">{eligibilityResult.eligibility_status}</div>
                  {eligibilityResult.answer ? <div>{eligibilityResult.answer}</div> : null}
                  {eligibilityResult.reasons.length ? (
                    <ul className="list-disc space-y-1 pl-5">
                      {eligibilityResult.reasons.map((reason) => (
                        <li key={reason}>{reason}</li>
                      ))}
                    </ul>
                  ) : null}
                  {eligibilityResult.sources.length ? (
                    <div className="space-y-2">
                      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Sources</div>
                      {eligibilityResult.sources.map((source, index) => (
                        <div key={`${source.grant_name ?? "source"}-${index}`} className="rounded-[16px] bg-white/70 p-2 text-xs text-slate-600 ring-1 ring-slate-200 dark:bg-slate-900/50 dark:text-slate-300 dark:ring-slate-700">
                          <div className="font-medium text-slate-900 dark:text-slate-100">{source.grant_name ?? "Grant source"}</div>
                          <div className="mt-1">
                            {source.organization ?? "Organization not provided"}
                            {source.source_document ? ` · ${source.source_document}` : ""}
                            {source.page_number ? ` · Page ${source.page_number}` : ""}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : (
                <div className="mt-2 text-sm text-slate-600 dark:text-slate-300">The backend eligibility response will appear here after you run the check.</div>
              )}
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}

function FitPill({ fit }: { fit: "High" | "Medium" }) {
  return (
    <span className="shrink-0 rounded-full bg-[var(--accent)]/15 px-3 py-1 text-xs font-semibold text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30">
      {fit} fit
    </span>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-[16px] bg-[var(--surface-section)] px-3 py-2 ring-1 ring-[var(--border)]">
      <div className="text-xs text-[var(--text-muted)]">{label}</div>
      <div className="text-xs font-semibold text-[var(--text-primary)]">{value}</div>
    </div>
  );
}

function Signal({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-[20px] bg-[var(--surface-section)] p-4 ring-1 ring-[var(--border)]">
      <div className="text-sm font-semibold text-[var(--text-primary)]">{title}</div>
      <div className="mt-1 text-sm text-[var(--text-secondary)]">{desc}</div>
    </div>
  );
}

