import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, BadgeCheck, Building2, IndianRupee, Sparkles, TrendingUp } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { fadeUp } from "./motion";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden px-6 pb-20 pt-16 lg:px-8 lg:pb-28 lg:pt-24">
      <div className="mx-auto max-w-7xl">
        <div className="grid items-center gap-14 lg:grid-cols-2 lg:gap-12">
          <motion.div initial="hidden" animate="visible" variants={fadeUp}>
            <motion.div custom={0} variants={fadeUp} className="inline-flex items-center gap-2 rounded-full border border-[#5BA8A0]/20 bg-[#5BA8A0]/10 px-4 py-1.5 text-xs font-medium text-[#4f918b] dark:text-[#8bd7ce]">
              <Sparkles className="size-3.5" />
              AI-powered grant discovery for India
            </motion.div>

            <motion.h1 custom={1} variants={fadeUp} className="mt-6 text-balance text-4xl font-semibold leading-[1.08] tracking-tight text-slate-900 sm:text-5xl lg:text-[3.25rem] dark:text-white">
              Find the Right Government Grant in Minutes using AI
            </motion.h1>

            <motion.p custom={2} variants={fadeUp} className="mt-6 max-w-xl text-pretty text-lg leading-relaxed text-slate-600 dark:text-slate-400">
              Stop scrolling ministry portals. Grant Agent matches your startup to eligible schemes, explains requirements in plain English, and drafts compliant proposals — powered by IBM watsonx.
            </motion.p>

            <motion.div custom={3} variants={fadeUp} className="mt-8 flex flex-wrap items-center gap-4">
              <Link to="/app/recommendations">
                <Button size="lg">Discover grants <ArrowRight className="size-4" /></Button>
              </Link>
              <Link to="/app/chat">
                <Button variant="secondary" size="lg">Talk to AI assistant</Button>
              </Link>
            </motion.div>

            <motion.div custom={4} variants={fadeUp} className="mt-10 flex flex-wrap gap-6 border-t border-slate-200/70 pt-8 dark:border-slate-800">
              <Stat icon={<IndianRupee className="size-4" />} value="₹500Cr+" label="Grants tracked" />
              <Stat icon={<Building2 className="size-4" />} value="120+" label="Central & state schemes" />
              <Stat icon={<TrendingUp className="size-4" />} value="3×" label="Faster applications" />
            </motion.div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 32, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }} className="relative">
            <div className="absolute -inset-4 rounded-[32px] bg-gradient-to-r from-[#5BA8A0]/20 via-[#F4B06A]/10 to-[#5BA8A0]/20 blur-2xl" />
            <div className="relative overflow-hidden rounded-[28px] border border-slate-200/80 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur-sm dark:border-slate-700 dark:bg-slate-900/80">
              <div className="flex items-center gap-2 border-b border-slate-200/80 px-4 py-3 dark:border-slate-700">
                <span className="size-2.5 rounded-full bg-red-400/80" />
                <span className="size-2.5 rounded-full bg-amber-400/80" />
                <span className="size-2.5 rounded-full bg-emerald-400/80" />
                <span className="ml-2 text-xs text-slate-500">grant-agent.app</span>
              </div>

              <div className="space-y-3 p-5">
                <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-950/60 dark:ring-slate-700">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Match score</span>
                    <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400">92% fit</span>
                  </div>
                  <div className="mt-2 text-sm font-semibold text-slate-900 dark:text-white">DST Seed Support — Deep Tech</div>
                  <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">₹20L–₹50L · AI / HealthTech · Karnataka</div>
                </div>

                <div className="rounded-[20px] bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-950/60 dark:ring-slate-700">
                  <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                    <BadgeCheck className="size-3.5 text-[#5BA8A0]" />
                    Eligibility check
                  </div>
                  <div className="mt-2 text-sm text-slate-700 dark:text-slate-300">Eligible — missing Udyam registration & audited FY statements.</div>
                </div>

                <div className="rounded-[20px] bg-gradient-to-r from-[#5BA8A0]/12 to-[#F4B06A]/10 p-4 ring-1 ring-[#5BA8A0]/20">
                  <div className="text-xs font-semibold text-slate-900 dark:text-white">Proposal draft ready</div>
                  <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">Executive summary · Technical approach · Budget · Milestones</div>
                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/70 dark:bg-slate-800/70">
                    <motion.div className="h-full rounded-full bg-gradient-to-r from-[#5BA8A0] to-[#F4B06A]" initial={{ width: 0 }} animate={{ width: "78%" }} transition={{ duration: 1.2, delay: 0.8, ease: "easeOut" }} />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function Stat({ icon, value, label }: { icon: ReactNode; value: string; label: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="inline-flex size-9 items-center justify-center rounded-2xl bg-[#5BA8A0]/10 text-[#5BA8A0] ring-1 ring-[#5BA8A0]/20">
        {icon}
      </span>
      <div>
        <div className="text-lg font-semibold text-slate-900 dark:text-white">{value}</div>
        <div className="text-xs text-slate-500 dark:text-slate-400">{label}</div>
      </div>
    </div>
  );
}
