import { useQuery } from "@tanstack/react-query";
import type { paths } from "../types/api"; // from openapi-typescript

type SearchResp = paths["/v1/search"]["get"]["responses"]["200"]["content"]["application/json"];

export function useSearch(q: string) {
  return useQuery({
    queryKey: ["search", q],
    queryFn: async (): Promise<SearchResp> => {
      const r = await fetch(`/api/cvr/search?q=${encodeURIComponent(q)}&limit=10`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    enabled: q.length >= 2,
    retry: 2,
  });
}
