import Image from "next/image";

export default function ReadySection() {
  return (
    <section className="w-full px-6">
      <div className="mx-auto max-w-6xl grid grid-cols-1 md:grid-cols-7 items-end">
        <div className="md:col-span-3  hidden md:flex md:flex-col">

          <Image
            src="/robot-ok.png"
            alt="Robot asistente listo para trabajar"
            width={600}
            height={600}
            className="w-full h-auto object-contain"
            priority={false}
          />
        </div>

        {/* Col 3-4: Info card — full width, semicircle left */}
        <div className="md:col-span-4 w-full rounded-l-full rounded-r-none bg-secondary flex items-center justify-center text-center text-white shadow-lg min-h-50 lg:min-h-75 px-10 py-8 md:px-12 md:py-10">
          <div>
            <h2 className="font-title text-2xl md:text-3xl font-bold mb-5">
              Listo para trabajar
            </h2>
            <p className="text-base md:text-lg leading-relaxed text-white/90">
              Una vez que completás tus datos, el bot de WhatsApp ya está activo en
              tiempo real y respondiendo consultas de forma autónoma.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
