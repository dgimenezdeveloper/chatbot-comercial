import { Inter, Montserrat } from "next/font/google";
import Navbar from "@/components/layout/navbar/navbar";
import Footer from "@/components/layout/footer/footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["500", "600"],
});

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  weight: ["500", "600"],
});

export default function LandingLayout({ children }) {
  return (
    <div
      className={`${inter.className} ${montserrat.className} theme-landing min-h-screen flex flex-col gap-4 lg:gap-20`}
    >
      <Navbar />
      <main className="grow">{children}</main>
      <Footer />
    </div>
  );
}
