import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Github, Linkedin, Sparkles, Twitter } from "lucide-react";

const productLinks = [
  { to: "/app/recommendations", label: "Grant discovery" },
  { to: "/app/chat", label: "AI assistant" },
  { to: "/app/proposals", label: "Proposal generator" },
  { to: "/app/profile", label: "Startup profile" }
];

const resourceLinks = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#ibm-tech", label: "IBM technologies" },
  { href: "#faq", label: "FAQ" }
];

export function LandingFooter() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--footer-bg)] px-6 py-16 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <Link to="/" className="flex items-center gap-3">
              <div className="flex size-9 items-center justify-center rounded-2xl bg-[var(--accent)] text-[#111827] font-bold">
                <Sparkles className="size-4" />
              </div>
              <span className="text-sm font-semibold text-slate-900 dark:text-white">Grant Agent</span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-slate-600 dark:text-slate-500">
              AI-powered government grant discovery and proposal generation for Indian startup founders.
            </p>
            <div className="mt-6 flex gap-3">
              <SocialIcon href="#" label="Twitter" icon={<Twitter className="size-4" />} />
              <SocialIcon href="#" label="LinkedIn" icon={<Linkedin className="size-4" />} />
              <SocialIcon href="#" label="GitHub" icon={<Github className="size-4" />} />
            </div>
          </div>

          <FooterColumn title="Product" links={productLinks.map((l) => ({ ...l, external: false }))} />
          <FooterColumn title="Resources" links={resourceLinks.map((l) => ({ ...l, external: true }))} />

          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Legal</h3>
            <ul className="mt-4 space-y-3">
              <li><a href="#" className="text-sm text-slate-600 transition hover:text-slate-900 dark:text-slate-500 dark:hover:text-slate-300">Privacy policy</a></li>
              <li><a href="#" className="text-sm text-slate-600 transition hover:text-slate-900 dark:text-slate-500 dark:hover:text-slate-300">Terms of service</a></li>
              <li><a href="#" className="text-sm text-slate-600 transition hover:text-slate-900 dark:text-slate-500 dark:hover:text-slate-300">Responsible AI</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-slate-200/80 pt-8 sm:flex-row dark:border-slate-800">
          <p className="text-xs text-slate-500">© {new Date().getFullYear()} Grant Agent. IBM Hackathon Project.</p>
          <p className="text-xs text-slate-500">Made with IBM watsonx · For Indian startups 🇮🇳</p>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({ title, links }: { title: string; links: { to?: string; href?: string; label: string; external: boolean }[]; }) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{title}</h3>
      <ul className="mt-4 space-y-3">
        {links.map((l) => (
          <li key={l.label}>
            {l.external ? (
              <a href={l.href} className="text-sm text-slate-600 transition hover:text-slate-900 dark:text-slate-500 dark:hover:text-slate-300">{l.label}</a>
            ) : (
              <Link to={l.to!} className="text-sm text-slate-600 transition hover:text-slate-900 dark:text-slate-500 dark:hover:text-slate-300">{l.label}</Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

function SocialIcon({ href, label, icon }: { href: string; label: string; icon: ReactNode }) {
  return (
    <a href={href} aria-label={label} className="inline-flex size-9 items-center justify-center rounded-2xl bg-[var(--surface-section)] text-[var(--text-secondary)] ring-1 ring-[var(--border)] transition hover:bg-[var(--hover)] hover:text-[var(--text-primary)]">
      {icon}
    </a>
  );
}
