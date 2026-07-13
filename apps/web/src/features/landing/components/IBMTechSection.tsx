import { motion } from "framer-motion";
import { Cloud, Cpu, GitBranch, MessageCircle } from "lucide-react";

import { fadeUp, stagger } from "./motion";

const technologies = [
  {
    icon: <MessageCircle className="size-6" />,
    name: "watsonx Assistant",
    role: "Conversational UX",
    desc: "Guides founders through eligibility questions, document checklists, and next-step actions."
  },
  {
    icon: <Cpu className="size-6" />,
    name: "Granite LLM",
    role: "Generation & reasoning",
    desc: "Drafts proposal sections, summarizes scheme guidelines, and runs compliance checks."
  },
  {
    icon: <GitBranch className="size-6" />,
    name: "watsonx Orchestrate",
    role: "Workflow automation",
    desc: "Orchestrates multi-step flows: retrieve → draft → validate → export."
  },
  {
    icon: <Cloud className="size-6" />,
    name: "IBM Cloud + FAISS",
    role: "RAG infrastructure",
    desc: "Grounds every answer in official grant documents with vector search and citations."
  }
];

export function IBMTechSection() {
  return (
    <section id="ibm-tech" className="relative px-6 py-24 lg:px-8">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-ibm-blue/[0.04] to-transparent" />
      <div className="relative mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={fadeUp}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-ibm-cyan">
            IBM Technologies
          </p>
          <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Enterprise AI stack, startup-friendly experience
          </h2>
          <p className="mt-4 text-pretty text-slate-400">
            Built on IBM watsonx and IBM Cloud — the same foundation trusted by governments and
            Fortune 500 teams worldwide.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          variants={stagger}
          className="mt-16 grid gap-5 sm:grid-cols-2"
        >
          {technologies.map((t) => (
            <motion.div
              key={t.name}
              variants={fadeUp}
              className="rounded-2xl border border-white/[0.08] bg-gradient-to-br from-white/[0.04] to-transparent p-6"
            >
              <div className="flex items-start gap-4">
                <div className="inline-flex size-12 shrink-0 items-center justify-center rounded-xl bg-ibm-blue/15 text-ibm-cyan ring-1 ring-ibm-blue/25">
                  {t.icon}
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-ibm-cyan">
                    {t.role}
                  </div>
                  <h3 className="mt-1 text-lg font-semibold text-white">{t.name}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">{t.desc}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
