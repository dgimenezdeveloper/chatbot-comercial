import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import { logger } from "@/lib/logger"

export const { handlers, signIn, signOut, auth } = NextAuth({
  trustHost: true,
  providers: [Google],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async jwt({ token, account }) {
      if (account?.provider === "google" && account.access_token) {
        try {
          logger.info(
            { url: `${process.env.NEXT_PUBLIC_API_URL}/auth/google` },
            "Initiating POST to backend"
          )
          
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ access_token: account.access_token }),
          })

          if (response.ok) {
            const data = await response.json()
            logger.info("Backend response OK. Token received.")
            token.backendAccessToken = data.access_token
            token.user = {
              ...data.user,
              picture: data.user.picture,
              email: data.user.email,
              name: data.user.name,
            }
          } else {
            logger.error({ status: response.status }, "Backend responded with error status")
            token.error = "BackendAuthenticationError"
          }
        } catch (error) {
          logger.error({ err: error.message }, "Backend connection failed")
          token.error = "BackendAuthenticationError"
        }
      }
      return token
    },
    async session({ session, token }) {
      session.backendAccessToken = token.backendAccessToken
      session.error = token.error
      
      if (token.user) {
        session.user = token.user
      }
      
      return session
    }
  }
})