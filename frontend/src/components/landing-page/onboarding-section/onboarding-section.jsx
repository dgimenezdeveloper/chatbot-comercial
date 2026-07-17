import Image from "next/image";

export default function OnboardingSection() {
  return (
    <section className="relative w-full min-h-175 flex items-center justify-center overflow-hidden bg-gray-900 py-16">
      <div className="absolute inset-0 z-0">
        <Image
          src="/onboarding.webp"
          alt="Fondo de onboarding"
          fill
          className="object-cover object-center"
          priority
        />
        <div className="absolute inset-0 bg-black/20" />
      </div>

      <div className="relative z-10 w-full max-w-300 mx-auto px-4 md:px-8 h-full flex flex-col justify-center">
        <div className="flex flex-col lg:flex-row items-center gap-8">
          <div className="w-75 rounded-4xl overflow-hidden border-4 border-gray-100 shadow-2xl bg-white">
            <div className="h-150 w-full bg-gray-50 flex items-center justify-center text-gray-400">
              Componente Chat UI
            </div>
          </div>

          <div className="flex-1">
            {/* TODO Seccion Derecha, reemplazar con contenido de Figma */}
          </div>
        </div>
      </div>
    </section>
  );
}
