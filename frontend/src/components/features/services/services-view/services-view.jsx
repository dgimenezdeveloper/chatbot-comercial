"use client";

import { useMemo, useState } from "react";
import { Pencil, Plus, Scissors, X } from "lucide-react";

import { PageHeader } from "@/components/layout/PageHeader";
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
        !active && "border-border bg-card text-foreground hover:bg-muted",
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
      active: localServices.filter((s) => s.active).length,
      inactive: localServices.filter((s) => !s.active).length,
    }),
    [localServices],
  );

  const filteredServices = useMemo(() => {
    if (filter === FILTERS.ACTIVE) return localServices.filter((s) => s.active);
    if (filter === FILTERS.INACTIVE) return localServices.filter((s) => !s.active);
    return localServices;
  }, [filter, localServices]);

  const handleToggleStatus = (serviceId, active) => {
    setLocalServices((prev) =>
      prev.map((s) => (s.id === serviceId ? { ...s, active } : s)),
    );
    onToggleStatus?.(serviceId, active);
  };

  const handleDelete = (serviceId) => {
    setLocalServices((prev) => prev.filter((s) => s.id !== serviceId));
    onDeleteService?.(serviceId);
  };

  return (
    <section className="flex flex-1 flex-col">
      <PageHeader
        icon={<Scissors className="size-5" />}
        title="Mis Servicios"
        action={
          <Button type="button" onClick={onAddService} className="h-10 px-4">
            <Plus data-icon="inline-start" />
            Agregar servicio
          </Button>
        }
      />

      {/* Filter tabs */}
      <div className="mb-6 flex gap-2">
        <FilterTab label="Todos" count={counts.all} active={filter === FILTERS.ALL} onClick={() => setFilter(FILTERS.ALL)} />
        <FilterTab label="Activos" count={counts.active} active={filter === FILTERS.ACTIVE} onClick={() => setFilter(FILTERS.ACTIVE)} />
        <FilterTab label="Inactivos" count={counts.inactive} active={filter === FILTERS.INACTIVE} onClick={() => setFilter(FILTERS.INACTIVE)} />
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="border-border bg-muted/50 hover:bg-muted/50">
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Servicio</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Categoría</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Duración</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Precio Base</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Estado</TableHead>
              <TableHead className="px-5 text-right text-xs font-semibold tracking-wide text-muted-foreground">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredServices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="px-5 py-10 text-center text-muted-foreground">
                  No hay servicios en esta categoría.
                </TableCell>
              </TableRow>
            ) : (
              filteredServices.map((service) => (
                <TableRow key={service.id} className="border-border hover:bg-muted/30">
                  <TableCell className="px-5 py-4 font-medium text-foreground">{service.name}</TableCell>
                  <TableCell className="px-5 py-4">
                    <Badge variant="secondary">{service.category}</Badge>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-muted-foreground">{formatDuration(service.durationMinutes)}</TableCell>
                  <TableCell className="px-5 py-4 text-muted-foreground">{formatCurrency(service.basePrice)}</TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={service.active}
                        onCheckedChange={(checked) => handleToggleStatus(service.id, checked)}
                      />
                      <span className={cn("text-xs font-semibold uppercase", service.active ? "text-foreground" : "text-muted-foreground")}>
                        {service.active ? "ON" : "OFF"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <Button type="button" variant="ghost" size="icon-sm" onClick={() => onEditService?.(service.id)} aria-label={`Editar ${service.name}`}>
                        <Pencil />
                      </Button>
                      <Button
                        type="button" variant="ghost" size="icon-sm"
                        onClick={() => handleDelete(service.id)}
                        aria-label={`Eliminar ${service.name}`}
                        className="text-muted-foreground hover:text-destructive"
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
