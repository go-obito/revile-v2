import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth/AuthProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Revile | Technology, reported",
    template: "%s | Revile",
  },
  description: "Independent reporting on the technology shaping tomorrow.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body><AuthProvider>{children}</AuthProvider></body>
    </html>
  );
}
