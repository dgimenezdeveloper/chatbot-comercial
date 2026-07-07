import HeroSection from '@/components/landingpage/HeroSection/HeroSection'
import FeaturesSection from '@/components/landingpage/FeaturesSection/FeaturesSection'
import OnboardingSection from '@/components/landingpage/OnboardingSection/OnboardingSection'
import HowToSection from '@/components/landingpage/HowToSection/HowToSection'
import ContactSection from '@/components/landingpage/ContactSection/ContactSection'

export default function Page() {
  return (<>
      <HeroSection />
      <FeaturesSection />
      <OnboardingSection />
      <HowToSection />
      <ContactSection />
      </>
  )
}