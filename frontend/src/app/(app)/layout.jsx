import { Geist, Geist_Mono } from "next/font/google";
import ThemeProvider from "@/components/layout/ThemeProvider";
import QueryProvider from "@/components/providers/QueryProvider";
import { SessionProvider } from "next-auth/react"; // <-- NUEVO IMPORT

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export default function AppLayout({ children }) {
  return (
    <>
      <ThemeProvider theme="theme-app" />
      <div className={`${geistSans.variable} ${geistMono.variable}`}>
        {/* NUEVO: Envolvemos con SessionProvider */}
        <SessionProvider>
          <QueryProvider>{children}</QueryProvider>
        </SessionProvider>
      </div>
    </>
  );
}