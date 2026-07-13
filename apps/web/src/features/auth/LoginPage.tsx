import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Lock, Mail, Sparkles } from "lucide-react";
import toast from "react-hot-toast";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { cn } from "@/utils/cn";

export function LoginPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = React.useState(false);

  return (
    <div className="min-h-dvh bg-[var(--surface-secondary)] text-[var(--text-primary)] transition-colors">
      <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 h-[520px] w-[820px] -translate-x-1/2 rounded-full bg-gradient-to-r from-[#5BA8A0]/20 via-[#F4B06A]/10 to-[#5BA8A0]/10 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(15,23,42,0.05),transparent_60%)] dark:bg-[radial-gradient(circle_at_top,rgba(148,163,184,0.08),transparent_60%)]" />
      </div>

      <header className="relative mx-auto max-w-6xl px-6 py-6">
        <Link to="/" className="inline-flex items-center gap-2 text-sm text-slate-700 transition hover:text-slate-900 dark:text-slate-300 dark:hover:text-slate-50">
          <span className="inline-flex size-9 items-center justify-center rounded-2xl bg-[var(--surface)] ring-1 ring-[var(--border)] shadow-sm">
            <Sparkles className="size-4" />
          </span>
          Back to landing
        </Link>
      </header>

      <main className="relative mx-auto grid max-w-6xl px-6 pb-16 pt-6 lg:grid-cols-2 lg:items-center lg:gap-10">
        <div className="hidden lg:block">
          <h1 className="text-balance text-4xl font-semibold tracking-tight">
            Sign in to your grant workspace.
          </h1>
          <p className="mt-4 max-w-md text-pretty text-slate-600 dark:text-slate-300">
            Premium experience, audit-ready tool calls, and structured proposal workflows — designed for real teams.
          </p>

          <div className="mt-8 grid max-w-md gap-3">
            <div className="rounded-[24px] border border-slate-200/80 bg-white/80 p-4 shadow-[0_16px_50px_rgba(15,23,42,0.06)] backdrop-blur-sm dark:border-slate-700 dark:bg-slate-900/70">
              <div className="text-sm font-semibold">Government-grade clarity</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-300">Eligibility decisions with rationale + missing-info prompts.</div>
            </div>
            <div className="rounded-[24px] border border-slate-200/80 bg-white/80 p-4 shadow-[0_16px_50px_rgba(15,23,42,0.06)] backdrop-blur-sm dark:border-slate-700 dark:bg-slate-900/70">
              <div className="text-sm font-semibold">IBM watsonx-ready</div>
              <div className="mt-1 text-sm text-slate-600 dark:text-slate-300">Assistant for chat UX, Granite for drafting, Orchestrate for workflows.</div>
            </div>
          </div>
        </div>

        <Card className="mx-auto w-full max-w-md p-6">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-[var(--accent)]/15 text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30 font-bold">
              <Lock className="size-5" />
            </div>
            <div>
              <div className="text-base font-semibold tracking-tight text-slate-900 dark:text-slate-50">Log in</div>
              <div className="text-sm text-slate-600 dark:text-slate-300">Use a work email for best results.</div>
            </div>
          </div>

          <form className="mt-6 space-y-4" onSubmit={async (e) => { e.preventDefault(); setLoading(true); await new Promise((r) => setTimeout(r, 650)); setLoading(false); toast.success("Signed in (demo)."); navigate("/app"); }}>
            <Field label="Email" icon={<Mail className="size-4" />} inputProps={{ type: "email", placeholder: "name@startup.com", required: true }} />
            <Field label="Password" icon={<Lock className="size-4" />} inputProps={{ type: "password", placeholder: "••••••••", required: true }} />

            <div className="flex items-center justify-between text-sm">
              <label className="inline-flex items-center gap-2 text-slate-600 dark:text-slate-300">
                <input type="checkbox" className="size-4 rounded border-slate-300 bg-white/80 dark:border-slate-600 dark:bg-slate-900" />
                Remember me
              </label>
              <button type="button" className="text-slate-700 underline-offset-4 hover:underline dark:text-slate-200" onClick={() => toast("Password reset hook can be added later.")}>
                Forgot password?
              </button>
            </div>

            <Button className="w-full" isLoading={loading} type="submit">
              Continue
            </Button>

            <div className="text-center text-xs text-slate-500 dark:text-slate-400">
              By continuing you agree to responsible AI usage and data handling.
            </div>
          </form>
        </Card>
      </main>
    </div>
  );
}

function Field({ label, icon, inputProps }: { label: string; icon: React.ReactNode; inputProps: React.InputHTMLAttributes<HTMLInputElement>; }) {
  return (
    <div>
      <div className="text-xs font-semibold text-slate-700 dark:text-slate-200">{label}</div>
      <div className="mt-2 flex items-center gap-2 rounded-[16px] border border-[var(--border)] bg-[var(--input-bg)] px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-[var(--accent)]/40">
        <span className="text-[var(--text-muted)]">{icon}</span>
        <input className={cn("h-9 w-full bg-transparent text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none", "focus:outline-none")} {...inputProps} />
      </div>
    </div>
  );
}

