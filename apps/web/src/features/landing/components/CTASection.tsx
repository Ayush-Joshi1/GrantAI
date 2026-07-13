import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { fadeUp } from "./motion";

export function CTASection() {
  return (
    <section className="relative px-6 py-24 lg:px-8">
      <motion.div
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={fadeUp}
        className="relative mx-auto max-w-5xl overflow-hidden rounded-3xl"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-ibm-blue via-ibm-blue-dark to-ibm-purple" />
        <div
          aria-hidden="true"
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 50%, rgba(255,255,255,0.15), transparent 50%), radial-gradient(circle at 80% 50%, rgba(17,146,232,0.2), transparent 50%)"
          }}
        />

        <div className="relative px-8 py-16 text-center sm:px-16 sm:py-20">
          <div className="mx-auto inline-flex size-14 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-sm">
            <Sparkles className="size-7 text-white" />
          </div>
          <h2 className="mt-6 text-balance text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Ready to find your next government grant?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-pretty text-base text-blue-100/90">
            Join founders who are unlocking non-dilutive capital with AI. Start free — no credit card,
            no consultant fees.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link to="/app/recommendations">
              <Button
                size="lg"
                className="bg-white text-ibm-blue-dark shadow-none hover:bg-blue-50"
              >
                Get started free <ArrowRight className="size-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button
                variant="secondary"
                size="lg"
                className="border-white/20 bg-white/10 text-white ring-white/20 hover:bg-white/20"
              >
                Sign in
              </Button>
            </Link>
          </div>
          <p className="mt-6 text-xs text-blue-200/70">
            Built for IBM Hackathon · Powered by watsonx · Made in India
          </p>
        </div>
      </motion.div>
    </section>
  );
}
