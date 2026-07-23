"use client";

import { useMemo, useState } from "react";
import { Pencil, Plus, Scissors, X } from "lucide-react";

import { Badge } from "@/components/ui/badge/badge";
import { Button } from "@/components/ui/button/button";
import { Switch } from "@/components/ui/switch/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table/table";
import { formatCurrency, formatDuration } from "@/lib/format";
import { cn } from "@/lib/utils";

const FILTERS = {
  ALL: "all",
  ACTIVE: "active",
  INACTIVE: "inactive",
};

function FilterTab({ active, count, label, onClick }) {
  return (
    <Button
      type="button"
      variant={active ? "default" : "outline"}
      size="sm"
      onClick={onClick}
      className={cn(
        "min-w-24",
        !active && "border-slate-200 bg-white text-slate-700 hover:bg-slate-50",
      )}
    >
      {label} ({count})
    </Button>
  );
}

export default function ServicesView({
  services,
  onAddService,
  onEditService,
  onDeleteService,
  onToggleStatus,
}) {
  const [filter, setFilter] = useState(FILTERS.ALL);
  const [localServices, setLocalServices] = useState(services);

  const counts = useMemo(
    () => ({
      all: localServices.length,
      active: localServices.filter((service) => service.active).length,
      inactive: localServices.filter((service) => !service.active).length,
    }),
    [localServices],
  );

  const filteredServices = useMemo(() => {
    if (filter === FILTERS.ACTIVE) {
      return localServices.filter((service) => service.active);
    }

    if (filter === FILTERS.INACTIVE) {
      return localServices.filter((service) => !service.active);
    }

    return localServices;
  }, [filter, localServices]);

  const handleToggleStatus = (serviceId, active) => {
    setLocalServices((previousServices) =>
      previousServices.map((service) =>
        service.id === serviceId ? { ...service, active } : service,
      ),
    );
    onToggleStatus?.(serviceId, active);
  };

  const handleDelete = (serviceId) => {
    setLocalServices((previousServices) =>
      previousServices.filter((service) => service.id !== serviceId),
    );
    onDeleteService?.(serviceId);
  };

  return (
    <section className="flex flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-slate-200 pb-6">
        <div className="flex items-center gap-3">
          <Scissors className="size-6 text-slate-800" />
          <h1 className="text-2xl font-bold tracking-wide text-slate-950">
            MIS SERVICIOS
          </h1>
        </div>

        <Button type="button" onClick={onAddService} className="h-10 px-4">
          <Plus data-icon="inline-start" />
          Agregar servicio
        </Button>
      </header>

      <div className="mt-6 flex gap-2">
        <FilterTab
          label="Todos"
          count={counts.all}
          active={filter === FILTERS.ALL}
          onClick={() => setFilter(FILTERS.ALL)}
        />
        <FilterTab
          label="Activos"
          count={counts.active}
          active={filter === FILTERS.ACTIVE}
          onClick={() => setFilter(FILTERS.ACTIVE)}
        />
        <FilterTab
          label="Inactivos"
          count={counts.inactive}
          active={filter === FILTERS.INACTIVE}
          onClick={() => setFilter(FILTERS.INACTIVE)}
        />
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-200 bg-slate-50 hover:bg-slate-50">
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                Servicio
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                Categoría
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                Duración
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                Precio Base
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                Estado
              </TableHead>
              <TableHead className="px-5 text-right text-xs font-semibold tracking-wide text-slate-600">
                Acciones
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredServices.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="px-5 py-10 text-center text-slate-500"
                >
                  No hay servicios en esta categoría.
                </TableCell>
              </TableRow>
            ) : (
              filteredServices.map((service) => (
                <TableRow
                  key={service.id}
                  className="border-slate-200 hover:bg-slate-50/50"
                >
                  <TableCell className="px-5 py-4 font-medium text-slate-900">
                    {service.name}
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                      {service.category}
                    </Badge>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-slate-600">
                    {formatDuration(service.durationMinutes)}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-slate-600">
                    {formatCurrency(service.basePrice)}
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={service.active}
                        onCheckedChange={(checked) =>
                          handleToggleStatus(service.id, checked)
                        }
                      />
                      <span
                        className={cn(
                          "text-xs font-semibold uppercase",
                          service.active ? "text-slate-800" : "text-slate-400",
                        )}
                      >
                        {service.active ? "ON" : "OFF"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => onEditService?.(service.id)}
                        aria-label={`Editar ${service.name}`}
                      >
                        <Pencil />
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => handleDelete(service.id)}
                        aria-label={`Eliminar ${service.name}`}
                        className="text-slate-500 hover:text-destructive"
                      >
                        <X />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </section>
  );
}
