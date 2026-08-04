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
import { usePedidos } from "@/hooks/usePedidos";

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
  onToggleStatus,
}) {
  const [mainTab, setMainTab] = useState("catalog");
  const [filter, setFilter] = useState(FILTERS.ALL);

  const { pedidos, isLoading: isLoadingPedidos, updateEstado } = usePedidos();

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
        title="Gestión de Productos"
        action={
          mainTab === "catalog" && (
            <Button type="button" onClick={onAddProduct} className="h-10 px-4">
              <Plus data-icon="inline-start" />
              Agregar producto
            </Button>
          )
        }
      />

      <div className="flex gap-6 border-b border-border mb-6">
        <button
          type="button"
          className={cn(
            "pb-3 text-sm font-medium transition-colors relative cursor-pointer",
            mainTab === "catalog" ? "text-foreground" : "text-muted-foreground hover:text-foreground"
          )}
          onClick={() => setMainTab("catalog")}
        >
          Catálogo de Productos
          {mainTab === "catalog" && (
            <span className="absolute bottom-0 left-0 w-full h-0.5 bg-primary rounded-t-full" />
          )}
        </button>
        <button
          type="button"
          className={cn(
            "pb-3 text-sm font-medium transition-colors relative flex items-center gap-2 cursor-pointer",
            mainTab === "orders" ? "text-foreground" : "text-muted-foreground hover:text-foreground"
          )}
          onClick={() => setMainTab("orders")}
        >
          Pedidos y Reservas
          {pedidos.filter((p) => p.status === "pendiente").length > 0 && (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white">
              {pedidos.filter((p) => p.status === "pendiente").length}
            </span>
          )}
          {mainTab === "orders" && (
            <span className="absolute bottom-0 left-0 w-full h-0.5 bg-primary rounded-t-full" />
          )}
        </button>
      </div>

      {mainTab === "catalog" && (
        <>
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
                          <Switch
                            checked={product.active}
                            onCheckedChange={(checked) => onToggleStatus?.(product.id, checked)}
                          />
                          <span className={cn("text-xs font-semibold uppercase", product.active ? "text-foreground" : "text-muted-foreground")}>
                            {product.active ? "ON" : "OFF"}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="px-5 py-4">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => onEditProduct?.(product.id)}
                            aria-label={`Editar ${product.name}`}
                            title="Editar producto"
                          >
                            <Pencil />
                          </Button>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => onDeleteProduct?.(product.id)}
                            aria-label={`Eliminar ${product.name}`}
                            title="Eliminar producto"
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
        </>
      )}

      {mainTab === "orders" && (
        <div className="overflow-hidden rounded-xl border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow className="border-border bg-muted/50 hover:bg-muted/50">
                <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Fecha</TableHead>
                <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Cliente</TableHead>
                <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Productos</TableHead>
                <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Total</TableHead>
                <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">Estado</TableHead>
                <TableHead className="px-5 text-right text-xs font-semibold tracking-wide text-muted-foreground">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoadingPedidos ? (
                <TableRow>
                  <TableCell colSpan={6} className="px-5 py-10 text-center text-muted-foreground">
                    <Loader2 className="size-6 animate-spin mx-auto mb-2 text-primary" />
                    Cargando pedidos...
                  </TableCell>
                </TableRow>
              ) : pedidos.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="px-5 py-10 text-center text-muted-foreground">
                    No hay pedidos registrados.
                  </TableCell>
                </TableRow>
              ) : (
                pedidos.map((pedido) => (
                  <TableRow key={pedido.id} className="border-border hover:bg-muted/30">
                    <TableCell className="px-5 py-4 text-muted-foreground text-sm">
                      {new Date(pedido.created_at).toLocaleDateString("es-AR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                    </TableCell>
                    <TableCell className="px-5 py-4 font-medium text-foreground">
                      <div>
                        <p>{pedido.user_name}</p>
                        <p className="text-xs text-muted-foreground">{pedido.user_phone}</p>
                      </div>
                    </TableCell>
                    <TableCell className="px-5 py-4 text-muted-foreground text-sm">
                      <ul className="list-disc list-inside">
                        {pedido.items_json?.map((item, idx) => (
                          <li key={idx}>{item.name}</li>
                        ))}
                      </ul>
                    </TableCell>
                    <TableCell className="px-5 py-4 font-medium text-foreground">
                      {formatCurrency(pedido.total_price)}
                    </TableCell>
                    <TableCell className="px-5 py-4">
                      <Badge variant={pedido.status === "entregado" ? "default" : pedido.status === "cancelado" ? "destructive" : "secondary"}>
                        {pedido.status.charAt(0).toUpperCase() + pedido.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="px-5 py-4">
                      <div className="flex items-center justify-end gap-2">
                        {pedido.status === "pendiente" && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              className="border-green-500 text-green-600 hover:bg-green-50"
                              onClick={() => updateEstado({ id: pedido.id, estado: "entregado" })}
                            >
                              Entregado
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-destructive hover:bg-destructive/10"
                              onClick={() => updateEstado({ id: pedido.id, estado: "cancelado" })}
                            >
                              Cancelar
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </section>
  );
}