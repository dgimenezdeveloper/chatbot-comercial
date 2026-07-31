"use client";

import { useState } from "react";
import Image from "next/image";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

const SLIDES = [
  {
    image: "/smartphone.png",
    alt: "Chat de WhatsApp con Pymio",
    imagePosition: "left",
    text: "Con Pymio tus mañanas, tardes y semanas están programadas, organizadas y accesibles según tus necesidades particulares. Él se encarga de contestar todas las consultas, y cargar las solicitudes en un solo lugar para que los puedas ver sin necesidad de tenerlo que anotar en tu cuaderno, así es, tu cuaderno ahora es digitado por tu ayudante Pymio.",
  },
  {
    image: "/dashboard.png",
    alt: "Panel de agenda semanal de Pymio",
    imagePosition: "left",
    text: "Al registrarte te facilitaremos un número de prueba gratuito que te permitirá jugar con el bot, cargar tu catálogo y chatear con él desde celulares autorizados para prueba.",
  },
];

export default function BenefitsSection() {
  const [current, setCurrent] = useState(0);

  function goTo(index) {
    setCurrent(index);
  }

  function prev() {
    setCurrent((c) => (c === 0 ? SLIDES.length - 1 : c - 1));
  }

  function next() {
    setCurrent((c) => (c === SLIDES.length - 1 ? 0 : c + 1));
  }

  const slide = SLIDES[current];

  return (
    <section id="beneficios" className="relative w-full min-h-[500px] md:min-h-[600px] overflow-hidden">
      {/* Background image */}
      <Image
        src="/onboarding.webp"
        alt=""
        fill
        className="object-cover object-center"
        priority
        aria-hidden="true"
      />
      {/* White semi-transparent overlay */}
      <div className="absolute inset-0 bg-white/80" aria-hidden="true" />

      {/* Content */}
      <div className="relative z-10 w-full h-full px-6 py-[60px]">
        <div className="mx-auto max-w-6xl flex flex-col h-full">
          {/* Title */}
          <h2 className="font-title text-[32px] font-semibold text-white mb-10 md:mb-14">
            <span className="border-b-2 border-white pb-1">
              Beneficios
            </span>
          </h2>

          {/* Carousel slide */}
          <div className="flex-1 flex flex-col md:flex-row items-center gap-8 md:gap-12">
            {/* Image */}
            <div className="md:w-1/2 flex items-center justify-center">
              <div className="rounded-2xl overflow-hidden shadow-xl bg-white/60 backdrop-blur-sm p-2">
                <Image
                  src={slide.image}
                  alt={slide.alt}
                  width={500}
                  height={400}
                  className="w-full max-w-[420px] h-auto object-contain rounded-xl"
                />
              </div>
            </div>

            {/* Text */}
            <div className="md:w-1/2 text-sm md:text-base text-foreground leading-relaxed">
              <p>{slide.text}</p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={prev}
              className="w-9 h-9 rounded-full border border-border bg-white/70 flex items-center justify-center text-muted-foreground hover:bg-white hover:text-foreground transition-colors cursor-pointer"
              aria-label="Anterior"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Dots */}
            <div className="flex items-center gap-2">
              {SLIDES.map((_, i) => (
                <button
                  key={i}
                  onClick={() => goTo(i)}
                  className={cn(
                    "w-2.5 h-2.5 rounded-full transition-colors cursor-pointer",
                    i === current
                      ? "bg-[hsl(var(--primary))]"
                      : "bg-muted-foreground/40 hover:bg-muted-foreground/70"
                  )}
                  aria-label={`Ir al slide ${i + 1}`}
                />
              ))}
            </div>

            <button
              onClick={next}
              className="w-9 h-9 rounded-full border border-border bg-white/70 flex items-center justify-center text-muted-foreground hover:bg-white hover:text-foreground transition-colors cursor-pointer"
              aria-label="Siguiente"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
