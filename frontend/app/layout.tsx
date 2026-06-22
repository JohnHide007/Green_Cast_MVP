import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "Green Cast — Portfolio Risk Intelligence",
  description:
    "Forward-looking ESG-financial risk intelligence for European mid-market PE, private credit & real estate funds.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gc-bg text-gc-text antialiased">
        <Nav />
        <main>{children}</main>
      </body>
    </html>
  );
}
