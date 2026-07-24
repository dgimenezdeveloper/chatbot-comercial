"use client";

import { useMemo, useState } from "react";
import { CalendarDays, ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";

import AgendaWeekGrid, {
  AgendaLegend,
} from "@/components/features/agenda/agenda-week-grid/agenda-week-grid";
import { Button } from "@/components/ui/button/button";
import {
  addDays,
  formatWeekRange,
  getWeekDays,
  toDateKey,
} from "@/lib/date";
import { cn } from "@/lib/utils";

const VIEW_MODES = {
  TODAY: "today",
  DAY: "day",
  WEEK: "week",
  MONTH: "month",
};

const viewModeLabels = {
  [VIEW_MODES.TODAY]: "Hoy",
  [VIEW_MODES.DAY]: "Día",
  [VIEW_MODES.WEEK]: "Semana",
  [VIEW_MODES.MONTH]: "Mes",
};

function ViewModeButton({ active, label, onClick }) {
  return (
    <Button
      type="button"
      variant={active ? "default" : "outline"}
      size="sm"
      onClick={onClick}
      className={cn(
        "min-w-16",
        !active && "border-border bg-card text-foreground hover:bg-muted",
      )}
    >
      {label}
    </Button>
  );
}

export default function AgendaView({
  appointments,
  initialDate = new Date("2026-07-22"),
  onNewAppointment,
  onAppointmentClick,
}) {
  const [viewMode, setViewMode] = useState(VIEW_MODES.WEEK);
  const [currentDate, setCurrentDate] = useState(initialDate);

  const weekDays = useMemo(() => {
    if (viewMode === VIEW_MODES.DAY || viewMode === VIEW_MODES.TODAY) {
      return [currentDate];
    }

    return getWeekDays(currentDate);
  }, [currentDate, viewMode]);

  const visibleAppointments = useMemo(() => {
    const visibleDateKeys = new Set(weekDays.map((day) => toDateKey(day)));

    return appointments.filter((appointment) =>
      visibleDateKeys.has(appointment.date),
    );
  }, [appointments, weekDays]);

  const rangeLabel = useMemo(() => {
    if (viewMode === VIEW_MODES.DAY || viewMode === VIEW_MODES.TODAY) {
      return formatWeekRange(currentDate, currentDate);
    }

    if (viewMode === VIEW_MODES.MONTH) {
      const monthLabel = currentDate.toLocaleDateString("es-AR", {
        month: "long",
        year: "numeric",
      });
      return monthLabel.charAt(0).toUpperCase() + monthLabel.slice(1);
    }

    const weekStart = weekDays[0];
    const weekEnd = weekDays[weekDays.length - 1];
    return formatWeekRange(weekStart, weekEnd);
  }, [currentDate, viewMode, weekDays]);

  const handlePrevious = () => {
    const offset =
      viewMode === VIEW_MODES.WEEK
        ? -7
        : viewMode === VIEW_MODES.MONTH
          ? -30
          : -1;

    setCurrentDate((previousDate) => addDays(previousDate, offset));
  };

  const handleNext = () => {
    const offset =
      viewMode === VIEW_MODES.WEEK
        ? 7
        : viewMode === VIEW_MODES.MONTH
          ? 30
          : 1;

    setCurrentDate((previousDate) => addDays(previousDate, offset));
  };

  const handleToday = () => {
    setViewMode(VIEW_MODES.TODAY);
    setCurrentDate(new Date());
  };

  return (
    <section className="flex flex-1 flex-col">
      <PageHeader
        icon={<CalendarDays className="size-5" />}
        title="Agenda Semanal"
        action={
          <Button type="button" onClick={onNewAppointment} className="h-10 px-4">
            <Plus data-icon="inline-start" />
            Nuevo turno
          </Button>
        }
      />

      <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="icon-sm"
            onClick={handlePrevious}
            aria-label="Periodo anterior"
          >
            <ChevronLeft />
          </Button>

          <span className="min-w-44 text-center text-sm font-medium text-foreground">
            {rangeLabel}
          </span>

          <Button
            type="button"
            variant="outline"
            size="icon-sm"
            onClick={handleNext}
            aria-label="Periodo siguiente"
          >
            <ChevronRight />
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          <ViewModeButton
            label={viewModeLabels[VIEW_MODES.TODAY]}
            active={viewMode === VIEW_MODES.TODAY}
            onClick={handleToday}
          />
          <ViewModeButton
            label={viewModeLabels[VIEW_MODES.DAY]}
            active={viewMode === VIEW_MODES.DAY}
            onClick={() => setViewMode(VIEW_MODES.DAY)}
          />
          <ViewModeButton
            label={viewModeLabels[VIEW_MODES.WEEK]}
            active={viewMode === VIEW_MODES.WEEK}
            onClick={() => setViewMode(VIEW_MODES.WEEK)}
          />
          <ViewModeButton
            label={viewModeLabels[VIEW_MODES.MONTH]}
            active={viewMode === VIEW_MODES.MONTH}
            onClick={() => setViewMode(VIEW_MODES.MONTH)}
          />
        </div>
      </div>

      <div className="mt-6">
        {viewMode === VIEW_MODES.MONTH ? (
          <div className="rounded-xl border border-border bg-card px-6 py-16 text-center text-muted-foreground">
            Vista mensual disponible próximamente.
          </div>
        ) : (
          <AgendaWeekGrid
            weekDays={weekDays}
            appointments={visibleAppointments}
            onAppointmentClick={onAppointmentClick}
          />
        )}
      </div>

      <AgendaLegend />
    </section>
  );
}
