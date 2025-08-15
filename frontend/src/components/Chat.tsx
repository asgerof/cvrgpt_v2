'use client'
import { useState } from 'react'
import { searchCompanies, getCompany, compare, listFilings } from '@/lib/api'
import type { components } from '@/types/api'

type Item = components["schemas"]["Company"]

export default function Chat() {
  const [q, setQ] = useState('')
  const [items, setItems] = useState<Item[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [answer, setAnswer] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [filings, setFilings] = useState<any[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function doSearch(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true); setError(null)
    try {
      const res = await searchCompanies(q)
      setItems(res.items || [])
      if ((res.items || []).length === 0) setError('No results')
    } catch (err:any) {
      setError(err?.message || 'Search failed')
    } finally { setLoading(false) }
  }

  async function pick(cvr: string) {
    setSelected(cvr)
    setLoading(true); setError(null)
    try {
      const [profile, cmp, fl] = await Promise.all([getCompany(cvr), compare(cvr), listFilings(cvr)])
      setAnswer({ profile, cmp })
      setFilings(fl?.filings || null)
    } catch (err:any) {
      setError(err?.message || 'Load failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-[380px_1fr] gap-4">
      <aside className="p-4 bg-[var(--card)] rounded-2xl">
        <form onSubmit={doSearch} className="space-y-2">
          <input className="w-full rounded-xl bg-white/5 px-3 py-2 outline-none" placeholder="Search by name or CVR…" value={q} onChange={e=>setQ(e.target.value)} />
          <button className="w-full rounded-xl bg-white/10 py-2 hover:bg-white/20" disabled={loading}>Search</button>
        </form>
        {error && <div className="mt-2 text-xs text-red-300">{error}</div>}
        <ul className="mt-4 space-y-1">
          {items.map(it => (
            <li key={it.cvr || 'unknown'}>
              <button className={`w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 ${selected===it.cvr?'bg-white/10':''}`} onClick={()=>it.cvr && pick(it.cvr)}>
                <div className="font-medium">{it.name || 'Unknown Company'}</div>
                <div className="text-xs opacity-70">{it.cvr || 'No CVR'} {it.status?`· ${it.status}`:''}</div>
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <section className="p-4 bg-[var(--card)] rounded-2xl min-h-[60vh]">
        {!answer && !loading && <div className="opacity-70">Pick a company to see profile + comparison.</div>}
        {loading && <div className="opacity-70">Loading…</div>}
        {answer && !loading && (
          <div className="space-y-6">
            <ProfileCard data={answer.profile.company} citations={answer.profile.citations} />
            <CompareCard data={answer.cmp} cvr={selected!} />
            <FilingsCard filings={filings} />
          </div>
        )}
      </section>
    </div>
  )
}

function ProfileCard({data, citations}:{data:any, citations:any[]}){
  if(!data) return null
  const addr = data.addresses?.[0]
  return (
    <div className="rounded-xl bg-black/20 p-4">
      <h2 className="text-xl font-semibold mb-3">Profile</h2>
      <div className="grid md:grid-cols-2 gap-3 text-sm">
        <div><span className="opacity-70">Name</span><div>{data.name}</div></div>
        <div><span className="opacity-70">CVR</span><div>{data.cvr}</div></div>
        <div><span className="opacity-70">Status</span><div>{data.status||'—'}</div></div>
        <div><span className="opacity-70">Industry</span><div>{data.industry?.code} · {data.industry?.text}</div></div>
        {addr && <div className="md:col-span-2"><span className="opacity-70">Address</span><div>{addr.street}, {addr.zip} {addr.city}</div></div>}
      </div>
      <Citations cites={citations} />
    </div>
  )
}

function DeltaBadge({v}:{v:number|null|undefined}){
  if(v==null) return <span className="text-xs px-2 py-0.5 rounded bg-white/10">n/a</span>
  const sign = v===0 ? '' : (v>0 ? '+' : '')
  return <span className={`text-xs px-2 py-0.5 rounded ${v>0?'bg-green-600/30':'bg-red-600/30'}`}>{sign}{v.toFixed(2)}</span>
}
function DeltaPct({v}:{v:number|null|undefined}){
  if(v==null) return <span className="text-xs px-2 py-0.5 rounded bg-white/10">n/a</span>
  const sign = v===0 ? '' : (v>0 ? '+' : '')
  return <span className={`text-xs px-2 py-0.5 rounded ${v>0?'bg-green-600/30':'bg-red-600/30'}`}>{sign}{(v*100).toFixed(1)}%</span>
}

function CompareCard({data, cvr}:{data:any, cvr:string}){
  const changes = data?.key_changes || []
  const narrative = data?.narrative
  const sources = data?.sources || []

  if(!changes.length && !narrative) return <div className="rounded-xl bg-black/20 p-4">No comparison available.</div>

  return (
    <div className="rounded-xl bg-black/20 p-4">
      <div className="flex justify-between items-center mb-1">
        <h2 className="text-xl font-semibold">Financial Comparison</h2>
        {changes.length > 0 && (
          <button
            onClick={() => downloadCSV(cvr)}
            className="text-xs px-3 py-1 rounded bg-blue-600/30 hover:bg-blue-600/50 transition"
          >
            Export CSV
          </button>
        )}
      </div>
      {data.current_period && data.previous_period && (
        <p className="text-sm opacity-70 mb-2">
          {data.previous_period} → {data.current_period}
        </p>
      )}
      {narrative && <p className="opacity-90 mb-3 text-sm">{narrative}</p>}

      {changes.length > 0 && (
        <div className="space-y-2 mb-3">
          {changes.slice(0, 5).map((change: any, i: number) => (
            <ChangeRow key={i} change={change} />
          ))}
        </div>
      )}

      <Citations cites={sources} />
    </div>
  )
}

function ChangeRow({change}: {change: any}) {
  const pctChange = change.percentage_change
  const isPositive = pctChange > 0
  const isSignificant = Math.abs(pctChange) > 1

  return (
    <div className="flex justify-between items-center p-2 rounded bg-white/5">
      <span className="font-medium text-sm">{change.field}</span>
      <div className="text-right">
        <div className="text-sm">
          {formatCurrency(change.previous_value)} → {formatCurrency(change.current_value)}
        </div>
        {isSignificant && (
          <div className={`text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? '+' : ''}{pctChange.toFixed(1)}%
          </div>
        )}
      </div>
    </div>
  )
}

function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'

  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`
  } else if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`
  } else {
    return value.toFixed(0)
  }
}

async function downloadCSV(cvr: string) {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/v1/compare/${cvr}/export`)
    if (!response.ok) throw new Error('Export failed')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `company_${cvr}_comparison.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed:', error)
    alert('Export failed. Please try again.')
  }
}

function Metric({label, value, suffix='', delta, isPercent=false}:{label:string, value:number|null|undefined, suffix?:string, delta:number|null|undefined, isPercent?:boolean}){
  return (
    <div className="rounded-lg bg-white/5 p-3">
      <div className="opacity-70 text-xs">{label}</div>
      <div className="text-lg font-semibold">
        {value==null ? 'n/a' : isPercent ? `${value.toFixed(1)}%` : value.toFixed(2)}
      </div>
      <div className="mt-1">{isPercent ? <DeltaPct v={delta} /> : <DeltaBadge v={delta} />}</div>
    </div>
  )
}

function Citations({cites}:{cites:any[]}){
  if(!cites?.length) return null
  return (
    <div className="mt-3 text-xs opacity-70 space-y-1">
      <div>Sources:</div>
      <ul className="list-disc ml-5">
        {cites.map((c,i)=> (
          <li key={i}>
            <code>{c.type||c.source}</code>
            {c.url ? (
              <>
                : <a href={c.url} target="_blank" className="underline break-all" rel="noreferrer">{c.url}</a>
              </>
            ) : null}
            {c.path ? (
              <>
                : <span className="break-all">{c.path}</span>
              </>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  )
}

function FilingsCard({filings}:{filings:any[]|null}){
  if(!filings || filings.length===0) return null
  return (
    <div className="rounded-xl bg-black/20 p-4">
      <h2 className="text-xl font-semibold mb-2">Recent filings</h2>
      <ul className="text-sm space-y-1">
        {filings.map((f:any)=> (
          <li key={f.id}>
            <a href={f.url} className="underline" target="_blank" rel="noreferrer">{f.id}</a>
            <span className="opacity-70"> · {f.type} · {f.date}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
