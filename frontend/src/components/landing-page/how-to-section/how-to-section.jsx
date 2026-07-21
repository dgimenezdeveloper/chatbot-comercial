export default function HowToSection() {
  return (
    <section className="w-full bg-[#f8fafc] py-20 px-6">
      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12">
        {/* Col 1 */}
        <div className="flex flex-col gap-6">
          <h3 className="text-2xl font-semibold text-[#5db2d6] mb-2 text-center md:text-left">
            ¿Cómo lo uso?
          </h3>
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-8 min-h-[300px]">
            <div className="text-[#5db2d6] font-medium">Paso 1</div>
            <div className="text-[#5db2d6] font-medium">Paso 2</div>
            <div className="text-[#5db2d6] font-medium">Paso 3</div>
          </div>
        </div>

        {/* Col 2 */}
        <div className="flex flex-col gap-6">
          <h3 className="text-2xl font-semibold text-[#5db2d6] mb-2 text-center md:text-left">
            ¿Como lo vinculo a mis redes sociales?
          </h3>
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-8 min-h-[300px]">
            <div className="text-[#5db2d6] font-medium">Paso 1</div>
            <div className="text-[#5db2d6] font-medium">Paso 2</div>
            <div className="text-[#5db2d6] font-medium">Paso 3</div>
          </div>
        </div>
      </div>
    </section>
  );
}
