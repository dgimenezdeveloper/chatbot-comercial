"use client";

import { useEffect } from "react";

/**
 * ThemeProvider — Aplica la clase del tema (theme-app o theme-landing)
 * directamente a <html> de forma compatible con React 19 y Next.js 16.
 */
export default function ThemeProvider({ theme }) {
  useEffect(() => {
    if (!theme) return;

    // Agregar la clase del tema actual a <html>
    document.documentElement.classList.add(theme);

    // Limpieza al desmontar o cambiar de ruta
    return () => {
      document.documentElement.classList.remove(theme);
    };
  }, [theme]);

  return null;
}