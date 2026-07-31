/**
 * Cliente HTTP Axios configurado para el backend de chatbot-comercial.
 *
 * Sanitiza automáticamente el protocolo HTTPS para evitar errores de Mixed Content
 * e inyecta el token JWT firmado de NextAuth en cada petición.
 *
 * @module lib/api-client
 */

import axios from "axios";
import { getSession } from "next-auth/react";

/**
 * Resuelve y sanitiza la URL base de la API garantizando HTTPS en producción.
 */
const getBaseUrl = () => {
  let url = process.env.NEXT_PUBLIC_API_URL || "https://pymebot.azurewebsites.net/api/v1";

  if (typeof window !== "undefined") {
    // Si la página se carga sobre HTTPS, forzamos la API a HTTPS (evita bloqueos de Mixed Content)
    if (window.location.protocol === "https:" && url.startsWith("http://") && !url.includes("localhost")) {
      url = url.replace("http://", "https://");
    }
  }
  return url;
};

const apiClient = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor de petición: sanitiza la URL base e inyecta el Bearer Token de NextAuth
apiClient.interceptors.request.use(async (config) => {
  config.baseURL = getBaseUrl();

  // Garantía estricta en tiempo de ejecución
  if (
    typeof window !== "undefined" &&
    window.location.protocol === "https:" &&
    config.baseURL.startsWith("http://") &&
    !config.baseURL.includes("localhost")
  ) {
    config.baseURL = config.baseURL.replace("http://", "https://");
  }

  const session = await getSession();

  if (session?.backendAccessToken) {
    config.headers.Authorization = `Bearer ${session.backendAccessToken}`;
  }

  return config;
});

// Interceptor de respuesta: normalización de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Error de conexión con el servidor";

    return Promise.reject(new Error(message));
  }
);

export default apiClient;