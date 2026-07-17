import { Input } from "@/components/ui/input/input";

export default function ContactSection() {
  return (
    <section className="w-full bg-white py-24 px-6 flex justify-center">
      <div className="bg-[#e2e8f0] w-full max-w-4xl min-h-[400px] flex items-center justify-end p-8 md:p-16 rounded-xl">
        {/* Form Container */}
        <div className="w-full max-w-sm flex flex-col gap-4 bg-[#a1a1aa] p-8 rounded-lg shadow-inner">
          <Input
            placeholder="Nombre y apellido"
            className="bg-[#e2e8f0] border-transparent"
          />
          <Input
            placeholder="Correo"
            type="email"
            className="bg-[#e2e8f0] border-transparent"
          />
          <Input
            placeholder="Numero de teléfono"
            type="tel"
            className="bg-[#e2e8f0] border-transparent"
          />
        </div>
      </div>
    </section>
  );
}
