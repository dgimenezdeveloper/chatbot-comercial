"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog/dialog";
import { Button } from "@/components/ui/button/button";
import { Input } from "@/components/ui/input/input";
import { Label } from "@/components/ui/label/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select/select";
import { useServicios } from "@/hooks/useServicios";
import { useTurnos } from "@/hooks/useTurnos";

export function CreateAppointmentDialog({ open, onOpenChange }) {
  const router = useRouter();
  const { services, isLoading: isLoadingServices } = useServicios();
  const { createAppointment, isCreating } = useTurnos();

  const [formData, setFormData] = useState({
    nombre_cliente: "",
    telefono: "",
    servicio_id: "",
    fecha: "",
    hora: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!formData.nombre_cliente || !formData.telefono || !formData.servicio_id || !formData.fecha || !formData.hora) {
      setError("Todos los campos son obligatorios.");
      return;
    }

    createAppointment(
      {
        nombre_cliente: formData.nombre_cliente,
        telefono: formData.telefono,
        servicio_id: Number(formData.servicio_id),
        fecha: formData.fecha,
        hora: formData.hora,
      },
      {
        onSuccess: () => {
          onOpenChange(false);
          setFormData({ nombre_cliente: "", telefono: "", servicio_id: "", fecha: "", hora: "" });
          router.refresh(); // Fuerza la actualización de los Server Components (Dashboard)
        },
        onError: (err) => {
          setError(err.message || "Ocurrió un error al agendar el turno.");
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Agregar Turno Manual</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          {error && (
            <div className="text-sm font-medium text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="nombre_cliente">Nombre del Cliente</Label>
            <Input
              id="nombre_cliente"
              placeholder="Ej. Juan Pérez"
              value={formData.nombre_cliente}
              onChange={(e) => setFormData({ ...formData, nombre_cliente: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="telefono">Teléfono del Cliente</Label>
            <Input
              id="telefono"
              placeholder="Ej. 5491123456789"
              value={formData.telefono}
              onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="servicio">Servicio</Label>
            <Select
              value={formData.servicio_id}
              onValueChange={(v) => setFormData({ ...formData, servicio_id: v })}
            >
              <SelectTrigger id="servicio">
                <SelectValue placeholder={isLoadingServices ? "Cargando..." : "Selecciona un servicio"} />
              </SelectTrigger>
              <SelectContent>
                {services
                  .filter((s) => s.active)
                  .map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      {s.name}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="fecha">Fecha</Label>
              <Input
                id="fecha"
                type="date"
                value={formData.fecha}
                onChange={(e) => setFormData({ ...formData, fecha: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="hora">Hora</Label>
              <Input
                id="hora"
                type="time"
                value={formData.hora}
                onChange={(e) => setFormData({ ...formData, hora: e.target.value })}
              />
            </div>
          </div>

          <DialogFooter className="pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isCreating}>
              {isCreating ? "Guardando..." : "Guardar Turno"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}