import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { cn } from "@/utils/cn";

const links = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#ibm-tech", label: "IBM Tech" },
  { href: "#faq", label: "FAQ" }
];

export function LandingNav() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--surface-secondary)]/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-2xl bg-[var(--accent)] text-[#111827] shadow-sm font-bold">
            <Sparkles className="size-5" />
          </div>
          <div>
            <div className="text-sm font-semibold tracking-tight text-[var(--text-primary)]">Grant Agent</div>
            <div className="text-[11px] text-[var(--text-muted)]">Built for Indian founders</div>
          </div>
        </Link>

        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="text-sm text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link to="/login">
            <Button variant="ghost" size="sm">
              Log in
            </Button>
          </Link>
          <Link to="/app/recommendations">
            <Button size="sm">Find grants free</Button>
          </Link>
        </div>

        <button type="button" className="inline-flex size-10 items-center justify-center rounded-2xl ring-1 ring-[var(--border)] md:hidden" aria-label={open ? "Close menu" : "Open menu"} onClick={() => setOpen((v) => !v)}>
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      <div className={cn("border-t border-[var(--border)] bg-[var(--surface)] px-6 py-4 md:hidden", open ? "block" : "hidden")}> 
        <nav className="flex flex-col gap-3" aria-label="Mobile">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="text-sm text-[var(--text-secondary)]" onClick={() => setOpen(false)}>
              {l.label}
            </a>
          ))}
          <div className="mt-2 flex flex-col gap-2">
            <Link to="/login" onClick={() => setOpen(false)}>
              <Button variant="secondary" className="w-full">
                Log in
              </Button>
            </Link>
            <Link to="/app/recommendations" onClick={() => setOpen(false)}>
              <Button className="w-full">Find grants free</Button>
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}
