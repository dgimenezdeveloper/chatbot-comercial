"use client";

import { useState } from "react";
import ProductsView from "@/components/features/products/products-view/products-view";
import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { useProductos } from "@/hooks/useProductos";
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

export default function ProductosPage() {
  const {
    products,
    isLoading,
    isError,
    error,
    refetch,
    createProduct,
    updateProduct,
    deleteProduct,
    isCreating,
    isUpdating,
    isDeleting,
  } = useProductos();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  const [deletingProduct, setDeletingProduct] = useState(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: 3500,
    stock: 10,
    active: true,
  });

  const handleOpenAdd = () => {
    setEditingProduct(null);
    setFormData({
      name: "",
      description: "",
      price: 3500,
      stock: 10,
      active: true,
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (productId) => {
    const prod = products.find((p) => String(p.id) === String(productId));
    if (prod) {
      setEditingProduct(prod);
      setFormData({
        name: prod.name,
        description: prod.description || "",
        price: prod.price || 0,
        stock: prod.stock || 0,
        active: prod.active ?? true,
      });
      setIsModalOpen(true);
    }
  };

  const handleOpenDelete = (productId) => {
    const prod = products.find((p) => String(p.id) === String(productId));
    if (prod) {
      setDeletingProduct(prod);
      setIsDeleteModalOpen(true);
    }
  };

  const handleConfirmDelete = () => {
    if (deletingProduct) {
      deleteProduct(deletingProduct.id, {
        onSuccess: () => {
          setIsDeleteModalOpen(false);
          setDeletingProduct(null);
        },
      });
    }
  };

  const handleToggleStatus = (productId, newActive) => {
    const prod = products.find((p) => String(p.id) === String(productId));
    if (prod) {
      updateProduct({
        id: prod.id,
        name: prod.name,
        description: prod.description,
        price: prod.price,
        stock: prod.stock,
        active: newActive,
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    if (editingProduct) {
      updateProduct(
        { id: editingProduct.id, ...formData, active: editingProduct.active },
        {
          onSuccess: () => {
            setIsModalOpen(false);
          },
        }
      );
    } else {
      createProduct(formData, {
        onSuccess: () => {
          setIsModalOpen(false);
        },
      });
    }
  };

  return (
    <DashboardPageLayout>
      <ProductsView
        products={products}
        isLoading={isLoading}
        isError={isError}
        error={error}
        onRetry={refetch}
        onAddProduct={handleOpenAdd}
        onEditProduct={handleOpenEdit}
        onDeleteProduct={handleOpenDelete}
        onToggleStatus={handleToggleStatus}
      />

      {/* Modal de Crear / Editar Producto */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {editingProduct ? "Editar Producto" : "Nuevo Producto"}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div className="space-y-1.5">
              <Label htmlFor="prod-name">Nombre del producto</Label>
              <Input
                id="prod-name"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="Ej. Pasta Dental Especial / Cepillo"
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="prod-desc">Descripción (opcional)</Label>
              <Textarea
                id="prod-desc"
                value={formData.description}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, description: e.target.value }))
                }
                placeholder="Detalle del producto..."
                className="resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="prod-price">Precio ($)</Label>
                <Input
                  id="prod-price"
                  type="number"
                  min={0}
                  step={100}
                  value={formData.price}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      price: Number(e.target.value),
                    }))
                  }
                  required
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="prod-stock">Stock disponible</Label>
                <Input
                  id="prod-stock"
                  type="number"
                  min={0}
                  value={formData.stock}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      stock: Number(e.target.value),
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
            <DialogTitle>¿Eliminar Producto?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground leading-relaxed">
            ¿Estás seguro de que deseas eliminar el producto <strong className="text-foreground">&quot;{deletingProduct?.name}&quot;</strong>? Se eliminará de tu catálogo y dejará de mostrarse en el chatbot de WhatsApp.
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