import { Inter, Montserrat } from "next/font/google";
import ThemeProvider from "@/components/layout/ThemeProvider";
import Navbar from "@/components/layout/navbar/navbar";
import Footer from "@/components/layout/footer/footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600"],
});

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  weight: ["500", "600", "700"],
});

export default function LandingLayout({ children }) {
  return (
    <>
      {/* Registers font CSS variables and applies theme-landing to <html> */}
      <ThemeProvider theme="theme-landing" />
      <div
        className={`${inter.variable} ${montserrat.variable} min-h-screen flex flex-col gap-4 lg:gap-20`}
      >
        <Navbar />
        <main className="grow">{children}</main>
        <Footer />
      </div>
    </>
  );
}
