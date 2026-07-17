import HeroSection from "@/components/landing-page/hero-section/hero-section";
import FeaturesSection from "@/components/landing-page/features-section/features-section";
import OnboardingSection from "@/components/landing-page/onboarding-section/onboarding-section";
import HowToSection from "@/components/landing-page/how-to-section/how-to-section";
import ContactSection from "@/components/landing-page/contact-section/contact-section";

export default function Page() {
  return (
    <div className="flex flex-col gap-20">
      <HeroSection />
      <FeaturesSection />
      <OnboardingSection />
      <HowToSection />
      <ContactSection />
    </div>
  );
}
