import { NavLink } from "react-router-dom";
import {
  Bot,
  Building2,
  Clock3,
  FileText,
  LayoutDashboard,
  Sparkles,
  Target
} from "lucide-react";

import { cn } from "@/utils/cn";

const nav = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/chat", label: "Chat", icon: Bot },
  { to: "/app/recommendations", label: "Recommendations", icon: Target },
  { to: "/app/proposals", label: "Proposal Generator", icon: FileText },
  { to: "/app/profile", label: "Profile", icon: Building2 },
  { to: "/app/history", label: "History", icon: Clock3 }
];

export function Sidebar() {
  return (
    <aside className="sticky top-6 hidden h-[calc(100dvh-3rem)] md:block">
      <div className="flex h-full flex-col rounded-[28px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_16px_50px_rgba(0,0,0,0.03)] backdrop-blur-sm">
        <div className="flex items-center gap-3 border-b border-[var(--border)] px-5 py-4">
          <div className="flex size-10 items-center justify-center rounded-2xl bg-[var(--accent)] text-[#111827] shadow-sm font-bold">
            <Sparkles className="size-5" />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold tracking-tight text-[var(--text-primary)]">Grant Agent</div>
            <div className="truncate text-xs text-[var(--text-muted)]">IBM + AI + Gov grants</div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-3">
          <div className="space-y-1">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/app"}
                className={({ isActive }) =>
                  cn(
                    "group flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm ring-1 ring-transparent transition-all duration-200",
                    "hover:bg-[var(--hover)] hover:ring-[var(--border)]",
                    isActive
                      ? "bg-[var(--accent)]/15 text-[var(--text-primary)] ring-[var(--border)] font-semibold"
                      : "text-[var(--text-secondary)]"
                  )
                }
              >
                <Icon className={cn(
                  "size-4 transition",
                  "text-[var(--text-muted)] group-hover:text-[var(--text-primary)]"
                )} />
                <span className="truncate">{label}</span>
              </NavLink>
            ))}
          </div>
        </nav>

        <div className="border-t border-[var(--border)] p-4">
          <div className="rounded-2xl bg-[var(--surface-section)] p-3 ring-1 ring-[var(--border)]">
            <div className="text-xs font-semibold text-[var(--text-primary)]">System status</div>
            <div className="mt-1 text-xs text-[var(--text-secondary)]">
              Retrieval, Assistant tools, and proposal jobs will appear here.
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}

