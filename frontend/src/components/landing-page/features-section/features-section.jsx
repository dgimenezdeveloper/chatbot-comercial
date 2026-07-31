import Image from "next/image";

export default function FeaturesSection() {
  return (
    <section id="propuesta" className="max-w-300 px-5 mx-auto w-full grid lg:grid-cols-2 gap-16 border-t border-slate-100 bg-white">
      {/* Left Column */}
      <div className="flex flex-col gap-6">
        <h2 className="font-title text-[32px] font-semibold text-[hsl(var(--neutral))]">
          <span className="border-b-2 border-[hsl(var(--neutral))] pb-1">
            Propuesta
          </span>
        </h2>
        <h3 className="text-2xl md:text-3xl font-medium text-[#456189] leading-snug">
          ¿Tienes problemas para gestionar todas las solicitudes de turnos o tu
          agenda?
        </h3>
        <p className="text-slate-500 leading-relaxed">
          Te sucede que te llegan mensajes al WhatsApp y no podes contestar
          porque estas trabajando, por lo que perdes nuevos clientes para tu
          peluquería o salón?
        </p>

        <div className="mt-4">
          <p className="text-slate-600 mb-4 font-medium">
            Esta es la indicación de que este bot es para vos:
          </p>
          <ul className="space-y-3">
            {[
              "Responder las dudas de los clientes.",
              "Ayudarlos a agendar su turno.",
              "Personalizar las respuestas que reciben.",
              "Derivarlo para que los atiendas cuando tengas tiempo.",
            ].map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-slate-500">
                <span className="text-slate-400 mt-1">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Right Column — Features image */}
      <div className="flex items-center justify-center">
        <Image
          src="/features.webp"
          alt="Funcionalidades de Pymio: saludo personalizado, contestador automático y agenda sincronizada"
          width={500}
          height={500}
          className="w-full max-w-[480px] h-auto object-contain"
          priority
        />
      </div>
    </section>
  );
}
