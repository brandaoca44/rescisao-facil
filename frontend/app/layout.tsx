import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rescisão Fácil | Simulador de rescisão",
  description: "Organize os dados do seu vínculo para estimar as verbas do desligamento.",
  icons: { icon: "/rescisao.svg" },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
