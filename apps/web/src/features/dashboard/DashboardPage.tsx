import type { ReactNode } from "react";
import { ArrowUpRight, Building2, FileText, Sparkles, Target } from "lucide-react";
import toast from "react-hot-toast";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-3">
        <KpiCard title="Grant fit score" value="8.6 / 10" sub="Based on your profile + recent calls" icon={<Target className="size-4" />} />
        <KpiCard title="Eligibility checks" value="12" sub="Last 30 days · with rationale" icon={<Sparkles className="size-4" />} />
        <KpiCard title="Proposals generated" value="4" sub="Export-ready drafts" icon={<FileText className="size-4" />} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle>Top opportunities</CardTitle>
            <CardDescription>Ranked recommendations tuned for Indian startup programs.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Opportunity title="DST Seed Support for Deep Tech" meta="₹20L–₹50L · AI/HealthTech · Evidence-heavy" tag="High fit" />
            <Opportunity title="MSME Innovation & Incubation" meta="Due in 12 days · Compliance checklist available" tag="Short window" />
            <Opportunity title="State Startup Policy Incentives" meta="Location matched · Multiple subsidy types" tag="New" />
            <div className="pt-2">
              <Button variant="secondary" onClick={() => toast("Hook this to /app/recommendations.")}>
                View all recommendations <ArrowUpRight className="size-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profile readiness</CardTitle>
            <CardDescription>Improve match quality by completing key fields.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <ReadinessRow label="Company basics" pct={92} icon={<Building2 className="size-4" />} />
            <ReadinessRow label="Financials & traction" pct={66} icon={<Sparkles className="size-4" />} />
            <ReadinessRow label="Compliance documents" pct={40} icon={<FileText className="size-4" />} />
            <div className="mt-4 rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
              <div className="text-xs font-semibold text-slate-900 dark:text-slate-100">Suggested next</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                Add incorporation certificate + last FY turnover for better eligibility accuracy.
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Live activity</CardTitle>
            <CardDescription>What your agents are doing right now.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
              <div className="text-sm font-semibold text-slate-900 dark:text-slate-50">RAG Index</div>
              <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">Ready · 18 sources · 4,120 chunks</div>
            </div>
            <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
              <div className="text-sm font-semibold text-slate-900 dark:text-slate-50">Proposal Job Queue</div>
              <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">Idle · 0 running</div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Loading states</CardTitle>
            <CardDescription>Premium skeletons for fast perceived performance.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-3">
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function KpiCard({ title, value, sub, icon }: { title: string; value: string; sub: string; icon: ReactNode }) {
  return (
    <Card className="p-5 transition hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">{title}</div>
          <div className="mt-2 text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-50">{value}</div>
          <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">{sub}</div>
        </div>
        <div className="inline-flex size-10 items-center justify-center rounded-2xl bg-[var(--accent)]/15 text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30 font-bold">
          <span>{icon}</span>
        </div>
      </div>
    </Card>
  );
}

function Opportunity({ title, meta, tag }: { title: string; meta: string; tag: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
      <div className="min-w-0">
        <div className="truncate text-sm font-semibold text-slate-900 dark:text-slate-50">{title}</div>
        <div className="mt-1 truncate text-xs text-slate-600 dark:text-slate-400">{meta}</div>
      </div>
      <div className="shrink-0 rounded-full bg-[var(--accent)]/15 px-3 py-1 text-xs font-semibold text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30">
        {tag}
      </div>
    </div>
  );
}

function ReadinessRow({ label, pct, icon }: { label: string; pct: number; icon: ReactNode }) {
  return (
    <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-800/70 dark:ring-slate-700">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex size-8 items-center justify-center rounded-2xl bg-[var(--surface)] text-[var(--text-primary)] ring-1 ring-[var(--border)]">
            {icon}
          </span>
          <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">{label}</div>
        </div>
        <div className="text-xs font-medium text-slate-600 dark:text-slate-300">{pct}%</div>
      </div>
      <div className="mt-3 h-2 rounded-full bg-[var(--border)]">
        <div className="h-2 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--text-primary)]" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

