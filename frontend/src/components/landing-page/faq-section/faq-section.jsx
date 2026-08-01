"use client";

import { Accordion } from "@base-ui/react/accordion";
import { ChevronDown } from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";

const FAQ_ITEMS = [
  {
    question: "¿Cuánto cuesta la autorización para usar el bot?",
    answer:
      "PYME-BOT ofrece planes accesibles pensados para emprendedores y pequeños negocios. Podés comenzar con un plan gratuito de prueba y luego elegir el que mejor se adapte a tu volumen de consultas.",
  },
  {
    question: "¿Cuáles son las formas de pago?",
    answer:
      "Aceptamos tarjetas de crédito, débito y transferencias bancarias. Los pagos se procesan de forma segura y podés gestionar tu suscripción directamente desde el panel de configuración.",
  },
  {
    question: "¿Puedo obtener una prueba?",
    answer:
      "Sí, ofrecemos un período de prueba gratuito para que puedas configurar tu bot de WhatsApp, cargar tus servicios y ver cómo responde a las consultas de tus clientes antes de comprometerte con un plan.",
  },
  {
    question: "Otras consultas",
    answer:
      "Para cualquier otra duda podés escribirnos desde la sección de contacto o directamente a nuestro WhatsApp de soporte. Te responderemos a la brevedad.",
  },
];

export default function FaqSection() {
  return (
    <section id="consultas" className="w-full px-6 py-15 bg-section-alt">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-[32px] font-medium text-neutral leading-[160%] tracking-[2%] mb-5">
          <span className="underline underline-offset-3 decoration-2">Consultas</span>
        </h2>

        {/* Content grid: accordion card (smaller) + robot image (larger) */}
        <div className="grid grid-cols-1 md:grid-cols-[3fr_2fr] gap-8 items-center">
          {/* White rounded card wrapping the accordion */}
          <div className="rounded-2xl bg-white p-6 md:p-8 shadow-sm">
            <Accordion.Root
              className="flex flex-col gap-3"
              defaultValue={[0]}
            >
              {FAQ_ITEMS.map((item, index) => (
                <Accordion.Item
                  key={index}
                  value={index}
                  className="group rounded-lg border border-border overflow-hidden bg-muted data-open:bg-white transition-colors duration-200"
                >
                  <Accordion.Header>
                    <Accordion.Trigger
                      className={cn(
                        "flex w-full items-center justify-between px-5 py-4",
                        "text-left text-sm md:text-base font-medium text-foreground",
                        "cursor-pointer hover:bg-muted/40 transition-colors"
                      )}
                    >
                      {item.question}
                      <ChevronDown
                        className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 group-data-open:rotate-180"
                        aria-hidden="true"
                      />
                    </Accordion.Trigger>
                  </Accordion.Header>
                  <Accordion.Panel
                    className={cn(
                      "overflow-hidden",
                      "data-starting-style:h-0 data-ending-style:h-0",
                      "h-(--accordion-panel-height)",
                      "transition-[height] duration-300 ease-in-out"
                    )}
                    keepMounted
                  >
                    <div className="px-5 pb-4 text-sm text-muted-foreground leading-relaxed">
                      {item.answer}
                    </div>
                  </Accordion.Panel>
                </Accordion.Item>
              ))}
            </Accordion.Root>
          </div>

          {/* Robot illustration */}
          <div className="hidden md:flex items-center justify-center">
            <Image
              src="/robot-question.png"
              alt="Robot asistente con signo de pregunta"
              width={360}
              height={360}
              className="w-auto h-auto object-contain"
              priority={false}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
