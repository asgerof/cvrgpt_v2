import { z } from "zod";

export const Citation = z.object({
  url: z.string().url(),
  title: z.string().optional(),
  retrieved_at: z.string().optional(),
});

export const Company = z.object({
  cvr: z.string().length(8),
  name: z.string(),
  address: z.string().optional(),
});

export const Filing = z.object({
  id: z.string(),
  year: z.number(),
  type: z.string(),
  url: z.string().url().optional(),
  citations: z.array(Citation).default([]),
});

export const Accounts = z.object({
  year: z.number(),
  revenue: z.number().nullable().optional(),
  ebit: z.number().nullable().optional(),
  equity: z.number().nullable().optional(),
  citations: z.array(Citation).default([]),
});

export const CompareAccountsResponse = z.object({
  a: Accounts,
  b: Accounts,
  deltas: z.record(z.string(), z.number().nullable()),
  citations: z.array(Citation),
});

export type TCompany = z.infer<typeof Company>;
export type TAccounts = z.infer<typeof Accounts>;
export type TCompareAccountsResponse = z.infer<typeof CompareAccountsResponse>;
