"use client";
import { useState } from "react";
import { useSearch } from "../../hooks/useSearch";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const { data, isLoading, isError } = useSearch(q);

  return (
    <main className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Search</h1>
      <input value={q} onChange={e=>setQ(e.target.value)} className="border p-2 w-full" placeholder="Company name..." />
      {isLoading && <p className="mt-4">Loading…</p>}
      {isError && <p className="mt-4 text-red-600">Error fetching results.</p>}
      <ul className="mt-4 space-y-2">
        {data?.items?.map((it)=>(
          <li key={it.cvr} className="border p-3 rounded">
            <div className="font-medium">{it.name}</div>
            <div className="text-sm text-gray-500">CVR: {it.cvr}</div>
          </li>
        ))}
      </ul>
    </main>
  );
}
