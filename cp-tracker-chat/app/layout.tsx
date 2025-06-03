import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "CP Tracker - Informações de Comboios da CP",
  description:
    "Assistente inteligente para consultar horários, perturbações e informações sobre comboios da CP em tempo real.",
  keywords: "CP, comboios, horários, Portugal, transporte, MCP",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
