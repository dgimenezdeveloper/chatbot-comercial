"use client";
import { useState } from "react";

const serviciosMock = [
  { id: 1, emoji: "✂️", nombre: "Corte de Cabello", duracion: "30 min", precio: "$15.000" },
  { id: 2, emoji: "🎨", nombre: "Coloración", duracion: "90 min", precio: "$30.000" },
  { id: 3, emoji: "💆", nombre: "Tratamiento", duracion: "45 min", precio: "$20.000" },
  { id: 4, emoji: "💅", nombre: "Manicura", duracion: "40 min", precio: "$12.000" },
  { id: 5, emoji: "🧖", nombre: "Facial", duracion: "60 min", precio: "$25.000" },
  { id: 6, emoji: "💇", nombre: "Peinado", duracion: "50 min", precio: "$18.000" },
];

export default function ServiciosPage() {
  const [verMas, setVerMas] = useState(false);

  const serviciosVisibles = verMas ? serviciosMock : serviciosMock.slice(0, 5);

  return (
    <div className="flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-6">Servicios</h1>

      {serviciosMock.length === 0 ? (
        <p className="text-gray-500">
          Actualmente no tenemos servicios disponibles. 
          Contactá con nosotros para más info.
        </p>
      ) : (
        <>
          {serviciosVisibles.map((servicio) => (
            <div
              key={servicio.id}
              className="border rounded-lg p-4 mb-4 w-80"
            >
              <h2 className="font-semibold">
                {servicio.id}. {servicio.emoji} {servicio.nombre}
              </h2>
              <p className="text-sm text-gray-500">{servicio.duracion}</p>
              <p className="font-bold">{servicio.precio}</p>
              <button className="mt-2 bg-black text-white px-4 py-1 rounded">
                Reservar
              </button>
            </div>
          ))}

          {serviciosMock.length > 5 && (
            <button
              onClick={() => setVerMas(!verMas)}
              className="text-blue-500 underline mb-4"
            >
              {verMas ? "Ver menos" : "Ver más"}
            </button>
          )}
        </>
      )}

      <button className="mt-4 border px-6 py-2 rounded-lg">
        ← Volver al menú
      </button>
    </div>
  );
}