import { auth } from "@/auth";
import { SidebarBusinessFooter } from "./SidebarBusinessFooter";

/**
 * SidebarUserFooter — Server Component.
 *
 * Reads session on the server and passes user data as fallback props
 * to the client-side SidebarBusinessFooter which reads localStorage
 * for business name and logo.
 */
export async function SidebarUserFooter() {
  const session = await auth();
  const name = session?.user?.name ?? "Usuario";
  const picture = session?.user?.picture ?? null;

  return <SidebarBusinessFooter userName={name} userPicture={picture} />;
}
