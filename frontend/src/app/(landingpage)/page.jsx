import HeroSection from "@/components/landing-page/hero-section/hero-section";
import FeaturesSection from "@/components/landing-page/features-section/features-section";
import BenefitsSection from "@/components/landing-page/benefits-section/benefits-section";
import HowToSection from "@/components/landing-page/how-to-section/how-to-section";
import FaqSection from "@/components/landing-page/faq-section/faq-section";
import ReadySection from "@/components/landing-page/ready-section/ready-section";

export default function Page() {
  return (
    <div className="flex flex-col gap-20">
      <HeroSection />
      <FeaturesSection />
      <BenefitsSection />
      <HowToSection />
      <FaqSection />
      <ReadySection />
    </div>
  );
}
