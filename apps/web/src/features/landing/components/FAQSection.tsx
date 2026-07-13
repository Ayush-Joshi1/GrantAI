import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

import { cn } from "@/utils/cn";
import { fadeUp } from "./motion";

const faqs = [
  {
    q: "Which government grants does Grant Agent cover?",
    a: "We track central schemes (DST, MSME, Startup India, BIRAC, MeitY) and state-level startup policies across major hubs — Bengaluru, Mumbai, Delhi NCR, Hyderabad, Pune, and more. New schemes are added continuously."
  },
  {
    q: "Is this only for tech startups?",
    a: "No. While deep-tech and AI startups benefit most, we cover agritech, healthtech, manufacturing, cleantech, and social enterprises — any sector with active government funding programs."
  },
  {
    q: "How accurate is the eligibility checker?",
    a: "Eligibility is computed from official scheme rules plus your profile data. We show confidence scores, missing information, and citations — so you always know why a decision was made."
  },
  {
    q: "Can I export proposals for submission?",
    a: "Yes. Generated proposals include structured sections aligned to scheme criteria and can be exported as PDF or DOCX. You review and edit before submitting on the official portal."
  },
  {
    q: "Do I need IBM Cloud credentials to use Grant Agent?",
    a: "No. IBM watsonx services run on our backend. Founders interact through a simple web interface — no technical setup required."
  },
  {
    q: "Is my startup data secure?",
    a: "All data is encrypted in transit and at rest. We follow enterprise-grade access controls and never share your information with third parties without consent."
  }
];

export function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="relative px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={fadeUp}
          className="text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-ibm-cyan">FAQ</p>
          <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Frequently asked questions
          </h2>
        </motion.div>

        <div className="mt-12 space-y-3">
          {faqs.map((item, i) => (
            <motion.div
              key={item.q}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              custom={i * 0.05}
              variants={fadeUp}
              className="overflow-hidden rounded-xl border border-white/[0.08] bg-white/[0.03]"
            >
              <button
                type="button"
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                aria-expanded={open === i}
                onClick={() => setOpen(open === i ? null : i)}
              >
                <span className="text-sm font-medium text-white">{item.q}</span>
                <ChevronDown
                  className={cn(
                    "size-5 shrink-0 text-slate-400 transition-transform",
                    open === i && "rotate-180"
                  )}
                />
              </button>
              <AnimatePresence initial={false}>
                {open === i ? (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                  >
                    <p className="border-t border-white/[0.06] px-5 pb-4 pt-2 text-sm leading-relaxed text-slate-400">
                      {item.a}
                    </p>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
