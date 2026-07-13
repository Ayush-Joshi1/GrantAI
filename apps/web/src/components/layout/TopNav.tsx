import { Link, useLocation } from "react-router-dom";
import { BrainCircuit, Search, Sparkles } from "lucide-react";
import toast from "react-hot-toast";

import { Button } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { cn } from "@/utils/cn";

export function TopNav() {
  const { pathname } = useLocation();

  return (
    <header className="sticky top-4 z-10">
      <div className="rounded-[24px] border border-[var(--border)] bg-[var(--surface)] px-4 py-3 shadow-[0_12px_40px_rgba(0,0,0,0.03)] backdrop-blur-sm">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-[var(--accent)] text-[#111827] shadow-sm font-bold">
              <BrainCircuit className="size-5" />
            </div>
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold tracking-tight text-[var(--text-primary)]">
                {titleForPath(pathname)}
              </div>
              <div className="truncate text-xs text-[var(--text-muted)]">
                IBM-grade AI workflows for grants, eligibility, and proposals.
              </div>
            </div>
          </div>

          <div className="hidden items-center gap-2 md:flex">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--text-muted)]" />
              <input
                className={cn(
                  "h-10 w-[320px] rounded-2xl border border-[var(--border)] bg-[var(--input-bg)] pl-9 pr-3 text-sm text-[var(--text-primary)] shadow-sm",
                  "placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/40"
                )}
                placeholder="Search grants, schemes, ministries…"
                onKeyDown={(e) => {
                  if (e.key === "Enter") toast("Search wiring comes next.");
                }}
              />
            </div>

            <ThemeToggle />

            <Link to="/app/proposals">
              <Button>
                <Sparkles className="size-4" />
                Generate proposal
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

function titleForPath(pathname: string) {
  if (pathname.startsWith("/app/chat")) return "AI Chat";
  if (pathname.startsWith("/app/recommendations")) return "Grant Recommendations";
  if (pathname.startsWith("/app/proposals")) return "Proposal Generator";
  if (pathname.startsWith("/app/profile")) return "Startup Profile";
  if (pathname.startsWith("/app/history")) return "History";
  return "Dashboard";
}

