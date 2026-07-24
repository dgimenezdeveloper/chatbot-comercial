import Image from "next/image";
import { auth } from "@/auth";

/**
 * SidebarUserFooter — Server Component.
 *
 * Renders two stacked rows:
 *   1. "Tu negocio" label (as before)
 *   2. User avatar (photo or initial) + user name from session
 *
 * The "Tu negocio" label preserves the original sidebar design.
 * The avatar/name replaces the hardcoded "🏪 Salón de Belleza".
 */
export async function SidebarUserFooter() {
  const session = await auth();
  const name    = session?.user?.name    ?? "Usuario";
  const picture = session?.user?.picture ?? null;
  const initial = name.charAt(0).toUpperCase();

  return (
    <div className="flex items-center gap-3 rounded-lg bg-background px-2 py-2">
      {/* Avatar: photo if available, otherwise colored initial */}
      {picture ? (
        <Image
          src={picture}
          alt={`Avatar de ${name}`}
          width={36}
          height={36}
          className="size-9 shrink-0 rounded-full object-cover"
        />
      ) : (
        <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
          {initial}
        </div>
      )}

      {/* Labels */}
      <div className="min-w-0">
        <p className="text-xs text-muted-foreground">Tu negocio</p>
        <p className="truncate text-sm font-medium text-foreground">{name}</p>
      </div>
    </div>
  );
}
