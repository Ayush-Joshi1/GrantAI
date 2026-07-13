import toast from "react-hot-toast";
import { Building2, Sparkles } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export function ProfilePage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-50">Startup Profile</div>
          <div className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Your profile drives eligibility accuracy and recommendation quality.
          </div>
        </div>
        <Button variant="secondary" onClick={() => toast.success("Saved (demo). Wire to backend /v1/me/profile later.")}>
          Save changes
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_420px]">
        <Card>
          <CardHeader>
            <CardTitle>Company details</CardTitle>
            <CardDescription>High-signal fields used in eligibility and proposal drafting.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            <Field label="Company name" value="AarogyaAI Labs" />
            <Field label="Location" value="Bengaluru, Karnataka" />
            <Field label="Incorporation date" value="2024-02-11" />
            <Field label="Sector" value="AI · Healthcare" />
            <Field label="Stage" value="Pre-seed" />
            <Field label="Annual revenue (FY)" value="₹0.8 Cr" />
          </CardContent>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-[var(--accent)]/15 text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30 font-bold">
              <Building2 className="size-5" />
            </div>
            <div>
              <div className="text-sm font-semibold tracking-tight text-slate-900 dark:text-slate-50">Readiness insights</div>
              <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">What to add for better outcomes.</div>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <Insight title="Add document evidence" desc="Upload incorporation certificate + audited statements for higher confidence." />
            <Insight title="Team credentials" desc="Founders’ profiles and patents improve deep-tech grant fit." />
            <Button className="w-full" onClick={() => toast("This will open an upload modal later.")}>
              <Sparkles className="size-4" />
              Improve profile quality
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[16px] bg-[var(--surface-section)] px-4 py-3 ring-1 ring-[var(--border)]">
      <div className="text-xs text-[var(--text-muted)]">{label}</div>
      <div className="mt-1 text-sm font-semibold text-[var(--text-primary)]">{value}</div>
    </div>
  );
}

function Insight({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-[20px] bg-[var(--surface-section)] p-4 ring-1 ring-[var(--border)]">
      <div className="text-sm font-semibold text-[var(--text-primary)]">{title}</div>
      <div className="mt-1 text-sm text-[var(--text-secondary)]">{desc}</div>
    </div>
  );
}

