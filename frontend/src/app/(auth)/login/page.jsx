"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { LoginForm } from "@/components/auth/LoginForm/LoginForm";

export default function LoginPage() {
  const handleCredentialsSubmit = (e) => {
    e.preventDefault();
  };

  const [isGoogleLoading, setIsGoogleLoading] = useState(false)

  const handleGoogleSignIn = () => {
    setIsGoogleLoading(true);
    signIn("google", { redirectTo: "/dashboard" });
  };

  return (
    <LoginForm 
          onCredentialsSubmit={handleCredentialsSubmit}
          onGoogleSignIn={handleGoogleSignIn}
          isGoogleLoading={isGoogleLoading}
        />
  );
}
