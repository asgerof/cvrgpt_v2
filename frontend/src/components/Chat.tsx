'use client'
import { useState } from 'react'
import { searchCompanies, getCompany, compare, listFilings } from '@/lib/api'

type Item = { cvr: string, name: string, status?: string }

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
            <li key={it.cvr}>
              <button className={`w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 ${selected===it.cvr?'bg-white/10':''}`} onClick={()=>pick(it.cvr)}>
                <div className="font-medium">{it.name}</div>
                <div className="text-xs opacity-70">{it.cvr} {it.status?`· ${it.status}`:''}</div>
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
            <CompareCard data={answer.cmp} />
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

function CompareCard({data}:{data:any}){
  const comp = data?.comparison
  if(!comp) return <div className="rounded-xl bg-black/20 p-4">No comparison available.</div>
  const cur = comp.current || {}
  const del = comp.delta || {}
  return (
    <div className="rounded-xl bg-black/20 p-4">
      <h2 className="text-xl font-semibold mb-1">Latest comparison</h2>
      {data.narrative && <p className="opacity-90 mb-3 text-sm">{data.narrative}</p>}
      <div className="grid md:grid-cols-3 gap-3 text-sm">
        <Metric label="Margin" value={cur.margin==null?null:(cur.margin*100)} suffix="%" delta={del.margin} isPercent />
        <Metric label="Solvency" value={cur.solvency==null?null:(cur.solvency*100)} suffix="%" delta={del.solvency} isPercent />
        <Metric label="Liquidity" value={cur.liquidity} delta={del.liquidity} />
      </div>
      <Citations cites={data.citations || []} />
    </div>
  )
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
