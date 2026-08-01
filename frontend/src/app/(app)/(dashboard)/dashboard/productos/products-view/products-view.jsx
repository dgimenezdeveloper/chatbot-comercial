"use client";

import { useMemo, useState } from "react";
import { Loader2, Package, Pencil, Plus, X } from "lucide-react";

import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/badge/badge";
import { Button } from "@/components/ui/button/button";
import { ErrorState } from "@/components/ui/error-state/error-state";
import { Switch } from "@/components/ui/switch/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table/table";
import { formatCurrency } from "@/lib/format";
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

export default function ProductsView({
  products = [],
  isLoading,
  isError,
  error,
  onRetry,
  onAddProduct,
  onEditProduct,
  onDeleteProduct,
}) {
  const [filter, setFilter] = useState(FILTERS.ALL);

  const counts = useMemo(
    () => ({
      all: products.length,
      active: products.filter((p) => p.active).length,
      inactive: products.filter((p) => !p.active).length,
    }),
    [products],
  );

  const filteredProducts = useMemo(() => {
    if (filter === FILTERS.ACTIVE) return products.filter((p) => p.active);
    if (filter === FILTERS.INACTIVE) return products.filter((p) => !p.active);
    return products;
  }, [filter, products]);

  if (isLoading) {
    return (
      <section className="flex flex-1 flex-col items-center justify-center gap-3 py-20">
        <Loader2 className="size-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Cargando productos...</p>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="flex flex-1 flex-col">
        <ErrorState message={error?.message} onRetry={onRetry} />
      </section>
    );
  }

  return (
    <section className="flex flex-1 flex-col">
      <PageHeader
        icon={<Package className="size-5" />}
        title="Catálogo de Productos"
        action={
          <Button type="button" onClick={onAddProduct} className="h-10 px-4">
            <Plus data-icon="inline-start" />
            Agregar producto
          </Button>
        }
      />

      <div className="mb-6 flex gap-2">
        <FilterTab label="Todos" count={counts.all} active={filter === FILTERS.ALL} onClick={() => setFilter(FILTERS.ALL)} />
        <FilterTab label="Activos" count={counts.active} active={filter === FILTERS.ACTIVE} onClick={() => setFilter(FILTERS.ACTIVE)} />
        <FilterTab label="Inactivos" count={counts.inactive} active={filter === FILTERS.INACTIVE} onClick={() => setFilter(FILTERS.INACTIVE)} />
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="border-border bg-muted/50 hover:bg-muted/50">
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Producto</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Stock</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Precio</TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Estado</TableHead>
              <TableHead className="px-5 text-right text-xs font-semibold tracking-wide text-muted-foreground">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredProducts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="px-5 py-10 text-center text-muted-foreground">
                  No hay productos en este catálogo.
                </TableCell>
              </TableRow>
            ) : (
              filteredProducts.map((product) => (
                <TableRow key={product.id} className="border-border hover:bg-muted/30">
                  <TableCell className="px-5 py-4 font-medium text-foreground">
                    <div>
                      <p>{product.name}</p>
                      {product.description && (
                        <p className="text-xs text-muted-foreground">{product.description}</p>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <Badge variant={product.stock > 0 ? "secondary" : "destructive"}>
                      {product.stock} unidades
                    </Badge>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-muted-foreground">{formatCurrency(product.price)}</TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <Switch checked={product.active} disabled />
                      <span className={cn("text-xs font-semibold uppercase", product.active ? "text-foreground" : "text-muted-foreground")}>
                        {product.active ? "ON" : "OFF"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <Button type="button" variant="ghost" size="icon-sm" onClick={() => onEditProduct?.(product.id)} aria-label={`Editar ${product.name}`}>
                        <Pencil />
                      </Button>
                      <Button
                        type="button" variant="ghost" size="icon-sm"
                        onClick={() => onDeleteProduct?.(product.id)}
                        aria-label={`Eliminar ${product.name}`}
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