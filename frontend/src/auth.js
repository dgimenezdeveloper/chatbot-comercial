import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import { logger } from "@/lib/logger"

export const { handlers, signIn, signOut, auth } = NextAuth({
  trustHost: true,
  providers: [Google],
  pages: {
    signIn: "/login",
    error: "/login", // Redirige errores de autenticación a la página de login
  },
  callbacks: {
    /**
     * Guardián de inicio de sesión:
     * Se ejecuta ANTES de crear la sesión en el frontend.
     * Consulta al backend si el mail está en la Lista Blanca.
     * Si el backend responde error (403), devuelve `false` y NextAuth cancela el login.
     */
    async signIn({ account }) {
      if (account?.provider === "google" && account.access_token) {
        try {
          const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/auth/google`
          logger.info({ url: apiUrl }, "Validando token de Google con la Lista Blanca del backend...")

          const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ access_token: account.access_token }),
          })

          if (!response.ok) {
            logger.error(
              { status: response.status },
              "Acceso denegado: El correo no está en la Lista Blanca del backend."
            )
            // Cancelar login en NextAuth
            return false
          }

          const data = await response.json()
          logger.info("Validación exitosa en backend. Usuario autorizado.")
          
          // Guardamos temporalmente la respuesta del backend en la cuenta
          account.backendData = data
          return true
        } catch (error) {
          logger.error({ err: error.message }, "Error de conexión con el backend durante signIn")
          return false
        }
      }
      return true
    },

    async jwt({ token, account }) {
      if (account?.backendData) {
        token.backendAccessToken = account.backendData.access_token
        token.user = account.backendData.user
      }
      return token
    },

    async session({ session, token }) {
      if (token.backendAccessToken) {
        session.backendAccessToken = token.backendAccessToken
      }
      if (token.user) {
        session.user = token.user
      }
      return session
    },
  },
})