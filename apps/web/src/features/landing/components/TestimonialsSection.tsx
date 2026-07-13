import { motion } from "framer-motion";
import { Quote } from "lucide-react";

import { fadeUp, stagger } from "./motion";

const testimonials = [
  {
    quote:
      "We spent three months on a consultant before finding Grant Agent. In one afternoon we had five eligible schemes and a draft proposal for DST.",
    name: "Priya Sharma",
    role: "Co-founder, AarogyaAI Labs",
    location: "Bengaluru"
  },
  {
    quote:
      "The eligibility checker saved us from applying to a scheme we didn't qualify for. The missing-info prompts are exactly what founders need.",
    name: "Rahul Mehta",
    role: "CEO, AgriSense Technologies",
    location: "Pune"
  },
  {
    quote:
      "As a first-time founder, government portals were overwhelming. Grant Agent feels like having a policy expert on speed dial.",
    name: "Ananya Reddy",
    role: "Founder, EduBridge AI",
    location: "Hyderabad"
  }
];

export function TestimonialsSection() {
  return (
    <section className="relative px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={fadeUp}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-ibm-cyan">
            Testimonials
          </p>
          <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Trusted by founders across India
          </h2>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          variants={stagger}
          className="mt-16 grid gap-6 md:grid-cols-3"
        >
          {testimonials.map((t) => (
            <motion.blockquote
              key={t.name}
              variants={fadeUp}
              className="flex flex-col rounded-2xl border border-white/[0.08] bg-white/[0.03] p-6"
            >
              <Quote className="size-8 text-ibm-blue/40" />
              <p className="mt-4 flex-1 text-sm leading-relaxed text-slate-300">&ldquo;{t.quote}&rdquo;</p>
              <footer className="mt-6 border-t border-white/[0.06] pt-4">
                <div className="text-sm font-semibold text-white">{t.name}</div>
                <div className="mt-0.5 text-xs text-slate-500">
                  {t.role} · {t.location}
                </div>
              </footer>
            </motion.blockquote>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
