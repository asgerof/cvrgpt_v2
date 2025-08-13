import Link from 'next/link'

export default function Home() {
  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="text-3xl font-semibold mb-2">CVRGPT</h1>
      <p className="opacity-80 mb-6">Decision copilot over Danish company data with citations.</p>
      <Link href="/chat" className="rounded-2xl bg-white/10 px-4 py-2 hover:bg-white/20 transition">Open Chat</Link>
      <div className="mt-8 text-sm opacity-70">
        <p>Backend expected at <code>{process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}</code></p>
      </div>
    </main>
  )
}
