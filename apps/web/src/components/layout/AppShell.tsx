import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";

export function AppShell() {
  return (
    <div className="min-h-dvh bg-[var(--surface-secondary)] text-[var(--text-primary)] transition-colors duration-200">
      <BackgroundFX />
      <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-4 px-4 py-4 md:grid-cols-[260px_1fr] md:gap-6 md:px-6 md:py-6">
        <Sidebar />
        <div className="min-w-0">
          <TopNav />
          <main className="mt-4 min-w-0">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

function BackgroundFX() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden">
      <div className="absolute -top-40 left-1/2 h-[520px] w-[820px] -translate-x-1/2 rounded-full bg-gradient-to-r from-[var(--accent)]/15 via-[var(--accent)]/5 to-transparent blur-3xl" />
      <div className="absolute bottom-[-180px] right-[-220px] h-[520px] w-[520px] rounded-full bg-gradient-to-tr from-[var(--accent)]/10 to-transparent blur-3xl" />
      <div className="absolute left-[-220px] top-[40%] h-[420px] w-[420px] rounded-full bg-gradient-to-tr from-[var(--accent)]/10 to-transparent blur-3xl" />
    </div>
  );
}

