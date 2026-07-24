import { Inter, Montserrat } from "next/font/google";
import Image from "next/image";
import Link from "next/link";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600"],
});

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  weight: ["500", "600", "700"],
});

/**
 * Global 404 page — landing style, shown for all unmatched routes.
 * Does not use ThemeProvider to avoid <script> warnings on client navigation.
 * Applies fonts and styles self-contained.
 */
export default function NotFound() {
  return (
    <div className={`${inter.variable} ${montserrat.variable} flex min-h-screen flex-col bg-white font-[family-name:var(--font-inter)]`}>
      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="mx-auto grid w-full max-w-6xl items-center gap-10 lg:grid-cols-2 lg:gap-16">

          {/* Left column — text */}
          <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
            {/* 404 heading */}
            <h1 className="font-[family-name:var(--font-montserrat)] text-7xl font-bold text-[hsl(221,83%,53%)] sm:text-8xl lg:text-9xl">
              404
            </h1>

            <h2 className="mt-4 font-[family-name:var(--font-montserrat)] text-2xl font-bold text-slate-900 sm:text-3xl">
              Esta pagina no esta por aqui
            </h2>

            <p className="mt-4 max-w-md text-base text-slate-500">
              Parece que te perdiste en el camino. Pero no te preocupes, Pymio esta aqui para ayudarte a volver al lugar correcto.
            </p>

            {/* Value props */}
            <div className="mt-8 space-y-5">
              <ValueProp
                title="Automatizacion de consultas"
                description="Responde al instante preguntas frecuentes, comparte catalogos y precios."
              />
              <ValueProp
                title="Organizacion comercial"
                description="Registra potenciales clientes y centraliza toda la informacion en un solo lugar."
              />
              <ValueProp
                title="Eficiencia operativa"
                description="Reduce la carga de trabajo y profesionaliza tu atencion para escalar tu negocio."
              />
            </div>

            {/* CTA */}
            <Link
              href="/"
              className="mt-8 inline-flex items-center gap-2 rounded-lg bg-[hsl(221,83%,53%)] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[hsl(221,83%,45%)]"
            >
              <span aria-hidden="true">&larr;</span>
              Volver al inicio
            </Link>
          </div>

          {/* Right column — illustration */}
          <div className="flex items-center justify-center">
            <Image
              src="/404-landing.png"
              alt="Robot Pymio indicando direcciones"
              width={550}
              height={500}
              className="h-auto w-full max-w-md lg:max-w-lg"
              priority
            />
          </div>
        </div>
      </main>
    </div>
  );
}

function ValueProp({ title, description }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-[hsl(221,83%,53%)]/10">
        <svg className="size-4 text-[hsl(221,83%,53%)]" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v1h8v-1zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-1a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 17v1h-3zM4.75 14.094A5.973 5.973 0 004 17v1H1v-1a3 3 0 013.75-2.906z" />
        </svg>
      </div>
      <div>
        <p className="text-sm font-semibold text-slate-900">{title}</p>
        <p className="text-sm text-slate-500">{description}</p>
      </div>
    </div>
  );
}
