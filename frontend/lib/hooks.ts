import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { Company, CompareAccountsResponse } from "./schemas";

export function useSearchCompanies(q: string) {
  return useQuery({
    queryKey: ["search", q],
    queryFn: async () => {
      const data = await api<any[]>(`/companies/search?q=${encodeURIComponent(q)}`);
      return Company.array().parse(data);
    },
    enabled: q.length >= 2,
  });
}

export function useCompare(cvr: string) {
  return useQuery({
    queryKey: ["compare", cvr],
    queryFn: async () => {
      const data = await api<any>(`/companies/${cvr}/accounts/compare`);
      return CompareAccountsResponse.parse(data);
    },
    enabled: cvr.length === 8,
  });
}
