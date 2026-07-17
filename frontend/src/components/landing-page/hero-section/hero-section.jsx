import Link from "next/link";
import RobotPymio from "@/components/icons/robot-pymio";

export default function Hero() {
  return (
    <section
      id="home"
      className="relative w-full max-w-300 px-5 mx-auto flex flex-col lg:flex-row items-center lg:items-start justify-between "
    >
      <div className="relative z-10 w-full lg:max-w-137 flex flex-col">
        <p className="font-sans text-sm lg:text-[14px] font-medium text-[#1A202C] leading-[121.2%] mb-5.25">
          La solución que estabas buscando para gestionar tu tiempo de trabajo
        </p>

        <h1 className="font-title text-3xl lg:text-[32px] font-semibold text-[#1A202C] leading-[121.2%] uppercase mb-8.5">
          Pyme bot, chat automatizado para tu pyme
        </h1>

        <p className="font-title text-lg lg:text-[24px] text-[#989AA0] font-medium leading-[160%] tracking-tight w-full mb-4">
          Equipo 10 te presenta su primer bot pensado especialmente para
          emprendedores.
        </p>
        <p className="font-title text-lg lg:text-[24px] text-[#989AA0] font-medium leading-[160%] tracking-tight w-full">
          En esta oportunidad te mostramos nuestro asistente para peluquerias y
          salones con gestión de turnos, respuestas y recordatorios mediante
          WhatsApp
        </p>

        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-6 mt-10 lg:mt-13.5">
          <Link
            href="/registro"
            className="flex items-center justify-center w-full sm:w-37.5 h-10.75 bg-[#ED7F3A] text-white text-[16px] font-semibold tracking-[-0.02em] rounded-[4px] shadow-[0px_4px_4px_rgba(0,0,0,0.25)] hover:bg-[#ED7F3A]/90 transition-colors"
          >
            Registrarse
          </Link>

          <a
            href="#propuesta"
            className="flex items-center justify-center w-full sm:w-37.5 h-10.75 bg-transparent text-[#456189] text-[16px] font-semibold tracking-[-0.02em] rounded-[4px] hover:bg-slate-50 transition-colors"
          >
            Ver propuesta
          </a>
        </div>
      </div>

      <div className="hidden lg:flex relative justify-center w-full lg:w-auto ">
        <RobotPymio className="w-55 sm:w-70 lg:w-94 h-auto lg:h-120.25 object-contain" />
      </div>
    </section>
  );
}
