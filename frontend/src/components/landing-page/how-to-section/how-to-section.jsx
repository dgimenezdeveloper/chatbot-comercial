export default function HowToSection() {
  return (
    <section id="indicaciones" className="w-full px-6 bg-white">
      <div className="mx-auto max-w-6xl">
        {/* Title */}
        <h2 className="font-title text-[32px] font-semibold text-neutral mb-10">
          <span className="border-b-2 border-neutral pb-1">
            Instrucciones
          </span>
        </h2>

        {/* Two-column content */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-0 md:divide-x md:divide-border">
          {/* Column 1 — Cómo obtener el bot */}
          <div className="flex flex-col gap-6 md:pr-10">
            <h3 className="w-full rounded-lg bg-secondary text-3xl py-3 font-semibold text-white text-center">
              ¿Cómo puedo obtener el bot?
            </h3>
            <ul className="flex flex-col gap-4 text-sm md:text-base text-muted-foreground leading-relaxed list-disc list-outside px-15">
              <li>
                <span className="font-medium text-foreground">Acceso Simple:</span>{" "}
                Al registrarte en nuestra web, hacé clic en &quot;Ingresar con
                Google&quot; y el sistema reconoce tu correo autorizado de forma
                ultra rápida, sin requerirle crear contraseñas nuevas.
              </li>
              <li>
                <span className="font-medium text-foreground">
                  Configuración del Local:
                </span>{" "}
                Lo recibimos directamente en su panel de control con un diseño súper
                limpio y fácil de usar para que complete la ficha de su negocio
                (nombre, dirección, horarios de atención, qué día de la semana
                cierra por descanso semanal) y cargue su lista de servicios y
                productos.
              </li>
            </ul>
          </div>

          {/* Column 2 — Cómo vincularlo a RRSS */}
          <div className="flex flex-col gap-6 md:pl-10">
            <h3 className="w-full rounded-lg bg-secondary text-3xl py-3 font-semibold text-white text-center">
              ¿Cómo lo vinculo a mis RRSS?
            </h3>
            <ul className="flex flex-col gap-4 text-sm md:text-base text-muted-foreground leading-relaxed list-disc list-outside px-15">
              <li>
                Una vez que un usuario nos contacta para adquirir el servicio, como
                administradores del SaaS, nosotros registramos y autorizamos su
                cuenta en nuestra base de datos.
              </li>
              <li>
                Esto significa que solo al registrarte nosotros vinculamos tus
                cuentas en Redes Sociales vinculadas a la cuenta autorizada de
                Google para empezar tu prueba.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
