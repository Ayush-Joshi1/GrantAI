import { motion } from "framer-motion";
import { ClipboardCheck, MessageSquare, Rocket, Search } from "lucide-react";

import { fadeUp } from "./motion";

const steps = [
  {
    step: "01",
    icon: <Search className="size-5" />,
    title: "Tell us about your startup",
    desc: "Share sector, location, incorporation date, and stage. We build your eligibility profile in seconds."
  },
  {
    step: "02",
    icon: <ClipboardCheck className="size-5" />,
    title: "Get matched grants instantly",
    desc: "AI ranks schemes from DST, MSME, Startup India, and state policies — with fit scores and deadlines."
  },
  {
    step: "03",
    icon: <MessageSquare className="size-5" />,
    title: "Chat & clarify requirements",
    desc: "Ask the assistant what documents you need, what's missing, and how to strengthen your application."
  },
  {
    step: "04",
    icon: <Rocket className="size-5" />,
    title: "Generate & submit-ready proposal",
    desc: "Export a structured, citation-backed draft aligned to the scheme's evaluation criteria."
  }
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="relative px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={fadeUp}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-ibm-cyan">How it works</p>
          <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            From zero to application-ready in four steps
          </h2>
        </motion.div>

        <div className="relative mt-16">
          <div
            aria-hidden="true"
            className="absolute left-8 top-0 hidden h-full w-px bg-gradient-to-b from-ibm-blue/50 via-ibm-cyan/30 to-transparent lg:left-1/2 lg:block"
          />

          <div className="space-y-8 lg:space-y-12">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-40px" }}
                custom={i * 0.1}
                variants={fadeUp}
                className={`relative flex flex-col gap-6 lg:flex-row lg:items-center ${
                  i % 2 === 1 ? "lg:flex-row-reverse" : ""
                }`}
              >
                <div className="lg:w-1/2 lg:px-12">
                  <div className="inline-flex items-center gap-3">
                    <span className="text-xs font-bold tracking-widest text-ibm-blue">{s.step}</span>
                    <span className="inline-flex size-10 items-center justify-center rounded-xl bg-ibm-blue/15 text-ibm-cyan ring-1 ring-ibm-blue/25">
                      {s.icon}
                    </span>
                  </div>
                  <h3 className="mt-4 text-xl font-semibold text-white">{s.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">{s.desc}</p>
                </div>

                <div className="hidden lg:block lg:w-1/2" />

                <div className="absolute left-6 top-6 hidden size-4 rounded-full border-2 border-ibm-blue bg-[#030712] lg:left-1/2 lg:-translate-x-1/2 lg:block" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
