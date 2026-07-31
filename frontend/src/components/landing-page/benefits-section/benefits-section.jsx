"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

const TOTAL_SLIDES = 2;
const AUTO_PLAY_INTERVAL = 6000;

export default function BenefitsSection() {
  const [current, setCurrent] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const trackRef = useRef(null);

  // Infinite loop: we duplicate slides [0,1,0] so when transitioning
  // from slide 1 → slide 0, it moves RIGHT to a clone of slide 0
  // then snaps back without animation.
  const slides = [0, 1, 0]; // indices into our slide content
  const [position, setPosition] = useState(0);

  const goToNext = useCallback(() => {
    if (isTransitioning) return;
    setIsTransitioning(true);
    setPosition((p) => p + 1);
  }, [isTransitioning]);

  const handleTransitionEnd = () => {
    setIsTransitioning(false);
    // If we're at the clone (position 2 which shows slide 0), snap back to 0
    if (position >= TOTAL_SLIDES) {
      const track = trackRef.current;
      if (track) {
        track.style.transition = "none";
        setPosition(0);
        // Force reflow then re-enable transition
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            if (track) track.style.transition = "";
          });
        });
      }
    }
    setCurrent(position >= TOTAL_SLIDES ? 0 : position);
  };



  useEffect(() => {
    const timer = setInterval(goToNext, AUTO_PLAY_INTERVAL);
    return () => clearInterval(timer);
  }, [goToNext]);

  function goTo(index) {
    if (isTransitioning) return;
    setIsTransitioning(true);
    setPosition(index);
  }

  return (
    <section
      id="beneficios"
      className="relative w-full overflow-hidden"
    >
      {/* Background image */}
      <Image
        src="/onboarding.webp"
        alt=""
        fill
        className="object-cover object-center"
        priority
        aria-hidden="true"
      />
      {/* White overlay — 35% */}
      <div className="absolute inset-0 bg-white/35" aria-hidden="true" />

      {/* Content */}
      <div className="relative w-full px-6 pb-12.5">
        <div className="mx-auto max-w-6xl flex flex-col">
          {/* Section title */}
          <h2 className="font-title text-[32px] font-normal text-white">
            <span className="border-b-2 border-white pb-1">Beneficios</span>
          </h2>

          {/* 2nd title */}
          <p className="font-title text-[32px] font-semibold text-white uppercase mt-1.25">
            Experimentá una nueva forma de conectarte con tus clientes
          </p>

          {/* Carousel container */}
          <div className="mt-7.5 rounded-2xl bg-white/60 backdrop-blur-sm p-5 overflow-hidden">
            {/* Slides track */}
            <div
              ref={trackRef}
              className="flex transition-transform duration-500 ease-in-out"
              style={{ transform: `translateX(-${position * (100 + 5)}%)` }}
              onTransitionEnd={handleTransitionEnd}
            >
              {/* Slide 1 — Smartphone */}
              <div className="w-full shrink-0 flex flex-col md:flex-row items-center gap-7.5 min-h-90 mr-[5%]">
                <div>
                  <Image
                    src="/smartphone.png"
                    alt="Chat de WhatsApp con Pymio"
                    width={300}
                    height={500}
                    className="h-full w-auto object-contain rounded-xl"
                  />
                </div>
                <div className="flex flex-col justify-center flex-1">
                  <p className="font-sans text-[24px] font-medium text-foreground leading-[160%]">
                    Con Pymio tus mañanas, tardes y semanas están programadas,
                    organizadas y accesibles según tus necesidades particulares.
                    Él se encarga de contestar todas las consultas, y cargar las
                    solicitudes en un solo lugar para que los puedas ver sin
                    necesidad de tenerlo que anotar en tu cuaderno, así es, tu
                    cuaderno ahora es digitado por tu ayudante Pymio.
                  </p>
                </div>
              </div>

              {/* Slide 2 — Dashboard */}
              <div className="w-full shrink-0 flex flex-col md:flex-row items-stretch gap-7.5 min-h-90 mr-[5%]">
                <div className="md:w-[70%] shrink-0 flex items-stretch">
                  <Image
                    src="/dashboard.png"
                    alt="Panel de agenda semanal de Pymio"
                    width={700}
                    height={500}
                    className="h-full w-auto object-contain rounded-xl"
                  />
                </div>
                <div className="flex flex-col justify-start pt-2 flex-1 md:w-[30%]">
                  <h3 className="font-title text-[20px] font-normal text-neutral mb-4">
                    Versión de prueba gratuita.
                  </h3>
                  <p className="font-sans text-[24px] font-medium text-foreground leading-snug tracking-[-.48]">
                    Al registrarte te facilitaremos un número de prueba gratuito
                    que te permitirá jugar con el bot, cargar tu catálogo y
                    chatear con él desde celulares autorizados para prueba.
                  </p>
                </div>
              </div>

              {/* Clone of Slide 1 — for infinite loop */}
              <div className="w-full shrink-0 flex flex-col md:flex-row items-center gap-7.5 min-h-90 mr-[5%]">
                <div>
                  <Image
                    src="/smartphone.png"
                    alt="Chat de WhatsApp con Pymio"
                    width={300}
                    height={500}
                    className="h-full w-auto object-contain rounded-xl"
                  />
                </div>
                <div className="flex flex-col justify-center flex-1">
                  <p className="font-sans text-[24px] font-medium text-foreground leading-[160%]">
                    Con Pymio tus mañanas, tardes y semanas están programadas,
                    organizadas y accesibles según tus necesidades particulares.
                    Él se encarga de contestar todas las consultas, y cargar las
                    solicitudes en un solo lugar para que los puedas ver sin
                    necesidad de tenerlo que anotar en tu cuaderno, así es, tu
                    cuaderno ahora es digitado por tu ayudante Pymio.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Dots — outside the white card */}
          <div className="flex items-center justify-center gap-3 mt-6">
            {Array.from({ length: TOTAL_SLIDES }).map((_, i) => (
              <button
                key={i}
                onClick={() => goTo(i)}
                className={cn(
                  "w-3 h-3 rounded-full transition-colors duration-300 cursor-pointer",
                  i === current % TOTAL_SLIDES
                    ? "bg-[hsl(var(--primary))]"
                    : "bg-white/60 hover:bg-white/80"
                )}
                aria-label={`Ir al slide ${i + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
