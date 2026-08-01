import { Geist, Geist_Mono } from "next/font/google";
import ThemeProvider from "@/components/layout/ThemeProvider";
import QueryProvider from "@/components/providers/QueryProvider";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

// Shared layout for all authenticated/app sections: dashboard, onboarding, auth.
// Registers Geist font variables and applies theme-app to <html>.
export default function AppLayout({ children }) {
  return (
    <>
      <ThemeProvider theme="theme-app" />
      <div 
        className={`${geistSans.variable} ${geistMono.variable}`}
        style={{
          fontFamily: "var(--font-geist-sans)",
          "--font-title": "var(--font-geist-sans)"
        }}
      >
        <QueryProvider>{children}</QueryProvider>
      </div>
    </>
  );
}
