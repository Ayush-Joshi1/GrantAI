import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { Bot, FileText, Search, ShieldCheck, Target, Zap } from "lucide-react";

import { fadeUp, stagger } from "./motion";

const features = [
  { icon: <Search className="size-5" />, title: "Smart grant discovery", desc: "Search 120+ central and state schemes filtered by sector, stage, location, and turnover." },
  { icon: <Target className="size-5" />, title: "AI recommendations", desc: "Ranked matches with fit scores and plain-language reasons — not generic lists." },
  { icon: <ShieldCheck className="size-5" />, title: "Eligibility engine", desc: "Instant decisions with missing-info prompts and evidence-backed rationale." },
  { icon: <Bot className="size-5" />, title: "Conversational assistant", desc: "Ask anything about schemes, documents, or deadlines — guided like a policy expert." },
  { icon: <FileText className="size-5" />, title: "Proposal generator", desc: "Structured drafts with compliance checks, citations, and export-ready formats." },
  { icon: <Zap className="size-5" />, title: "End-to-end workflow", desc: "From discovery to submission prep in one workspace — built for startup speed." }
];

export function FeaturesSection() {
  return (
    <section id="features" className="relative px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-80px" }} variants={fadeUp} className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-[#5BA8A0]">Features</p>
          <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl dark:text-white">Everything founders need to win government funding</h2>
          <p className="mt-4 text-pretty text-slate-600 dark:text-slate-400">One platform replaces weeks of portal-hopping, consultant calls, and guesswork.</p>
        </motion.div>

        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-60px" }} variants={stagger} className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <FeatureCard key={f.title} icon={f.icon} title={f.title} desc={f.desc} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function FeatureCard({ icon, title, desc }: { icon: ReactNode; title: string; desc: string }) {
  return (
    <motion.div variants={fadeUp} className="group rounded-[24px] border border-slate-200/80 bg-white/80 p-6 shadow-[0_16px_50px_rgba(15,23,42,0.05)] transition hover:-translate-y-1 hover:border-[#5BA8A0]/20 hover:shadow-[0_18px_60px_rgba(15,23,42,0.08)] dark:border-slate-800 dark:bg-slate-900/70">
      <div className="inline-flex size-11 items-center justify-center rounded-2xl bg-[#5BA8A0]/10 text-[#5BA8A0] ring-1 ring-[#5BA8A0]/20 transition group-hover:bg-[#5BA8A0]/15">
        {icon}
      </div>
      <h3 className="mt-4 text-base font-semibold text-slate-900 dark:text-white">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{desc}</p>
    </motion.div>
  );
}
