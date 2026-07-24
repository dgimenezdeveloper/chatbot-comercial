"use client";

import { Button } from "@/components/ui/button/button";
import { Checkbox } from "@/components/ui/checkbox/checkbox";
import { Label } from "@/components/ui/label/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select/select";

import FieldError from "@/components/features/onboarding/shared/field-error/field-error";
import DaysSelector from "@/components/features/onboarding/schedule/days-selector/days-selector";

/**
 * Horarios disponibles en los selectores.
 *
 * Se generan intervalos de 30 minutos:
 * 08:00, 08:30, 09:00, 09:30, etc.
 */
const TIME_OPTIONS = [
  "07:00",
  "07:30",
  "08:00",
  "08:30",
  "09:00",
  "09:30",
  "10:00",
  "10:30",
  "11:00",
  "11:30",
  "12:00",
  "12:30",
  "13:00",
  "13:30",
  "14:00",
  "14:30",
  "15:00",
  "15:30",
  "16:00",
  "16:30",
  "17:00",
  "17:30",
  "18:00",
  "18:30",
  "19:00",
  "19:30",
  "20:00",
  "20:30",
  "21:00",
];

/**
 * Convierte "09:00" en "09:00 hs".
 */
function formatTimeLabel(time) {
  return `${time} hs`;
}

/**
 * Segundo paso del onboarding.
 
 */
export default function ScheduleStep({
  data,
  errors = {},
  onFieldChange,
  onBack,
  onContinue,
}) {
  return (
    <section className="flex flex-1 flex-col">
      {/* Encabezado */}
      <header className="border-b border-border pb-6">
        <h1 className="text-2xl font-bold text-foreground">
          Configurá tus horarios de atención
        </h1>

        <p className="mt-2 text-sm text-muted-foreground">
          Definí en qué días y horarios atendés clientes. Podés
          modificarlos después.
        </p>
      </header>

      {/* Contenido principal */}
      <div className="flex-1 py-8">
        <div className="max-w-4xl space-y-8">
          {/* Selección de días */}
          <div>
            <DaysSelector
              selectedDays={data.days}
              onChange={(days) =>
                onFieldChange("days", days)
              }
            />

            <FieldError message={errors.days} />
          </div>

          {/* Horarios de apertura y cierre */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Hora de apertura */}
            <div>
              <Label
                htmlFor="opening-time"
                className="font-semibold text-foreground"
              >
                Horario de apertura
              </Label>

              <Select
                value={data.open}
                onValueChange={(value) =>
                  onFieldChange("open", value)
                }
              >
                <SelectTrigger
                  id="opening-time"
                  className="mt-3 h-11 w-full"
                  aria-invalid={Boolean(errors.open)}
                >
                  <SelectValue placeholder="Seleccioná una hora" />
                </SelectTrigger>

                <SelectContent>
                  {TIME_OPTIONS.map((time) => (
                    <SelectItem key={time} value={time}>
                      {formatTimeLabel(time)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <FieldError message={errors.open} />
            </div>

            {/* Hora de cierre */}
            <div>
              <Label
                htmlFor="closing-time"
                className="font-semibold text-foreground"
              >
                Horario de cierre
              </Label>

              <Select
                value={data.close}
                onValueChange={(value) =>
                  onFieldChange("close", value)
                }
              >
                <SelectTrigger
                  id="closing-time"
                  className="mt-3 h-11 w-full"
                  aria-invalid={Boolean(errors.close)}
                >
                  <SelectValue placeholder="Seleccioná una hora" />
                </SelectTrigger>

                <SelectContent>
                  {TIME_OPTIONS.map((time) => (
                    <SelectItem key={time} value={time}>
                      {formatTimeLabel(time)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <FieldError message={errors.close} />
            </div>
          </div>

          {/* Pausa del mediodía */}
          <div className="flex items-start gap-3">
            <Checkbox
              id="lunch-break"
              checked={data.lunchBreak}
              onCheckedChange={(checked) =>
                onFieldChange(
                  "lunchBreak",
                  checked === true
                )
              }
            />

            <div>
              <Label
                htmlFor="lunch-break"
                className="cursor-pointer font-normal text-muted-foreground"
              >
                Habilitar pausa del mediodía
              </Label>

              <p className="mt-1 text-xs text-muted-foreground">
                Ejemplo: de 13:00 a 14:00.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Acciones inferiores */}
      <footer className="flex items-center justify-between border-t border-border pt-6">
        <Button type="button" variant="outline" onClick={onBack}>
          <span aria-hidden="true">←</span>
          Volver
        </Button>

        <Button type="button" onClick={onContinue} size="lg" className="min-w-52">
          Guardar y continuar
          <span aria-hidden="true">→</span>
        </Button>
      </footer>
    </section>
  );
}