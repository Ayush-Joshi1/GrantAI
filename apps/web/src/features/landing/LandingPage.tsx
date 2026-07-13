import { LandingBackground } from "./components/LandingBackground";
import { LandingNav } from "./components/LandingNav";
import { HeroSection } from "./components/HeroSection";
import { FeaturesSection } from "./components/FeaturesSection";
import { HowItWorksSection } from "./components/HowItWorksSection";
import { IBMTechSection } from "./components/IBMTechSection";
import { BenefitsSection } from "./components/BenefitsSection";
import { TestimonialsSection } from "./components/TestimonialsSection";
import { FAQSection } from "./components/FAQSection";
import { CTASection } from "./components/CTASection";
import { LandingFooter } from "./components/LandingFooter";

export function LandingPage() {
  return (
    <div className="relative min-h-dvh bg-[var(--surface-secondary)] text-[var(--text-primary)] transition-colors duration-200">
      <LandingBackground />
      <div className="relative z-10">
        <LandingNav />
        <main>
          <HeroSection />
          <FeaturesSection />
          <HowItWorksSection />
          <IBMTechSection />
          <BenefitsSection />
          <TestimonialsSection />
          <FAQSection />
          <CTASection />
        </main>
        <LandingFooter />
      </div>
    </div>
  );
}
