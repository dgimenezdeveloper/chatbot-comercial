"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet/sheet";
import { Menu } from "lucide-react";
import LogoPymio from "@/components/icons/logo-pymio";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <nav className="w-full bg-white border-b border-gray-100 px-5">
      <div className="max-w-300 mx-auto h-22 flex justify-between">
        <Link href="/" className="shrink-0 flex items-center">
          <LogoPymio className="w-22.5 h-11.5 lg:w-31.25 lg:h-16" />
        </Link>

        <div className="hidden lg:flex items-center gap-10 text-[1rem] leading-1.5 text-menu-primary/90 font-title font-medium transition-colors tracking-wide">
          <a
            href="#home"
            className="text-menu-active  font-semibold hover:text-menu-active"
          >
            Home
          </a>
          <a href="#propuesta" className="hover:text-menu-active font-medium">
            Propuesta
          </a>
          <a href="#beneficios" className="hover:text-menu-active font-medium">
            Beneficios
          </a>
          <a
            href="#indicaciones"
            className="hover:text-menu-active font-medium"
          >
            Indicaciones
          </a>
        </div>

        <div className="hidden lg:flex items-center gap-[1.125rem]">
          <div className="h-[1.3125rem] w-[.0625rem] bg-[#486284]/80 mx-1" />

          <Link
            href="/registro"
            className="text-[1rem] font-medium text-[#486284]/75 underline tracking-[-0.03em] hover:text-[#1A202C] transition-colors"
          >
            Registro
          </Link>

          <Link
            href="/login"
            className="flex items-center justify-center bg-[#486284] text-white hover:bg-[#486284]/90 rounded-[.25rem] w-[5.125rem] h-[2.375rem] text-[.875rem] font-medium tracking-[-0.03em] transition-colors"
          >
            Log In
          </Link>
        </div>

        <div className="lg:hidden flex items-center">
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-slate-50 h-10 w-10 transition-colors">
              <Menu className="h-7 w-7 text-[#486284]" />
            </SheetTrigger>

            <SheetContent
              side="right"
              className="flex flex-col p-6 pt-16 theme-landing w-[85vw] sm:w-[21.875rem] bg-white border-l"
            >
              <div className="flex flex-col gap-4 mt-2">
                <a
                  href="#home"
                  className="text-[1.125rem] font-semibold text-[#1A202C] py-2 border-b border-transparent hover:border-gray-100 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Home
                </a>
                <a
                  href="#propuesta"
                  className="text-[1.125rem] font-medium text-[#486284]/90 py-2 border-b border-transparent hover:border-gray-100 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Propuesta
                </a>
                <a
                  href="#beneficios"
                  className="text-[1.125rem] font-medium text-[#486284]/90 py-2 border-b border-transparent hover:border-gray-100 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Beneficios
                </a>
                <a
                  href="#indicaciones"
                  className="text-[1.125rem] font-medium text-[#486284]/90 py-2 border-b border-transparent hover:border-gray-100 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Indicaciones
                </a>
              </div>

              <div className="mt-6 flex flex-col gap-5 border-t border-gray-100 pt-8">
                <Link
                  href="/registro"
                  className="text-[1.125rem] font-medium text-[#486284]/90 underline text-center py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Register
                </Link>
                <Link
                  href="/login"
                  className="flex items-center justify-center bg-[#486284] text-white rounded-[.25rem] h-[3.25rem] w-full text-[1rem] font-semibold transition-colors hover:bg-[#486284]/90 shadow-sm"
                  onClick={() => setIsOpen(false)}
                >
                  Log In
                </Link>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  );
}
