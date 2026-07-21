import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog/dialog";
import { useState, useEffect } from "react";
import { GoogleButton } from "@/components/auth/google-button/google-button";

export function LoginDialog({
  children,
  onGoogleSignIn,
  isGoogleLoading,
  open,
  onOpenChange,
}) {
  const [internalOpen, setInternalOpen] = useState(false);

  const isControlled = open !== undefined;
  const currentOpen = isControlled ? open : internalOpen;

  const handleOpenChange = (newOpen) => {
    if (!isControlled) {
      setInternalOpen(newOpen);
    }
    if (onOpenChange) {
      onOpenChange(newOpen);
    }
  };

  useEffect(() => {
    const handlePageShow = () => {
      if (isControlled && onOpenChange) {
        onOpenChange(false);
      } else {
        setInternalOpen(false);
      }
    };

    window.addEventListener("pageshow", handlePageShow);
    return () => window.removeEventListener("pageshow", handlePageShow);
  }, [isControlled, onOpenChange]);

  return (
    <Dialog open={currentOpen} onOpenChange={handleOpenChange}>
      {children && <DialogTrigger asChild>{children}</DialogTrigger>}
      <DialogContent className="sm:max-w-100 p-8 rounded-2xl border-zinc-800">
        <DialogHeader className="space-y-4">
          <DialogTitle className="text-center text-2xl font-semibold text-zinc-800">
            Ingresar
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
