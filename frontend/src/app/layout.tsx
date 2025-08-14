import './globals.css'
"use client";

import type { Metadata } from 'next'
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { ErrorBoundary } from "../components/ErrorBoundary";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <ErrorBoundary>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
