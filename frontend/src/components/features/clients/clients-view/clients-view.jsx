"use client";

import { useMemo, useState } from "react";
import { Search, Users } from "lucide-react";

import { PageHeader } from "@/components/layout/PageHeader";
import { Input } from "@/components/ui/input/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table/table";

function ClientAvatar({ name }) {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
      {name.charAt(0).toUpperCase()}
    </div>
  );
}

export default function ClientsView({ clients, totalCount, onSearch }) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredClients = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return clients;
    return clients.filter(
      (client) =>
        client.name.toLowerCase().includes(query) ||
        client.phone.replace(/\s/g, "").includes(query.replace(/\s/g, "")),
    );
  }, [clients, searchQuery]);

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchQuery(value);
    onSearch?.(value);
  };

  return (
    <section className="flex flex-1 flex-col">
      <PageHeader
        icon={<Users className="size-5" />}
        title="Clientes"
      />

      <div className="overflow-hidden rounded-xl border border-border bg-card">
        {/* Sub-header */}
        <div className="flex items-center justify-between border-b border-border bg-muted/50 px-5 py-3">
          <h2 className="text-sm font-semibold tracking-wide text-foreground">
            CLIENTES
          </h2>
          <span className="text-sm text-muted-foreground">
            Total: {totalCount ?? clients.length}
          </span>
        </div>

        {/* Search */}
        <div className="border-b border-border px-5 py-4">
          <div className="relative">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Buscar por nombre o teléfono"
              value={searchQuery}
              onChange={handleSearchChange}
              className="h-10 pl-9"
            />
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow className="border-border bg-muted/50 hover:bg-muted/50">
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">
                CLIENTE
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">
                TELÉFONO
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">
                TURNOS
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-muted-foreground">
                ÚLTIMO
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredClients.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="px-5 py-10 text-center text-muted-foreground"
                >
                  No se encontraron clientes.
                </TableCell>
              </TableRow>
            ) : (
              filteredClients.map((client) => (
                <TableRow
                  key={client.id}
                  className="border-border hover:bg-muted/30"
                >
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <ClientAvatar name={client.name} />
                      <span className="font-medium text-foreground">
                        {client.name}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-muted-foreground">
                    {client.phone}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-muted-foreground">
                    {client.appointments}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-muted-foreground">
                    {client.lastVisit}
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
