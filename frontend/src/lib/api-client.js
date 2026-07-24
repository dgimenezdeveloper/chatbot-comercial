/**
 * Axios instance configured for the chatbot-comercial backend.
 *
 * Auth token injection is handled per-request via getSession() from next-auth.
 * This file is imported by service modules and hooks.
 *
 * @module lib/api-client
 */

import axios from "axios";
import { getSession } from "next-auth/react";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: inject backend access token from NextAuth session
apiClient.interceptors.request.use(async (config) => {
  const session = await getSession();

  if (session?.backendAccessToken) {
    config.headers.Authorization = `Bearer ${session.backendAccessToken}`;
  }

  return config;
});

// Response interceptor: normalize errors
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
