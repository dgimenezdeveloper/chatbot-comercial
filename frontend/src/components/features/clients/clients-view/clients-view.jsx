"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { ClientesIcon } from "@/components/icons/ClientesIcon";

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
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-800 text-sm font-medium text-white">
      {name.charAt(0).toUpperCase()}
    </div>
  );
}

export default function ClientsView({
  clients,
  totalCount,
  onSearch,
}) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredClients = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    if (!query) {
      return clients;
    }

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
      <header className="border-b border-slate-200 pb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <ClientesIcon className="size-6 text-slate-800" />
            <h1 className="text-2xl font-bold tracking-wide text-slate-950">
              CLIENTES
            </h1>
          </div>
        </div>
      </header>

      <div className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white">
        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-5 py-3">
          <h2 className="text-sm font-semibold tracking-wide text-slate-700">
            CLIENTES
          </h2>
          <span className="text-sm text-slate-500">
            Total: {totalCount ?? clients.length}
          </span>
        </div>

        <div className="border-b border-slate-200 px-5 py-4">
          <div className="relative">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400" />
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
            <TableRow className="border-slate-200 bg-slate-50 hover:bg-slate-50">
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                CLIENTE
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                TELÉFONO
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                TURNOS
              </TableHead>
              <TableHead className="px-5 text-xs font-semibold tracking-wide text-slate-600">
                ÚLTIMO
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredClients.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="px-5 py-10 text-center text-slate-500"
                >
                  No se encontraron clientes.
                </TableCell>
              </TableRow>
            ) : (
              filteredClients.map((client) => (
                <TableRow
                  key={client.id}
                  className="border-slate-200 hover:bg-slate-50/50"
                >
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <ClientAvatar name={client.name} />
                      <span className="font-medium text-slate-900">
                        {client.name}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-slate-600">
                    {client.phone}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-slate-600">
                    {client.appointments}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-slate-600">
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
