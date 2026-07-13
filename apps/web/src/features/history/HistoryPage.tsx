import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";

const items = [
  {
    title: "Generated proposal draft",
    meta: "DST Seed Support · 14 min ago",
    detail: "Executive summary, approach, milestones, budget notes."
  },
  {
    title: "Eligibility check",
    meta: "MSME Innovation · Yesterday",
    detail: "Eligible (provisional) · Missing: turnover proof, MSME Udyam."
  },
  {
    title: "Saved recommendation list",
    meta: "State incentives · 3 days ago",
    detail: "Shortlisted 6 schemes for Karnataka."
  }
];

export function HistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-50">History</div>
        <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          Traceability for decisions, drafts, and tool calls (audit-ready).
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent activity</CardTitle>
          <CardDescription>Everything your team did inside Grant Agent.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {items.map((it) => (
            <div key={it.title} className="flex items-start justify-between gap-3 rounded-[20px] bg-[var(--surface-section)] p-4 ring-1 ring-[var(--border)]">
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-[var(--text-primary)]">{it.title}</div>
                <div className="mt-1 text-xs text-[var(--text-secondary)]">{it.detail}</div>
              </div>
              <div className="shrink-0 text-xs text-[var(--text-muted)]">{it.meta}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

