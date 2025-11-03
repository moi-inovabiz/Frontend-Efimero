import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/contexts/AuthContext";
import ThemeProvider from "@/components/ThemeProvider";
import { generateServerThemeTag } from "@/lib/server-theme";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Frontend Efímero - Sistema Adaptativo",
  description: "Sistema de Adaptación Predictiva Profunda de UI",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Generar tema en el servidor
  const serverThemeCSS = await generateServerThemeTag();

  return (
    <html lang="es">
      <head>
        {/* Inyectar tema del usuario ANTES de renderizar el contenido (SSR) */}
        <style id="user-theme-ssr" dangerouslySetInnerHTML={{ __html: serverThemeCSS }} />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider>
          <ThemeProvider>
            {children}
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
