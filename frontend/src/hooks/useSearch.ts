import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { paths } from "../types/api"; // from openapi-typescript

type SearchResp = paths["/v1/search"]["get"]["responses"]["200"]["content"]["application/json"];

export function useSearch(q: string) {
  return useQuery({
    queryKey: ["search", q],
    queryFn: async () => {
      const r = await api.get<SearchResp>("/v1/search", { params: { q, limit: 10 } });
      return r.data;
    },
    enabled: q.length >= 2,
    retry: 2,
  });
}
