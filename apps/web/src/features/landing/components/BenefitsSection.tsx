import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { Clock, IndianRupee, MapPin, Users } from "lucide-react";

import { fadeUp, stagger } from "./motion";

const benefits = [
  {
    icon: <Clock className="size-5" />,
    title: "Save 40+ hours per application",
    desc: "No more reading 80-page PDFs. Get answers and drafts in minutes, not weeks."
  },
  {
    icon: <IndianRupee className="size-5" />,
    title: "Access capital you're missing",
    desc: "Most founders apply to 1–2 schemes. Grant Agent surfaces 10+ you never knew existed."
  },
  {
    icon: <MapPin className="size-5" />,
    title: "Built for India's policy landscape",
    desc: "Central ministries, state incentives, MSME schemes, and Startup India — all in one place."
  },
  {
    icon: <Users className="size-5" />,
    title: "Founder-first, not consultant-first",
    desc: "Plain language, actionable steps, and transparent eligibility — no jargon gatekeeping."
  }
];

export function BenefitsSection() {
  return (
    <section className="relative px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-br from-ibm-gray-100/80 to-[#030712]">
          <div className="grid lg:grid-cols-2">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-80px" }}
              variants={fadeUp}
              className="p-10 lg:p-14"
            >
              <p className="text-sm font-semibold uppercase tracking-widest text-ibm-cyan">Benefits</p>
              <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Why Indian startup founders choose Grant Agent
              </h2>
              <p className="mt-4 text-pretty text-slate-400">
                Government grants aren't impossible — they're just hard to navigate. We make them
                accessible.
              </p>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-60px" }}
              variants={stagger}
              className="grid gap-px bg-white/[0.06] sm:grid-cols-2"
            >
              {benefits.map((b) => (
                <BenefitItem key={b.title} icon={b.icon} title={b.title} desc={b.desc} />
              ))}
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}

function BenefitItem({
  icon,
  title,
  desc
}: {
  icon: ReactNode;
  title: string;
  desc: string;
}) {
  return (
    <motion.div variants={fadeUp} className="bg-[#0a0f1a]/90 p-6 lg:p-8">
      <span className="inline-flex size-10 items-center justify-center rounded-lg bg-ibm-blue/15 text-ibm-cyan">
        {icon}
      </span>
      <h3 className="mt-4 text-base font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">{desc}</p>
    </motion.div>
  );
}
