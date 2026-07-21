import { auth, signOut } from "@/auth";
import Image from "next/image";
import { Button } from "@/components/ui/button/button";
import { Separator } from "@/components/ui/separator/separator";

export default async function DashboardPage() {
  const session = await auth();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex items-center justify-between px-6 py-4 bg-white border-b shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold tracking-tight">
            Panel Administrativo
          </span>
        </div>

        <div className="flex items-center gap-6">
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

          <Separator
            orientation="vertical"
            className="w-px h-10 bg-gray-200 self-center"
          />

          <form
            action={async () => {
              "use server";
              await signOut({ redirectTo: "/" });
            }}
          >
            <Button variant="outline" size="sm" type="submit">
              Cerrar Sesión
            </Button>
          </form>
        </div>
      </header>

      <main className="p-8">
        <h2 className="text-lg font-semibold">Contenido</h2>
      </main>
    </div>
  );
}
