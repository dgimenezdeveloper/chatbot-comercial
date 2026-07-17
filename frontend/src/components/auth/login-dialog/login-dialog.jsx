import { Button } from "@/components/ui/button/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog/dialog";
import { GoogleButton } from "@/components/auth/google-button/google-button";

export function LoginDialog({ onGoogleSignIn, isGoogleLoading }) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Iniciar Sesión</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-100 p-8 rounded-2xl border-zinc-800">
        <DialogHeader className="space-y-4">
          <DialogTitle className="text-center text-2xl font-semibold text-zinc-800">
            Log in
          </DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-3 pt-6">
          <GoogleButton
            className="h-12"
            onClick={onGoogleSignIn}
            isLoading={isGoogleLoading}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
