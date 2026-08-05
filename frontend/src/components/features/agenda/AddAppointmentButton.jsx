"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button/button";
import { Plus } from "lucide-react";
import { CreateAppointmentDialog } from "./CreateAppointmentDialog";

export function AddAppointmentButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setIsOpen(true)}>
        <Plus className="size-4 mr-2" />
        Agregar turno manual
      </Button>
      <CreateAppointmentDialog open={isOpen} onOpenChange={setIsOpen} />
    </>
  );
}