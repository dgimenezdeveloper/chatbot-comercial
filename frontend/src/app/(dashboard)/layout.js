"use client";

import { SessionProvider } from "next-auth/react";
import { Sidebar } from "@/components/dashboard/Sidebar";

export default function DashboardLayout({ children }) {
  return (
    <SessionProvider>
      <div className="flex h-screen overflow-hidden">
        <div className="flex-shrink-0">
          <Sidebar />
        </div>
        <main className="flex-1 overflow-y-auto overflow-x-hidden bg-slate-50
          [&::-webkit-scrollbar]:w-1
          [&::-webkit-scrollbar-track]:bg-transparent
          [&::-webkit-scrollbar-thumb]:bg-slate-300
          [&::-webkit-scrollbar-thumb]:rounded-full
          dark:[&::-webkit-scrollbar-thumb]:bg-slate-700">
          {children}
        </main>
      </div>
    </SessionProvider>
  );
}
