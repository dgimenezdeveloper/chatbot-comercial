"use client";

import { useState } from "react";
import ServicesView from "@/components/features/services/services-view/services-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { useServicios } from "@/hooks/useServicios";
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
import { Textarea } from "@/components/ui/textarea/textarea";

export default function ServiciosPage() {
  const {
    services,
    isLoading,
    isError,
    error,
    refetch,
    createService,
    updateService,
    deleteService,
    isCreating,
    isUpdating,
    isDeleting,
  } = useServicios();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);

  const [deletingService, setDeletingService] = useState(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    durationMinutes: 30,
    basePrice: 5000,
  });

  const handleOpenAdd = () => {
    setEditingService(null);
    setFormData({
      name: "",
      description: "",
      durationMinutes: 30,
      basePrice: 5000,
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (serviceId) => {
    const svc = services.find((s) => String(s.id) === String(serviceId));
    if (svc) {
      setEditingService(svc);
      setFormData({
        name: svc.name,
        description: svc.description || "",
        durationMinutes: svc.durationMinutes || 30,
        basePrice: svc.basePrice || 0,
      });
      setIsModalOpen(true);
    }
  };

  const handleOpenDelete = (serviceId) => {
    const svc = services.find((s) => String(s.id) === String(serviceId));
    if (svc) {
      setDeletingService(svc);
      setIsDeleteModalOpen(true);
    }
  };

  const handleConfirmDelete = () => {
    if (deletingService) {
      deleteService(deletingService.id, {
        onSuccess: () => {
          setIsDeleteModalOpen(false);
          setDeletingService(null);
        },
      });
    }
  };

  const handleToggleStatus = (serviceId, newActive) => {
    const svc = services.find((s) => String(s.id) === String(serviceId));
    if (svc) {
      updateService({
        id: svc.id,
        name: svc.name,
        description: svc.description,
        durationMinutes: svc.durationMinutes,
        basePrice: svc.basePrice,
        active: newActive,
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    if (editingService) {
      updateService(
        { id: editingService.id, ...formData, active: editingService.active },
        {
          onSuccess: () => {
            setIsModalOpen(false);
          },
        }
      );
    } else {
      createService(formData, {
        onSuccess: () => {
          setIsModalOpen(false);
        },
      });
    }
  };

  return (
    <DashboardPageLayout>
      <ServicesView
        services={services}
        isLoading={isLoading}
        isError={isError}
        error={error}
        onRetry={refetch}
        onAddService={handleOpenAdd}
        onEditService={handleOpenEdit}
        onDeleteService={handleOpenDelete}
        onToggleStatus={handleToggleStatus}
      />

      {/* Modal de Crear / Editar Servicio */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {editingService ? "Editar Servicio" : "Nuevo Servicio"}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div className="space-y-1.5">
              <Label htmlFor="svc-name">Nombre del servicio</Label>
              <Input
                id="svc-name"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="Ej. Limpieza Dental / Consulta"
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="svc-desc">Descripción (opcional)</Label>
              <Textarea
                id="svc-desc"
                value={formData.description}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, description: e.target.value }))
                }
                placeholder="Detalle breve del servicio..."
                className="resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="svc-duration">Duración (min)</Label>
                <Input
                  id="svc-duration"
                  type="number"
                  min={5}
                  step={5}
                  value={formData.durationMinutes}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      durationMinutes: Number(e.target.value),
                    }))
                  }
                  required
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="svc-price">Precio ($)</Label>
                <Input
                  id="svc-price"
                  type="number"
                  min={0}
                  step={100}
                  value={formData.basePrice}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      basePrice: Number(e.target.value),
                    }))
                  }
                  required
                />
              </div>
            </div>

            <DialogFooter className="pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsModalOpen(false)}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isCreating || isUpdating}>
                {isCreating || isUpdating ? "Guardando..." : "Guardar"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Confirmación de Eliminación */}
      <Dialog open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle>¿Eliminar Servicio?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground leading-relaxed">
            ¿Estás seguro de que deseas eliminar el servicio <strong className="text-foreground">&quot;{deletingService?.name}&quot;</strong>? Se eliminará de tu catálogo y dejará de estar disponible.
          </div>
          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsDeleteModalOpen(false)}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={isDeleting}
            >
              {isDeleting ? "Eliminando..." : "Eliminar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardPageLayout>
  );
}