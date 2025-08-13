import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CVRGPT',
  description: 'Chat + evidence over CVR/Virk data',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  )
}
