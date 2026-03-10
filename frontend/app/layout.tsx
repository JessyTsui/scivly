import type { Metadata } from "next";

import "./globals.css";
import { ThemeProvider } from "./providers";

export const metadata: Metadata = {
  title: {
    default: "Scivly",
    template: "%s | Scivly",
  },
  description:
    "Scivly is the research intelligence layer for monitoring papers, generating digests, and running follow-up questions in one place.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-[var(--background)] font-[family:var(--font-body)] text-[var(--foreground)] antialiased transition-colors duration-300">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
