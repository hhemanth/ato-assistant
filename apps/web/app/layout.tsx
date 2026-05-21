import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ATO Assistant",
  description: "AI assistant for Australian Taxation Office information",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} bg-page-bg text-gray-900 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
