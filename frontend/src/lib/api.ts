const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export async function searchCompanies(q: string) {
  const r = await fetch(`${base}/v1/search?q=${encodeURIComponent(q)}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('search failed')
  return r.json()
}

export async function getCompany(cvr: string) {
  const r = await fetch(`${base}/v1/company/${cvr}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('company failed')
  return r.json()
}

export async function compare(cvr: string) {
  const r = await fetch(`${base}/v1/compare/${cvr}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('compare failed')
  return r.json()
}
