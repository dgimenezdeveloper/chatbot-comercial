"use client";

import { useMemo } from "react";

import AppointmentCard from "@/components/features/agenda/appointment-card/appointment-card";
import {
  formatDayLabel,
  formatShortDate,
  parseTimeToMinutes,
  toDateKey,
} from "@/lib/date";
import { cn } from "@/lib/utils";

const HOUR_START = 9;
const HOUR_END = 17;
const ROW_HEIGHT = 64;

function buildHourLabels() {
  return Array.from(
    { length: HOUR_END - HOUR_START + 1 },
    (_, index) => HOUR_START + index,
  );
}

function getAppointmentStyle(startTime, endTime) {
  const startMinutes = parseTimeToMinutes(startTime) - HOUR_START * 60;
  const endMinutes = parseTimeToMinutes(endTime) - HOUR_START * 60;
  const totalMinutes = (HOUR_END - HOUR_START) * 60;

  return {
    top: `${(startMinutes / totalMinutes) * 100}%`,
    height: `${((endMinutes - startMinutes) / totalMinutes) * 100}%`,
  };
}

export default function AgendaWeekGrid({
  weekDays,
  appointments,
  onAppointmentClick,
}) {
  const hours = useMemo(() => buildHourLabels(), []);

  const appointmentsByDay = useMemo(() => {
    return weekDays.reduce((accumulator, day) => {
      const dateKey = toDateKey(day);
      accumulator[dateKey] = appointments.filter(
        (appointment) => appointment.date === dateKey,
      );
      return accumulator;
    }, {});
  }, [appointments, weekDays]);

  const gridHeight = hours.length * ROW_HEIGHT;
  const gridTemplateColumns = `72px repeat(${weekDays.length}, minmax(0, 1fr))`;

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div
        className="grid border-b border-slate-200 bg-slate-50"
        style={{ gridTemplateColumns }}
      >
        <div className="border-r border-slate-200" />
        {weekDays.map((day) => (
          <div
            key={toDateKey(day)}
            className="border-r border-slate-200 px-3 py-3 last:border-r-0"
          >
            <p className="text-sm font-semibold text-slate-800">
              {formatDayLabel(day)}
            </p>
            <p className="text-xs text-slate-500">{formatShortDate(day)}</p>
          </div>
        ))}
      </div>

      <div className="grid" style={{ gridTemplateColumns }}>
        <div className="border-r border-slate-200">
          {hours.map((hour) => (
            <div
              key={hour}
              style={{ height: ROW_HEIGHT }}
              className="flex items-start justify-end border-b border-slate-100 px-2 pt-2 text-xs text-slate-400"
            >
              {String(hour).padStart(2, "0")}:00
            </div>
          ))}
        </div>

        {weekDays.map((day) => {
          const dateKey = toDateKey(day);
          const dayAppointments = appointmentsByDay[dateKey] ?? [];

          return (
            <div
              key={dateKey}
              className="relative border-r border-slate-200 last:border-r-0"
              style={{ height: gridHeight }}
            >
              {hours.map((hour) => (
                <div
                  key={`${dateKey}-${hour}`}
                  style={{ height: ROW_HEIGHT }}
                  className="border-b border-slate-100"
                />
              ))}

              {dayAppointments.map((appointment) => (
                <AppointmentCard
                  key={appointment.id}
                  appointment={appointment}
                  style={getAppointmentStyle(
                    appointment.startTime,
                    appointment.endTime,
                  )}
                  onClick={onAppointmentClick}
                />
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function AgendaLegend() {
  const items = [
    { label: "Confirmado", className: "bg-green-100 border-green-200" },
    { label: "Expirado / Cancelado", className: "bg-slate-100 border-slate-200" },
    { label: "Pausa / Bloqueado", className: "bg-yellow-100 border-yellow-200" },
  ];

  return (
    <div className="mt-4 flex flex-wrap items-center gap-4">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <span
            className={cn("size-4 rounded border", item.className)}
          />
          <span className="text-sm text-slate-600">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
