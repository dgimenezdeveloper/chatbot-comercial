import "./globals.css";

export const metadata = {
  title: "Pymio chatbot para tu Pyme",
  description:
    "Un Chatbot para tu Pyme, gestioná tus turnos y recordatorios de manera automatizada",
};

// No theme class here — each route group layout applies its own theme
// to <html> via ThemeProvider so CSS variables resolve correctly.
export default function RootLayout({ children }) {
  return (
    <html lang="es" className="h-full antialiased" suppressHydrationWarning>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
