import axios from "axios";
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000",
  headers: { "x-api-key": process.env.NEXT_PUBLIC_API_KEY || "dev-local-key" },
});
