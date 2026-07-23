import { auth, signOut } from "@/auth";
import Image from "next/image";
import { PanelIcon } from "@/components/icons/PanelIcon";

export default async function DashboardPage() {
  const session = await auth();

  return (
    <section className="flex flex-1 flex-col">
      <header className="border-b border-slate-200 pb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <PanelIcon className="size-6 text-slate-800" />
            <h1 className="text-2xl font-bold tracking-wide text-slate-950">
              PANEL ADMINISTRATIVO
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium leading-none">
                {session.user.name}
              </p>
            </div>
            {session?.user?.picture ? (
              <Image
                src={session.user.picture}
                alt="User Avatar"
                width={40}
                height={40}
                className="rounded-full"
              />
            ) : (
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200 text-gray-600 font-bold">
                {session?.user?.name?.charAt(0).toUpperCase() || "U"}
              </div>
            )}
          </div>
        </div>
      </header>
      <main className="p-8">
        <h2 className="text-lg font-semibold">Contenido</h2>
      </main>
    </section>
  );
}
