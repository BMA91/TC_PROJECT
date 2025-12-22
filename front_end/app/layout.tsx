"use client";

import { Geist, Geist_Mono } from "next/font/google";
import { createContext, useState } from "react";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

/* 🔹 Shared Context */
export const LoginContext = createContext<{
  loginData: any;
  setLoginData: (data: any) => void;
} | null>(null);

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [loginData, setLoginData] = useState(null);

  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <LoginContext.Provider value={{ loginData, setLoginData }}>
          {children}
        </LoginContext.Provider>
      </body>
    </html>
  );
}
