import { Geist, Geist_Mono } from "next/font/google";
import ThemeProvider from "@/components/layout/ThemeProvider";

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
      {/* Applies theme-app class to <html> so CSS vars override :root fallbacks */}
      <ThemeProvider theme="theme-app" />
      <div className={`${geistSans.variable} ${geistMono.variable}`}>
        {children}
      </div>
    </>
  );
}
