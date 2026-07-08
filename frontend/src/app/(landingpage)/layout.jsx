import Navbar from "@/components/layout/navbar/navbar";
import Footer from "@/components/layout/footer/footer";

export default function LandingLayout({ children }) {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 w-full">{children}</main>
      <Footer />
    </div>
  );
}
