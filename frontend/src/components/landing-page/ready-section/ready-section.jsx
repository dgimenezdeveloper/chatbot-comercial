import Image from "next/image";

export default function ReadySection() {
  return (
    <section className="w-full px-6">
      <div className="mx-auto max-w-5xl grid grid-cols-1 md:grid-cols-4 items-end">
        {/* Col 1-2: Robot + speech bubble */}
        <div className="md:col-span-2 flex flex-col items-center">
          {/* Speech bubble — aligned right */}
          <div className="relative self-end mr-4 mb-3 max-w-[150px] rounded-2xl bg-[hsl(var(--secondary))] px-4 py-3 text-center text-xs font-medium text-white shadow-md">
            <p>¡Bienvenido!</p>
            <p>Estoy listo para</p>
            <p>ayudarte!</p>
            {/* Bubble tail — bottom-left */}
            <span
              className="absolute -bottom-3 left-4 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[14px] border-l-transparent border-r-transparent border-t-[hsl(var(--secondary))]"
              aria-hidden="true"
            />
          </div>

          {/* Robot image — centered */}
          <Image
            src="/robot-ok.png"
            alt="Robot asistente listo para trabajar"
            width={320}
            height={320}
            className="w-full max-w-[280px] md:max-w-[300px] h-auto object-contain"
            priority={false}
          />
        </div>

        {/* Col 3-4: Info card — full width, semicircle left */}
        <div className="md:col-span-2 w-full rounded-l-full rounded-r-none bg-[hsl(var(--secondary))] flex items-center justify-center text-center text-white shadow-lg min-h-[260px] px-10 py-8 md:px-12 md:py-10">
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
