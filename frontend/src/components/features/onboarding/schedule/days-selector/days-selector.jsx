"use client";

import { Checkbox } from "@/components/ui/checkbox/checkbox";
import { Label } from "@/components/ui/label/label";

/**
 * Días disponibles.
 *
 * value: valor guardado en el estado.
 * label: texto mostrado al usuario.
 */
const DAYS = [
  { value: "monday", label: "Lunes" },
  { value: "tuesday", label: "Martes" },
  { value: "wednesday", label: "Miércoles" },
  { value: "thursday", label: "Jueves" },
  { value: "friday", label: "Viernes" },
  { value: "saturday", label: "Sábado" },
  { value: "sunday", label: "Domingo" },
];

/**
 * Selector múltiple de días de atención.
 *
 * selectedDays contiene los días seleccionados:
 *
 * ["monday", "tuesday", "wednesday"]
 *
 * onChange envía el nuevo arreglo al componente padre.
 */
export default function DaysSelector({
  selectedDays = [],
  onChange,
}) {
  /**
   * Agrega o elimina un día del arreglo.
   */
  const handleDayChange = (dayValue, checked) => {
    if (checked) {
      // Agregamos el día si todavía no estaba seleccionado.
      onChange([...selectedDays, dayValue]);

      return;
    }

    // Eliminamos el día cuando se desmarca.
    onChange(
      selectedDays.filter(
        (selectedDay) => selectedDay !== dayValue
      )
    );
  };

  return (
    <fieldset>
      <legend className="text-sm font-semibold text-slate-900">
        Días de atención
      </legend>

      <div className="mt-4 flex flex-wrap gap-2">
        {DAYS.map((day) => {
          const isSelected = selectedDays.includes(day.value);
          const checkboxId = `schedule-day-${day.value}`;

          return (
            /*
             * El Label envuelve toda la tarjeta.
             * Por eso se puede seleccionar haciendo clic
             * en cualquier parte del botón.
             */
            <Label
              key={day.value}
              htmlFor={checkboxId}
              className={`
                flex
                h-10
                min-w-24
                cursor-pointer
                items-center
                justify-between
                gap-3
                rounded-md
                border
                px-3
                text-sm
                font-medium
                transition
                ${
                  isSelected
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:bg-blue-50"
                }
              `}
            >
              {/* agregar aquí el SVG del calendario */}
              <span>{day.label}</span>

              <Checkbox
                id={checkboxId}
                checked={isSelected}
                onCheckedChange={(checked) =>
                  handleDayChange(day.value, checked === true)
                }
                aria-label={`Seleccionar ${day.label}`}
                className="
                  rounded-full
                  border-blue-500
                  data-[state=checked]:border-blue-600
                  data-[state=checked]:bg-blue-600
                "
              />
            </Label>
          );
        })}
      </div>
    </fieldset>
  );
}