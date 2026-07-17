import { Bot, ImageIcon } from "lucide-react";

export default function FeaturesSection() {
  return (
    <section className="max-w-300 px-5 mx-auto w-full grid lg:grid-cols-2 gap-16 border-t border-slate-100 bg-white">
      {/* Left Column */}
      <div className="flex flex-col gap-6">
        <span className="text-sm font-medium text-slate-400 underline underline-offset-4 uppercase">
          Propuesta
        </span>
        <h2 className="text-3xl  font-medium text-[#456189] leading-snug">
          ¿Tienes problemas para gestionar todas las solicitudes de turnos o tu
          agenda?
        </h2>
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

      {/* Right Column (Feature Blocks) */}
      <div className="flex flex-col gap-12 justify-center">
        {/* Feature 1 */}
        <div className="flex items-center gap-6 justify-end">
          <span className="text-right text-sm font-medium text-slate-700 max-w-[120px]">
            Saludo amigable personalizado
          </span>
          <div className="w-40 h-32 bg-slate-300 rounded-tr-[3rem] rounded-bl-[3rem] rounded-tl-lg rounded-br-lg flex items-center justify-center text-slate-50 relative overflow-hidden">
            <ImageIcon size={48} className="text-slate-100" />
            <div className="absolute top-0 right-0 w-16 h-16 bg-slate-400 rounded-bl-full opacity-50"></div>
          </div>
        </div>

        {/* Feature 2 */}
        <div className="flex items-center gap-6 justify-start">
          <span className="text-left text-sm font-medium text-slate-700 max-w-[120px]">
            Contestador automatico con opciones
          </span>
          <div className="w-40 h-32 bg-slate-200 rounded-tl-[3rem] rounded-br-[3rem] rounded-tr-lg rounded-bl-lg flex items-center justify-center text-slate-50">
            <Bot size={48} className="text-slate-400" />
          </div>
        </div>

        {/* Feature 3 */}
        <div className="flex items-center gap-6 justify-end">
          <span className="text-right text-sm font-medium text-slate-700 max-w-[140px]">
            Agenda practica para el cliente y sincronizada a tu calendario.
          </span>
          <div className="w-40 h-32 bg-slate-300 rounded-tr-[3rem] rounded-bl-[3rem] rounded-tl-lg rounded-br-lg flex items-center justify-center text-slate-50 relative overflow-hidden">
            <ImageIcon size={48} className="text-slate-100" />
            <div className="absolute top-0 right-0 w-16 h-16 bg-slate-400 rounded-bl-full opacity-50"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
