export function downloadCSV(columns: string[], rows: (string|number|null)[][], filename: string) {
  const header = columns.join(",");
  const body = rows.map(r => r.map(v => (v ?? "").toString().replace(/"/g,'""')).map(v=>`"${v}"`).join(",")).join("\n");
  const blob = new Blob([header + "\n" + body], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
