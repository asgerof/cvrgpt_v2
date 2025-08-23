import type { paths, components } from "@/types/api";

// Type aliases for better readability
type SearchResponse = paths["/v1/search"]["get"]["responses"]["200"]["content"]["application/json"];
type CompanyResponse = components["schemas"]["Company"];
type CompareResponse = components["schemas"]["CompareResponse"];
type FilingsResponse = paths["/v1/filings/{cvr}"]["get"]["responses"]["200"]["content"]["application/json"];
type AccountsResponse = components["schemas"]["AccountsResponse"];

export async function searchCompanies(q: string): Promise<SearchResponse> {
  const r = await fetch(`/api/cvr/search?q=${encodeURIComponent(q)}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('search failed')
  return r.json()
}

export async function getCompany(cvr: string): Promise<CompanyResponse> {
  const r = await fetch(`/api/cvr/company/${cvr}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('company failed')
  return r.json()
}

export async function compare(cvr: string): Promise<CompareResponse> {
  const r = await fetch(`/api/cvr/compare/${cvr}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('compare failed')
  return r.json()
}

export async function listFilings(cvr: string, limit: number = 2): Promise<FilingsResponse> {
  const r = await fetch(`/api/cvr/filings/${cvr}?limit=${limit}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('filings failed')
  return r.json()
}

export async function getLatestAccounts(cvr: string): Promise<AccountsResponse> {
  const r = await fetch(`/api/cvr/accounts/${cvr}`, { cache: 'no-store' })
  if (!r.ok) throw new Error('accounts failed')
  return r.json()
}
