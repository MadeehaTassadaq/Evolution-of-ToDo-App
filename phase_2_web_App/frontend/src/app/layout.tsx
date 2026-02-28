import type { Metadata, Viewport } from "next";
import Script from "next/script";
import ClientWrapper from "../components/ClientWrapper";
import ChatKitOfficialWidget from "../components/ChatKitOfficialWidget";
import { ChatKitErrorBoundary } from "../components/ChatKitErrorBoundary";
import "./globals.css";

export const metadata: Metadata = {
  title: "TaskFlow - Modern Task Management",
  description:
    "A sleek, production-ready task management app with dark theme. Organize your work, boost your productivity.",
  keywords: ["todo", "tasks", "productivity", "task management", "dark theme"],
  authors: [{ name: "TaskFlow" }],
  openGraph: {
    title: "TaskFlow - Modern Task Management",
    description:
      "A sleek, production-ready task management app with dark theme.",
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
    <html lang="en" className="dark">
      <body className="font-sans antialiased bg-black text-white" style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
        <ClientWrapper>{children}</ClientWrapper>
        <ChatKitErrorBoundary>
          <ChatKitOfficialWidget />
        </ChatKitErrorBoundary>
        {/* Load ChatKit Web Component from CDN */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
