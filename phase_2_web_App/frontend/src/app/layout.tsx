import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "TaskFlow - Modern Task Management",
  description: "A sleek, production-ready task management app with dark theme. Organize your work, boost your productivity.",
  keywords: ["todo", "tasks", "productivity", "task management", "dark theme"],
  authors: [{ name: "TaskFlow" }],
  openGraph: {
    title: "TaskFlow - Modern Task Management",
    description: "A sleek, production-ready task management app with dark theme.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#000000",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body className="font-sans antialiased bg-black text-white">
        {children}
      </body>
    </html>
  );
}
