import type { Domain, Investigation } from './research';
export const accentForDomain = (domain: Domain) => ({ Prevention: 'orange', Detection: 'cyan', Suppression: 'violet', Foundations: 'mint' }[domain]);
export function csvFromInvestigations(items: Investigation[]) {
  const cols: (keyof Investigation)[] = ['id', 'longTitle', 'domain', 'objective', 'platform', 'fuel', 'oxygen', 'airflow', 'measurements', 'source'];
  const escape = (v: string) => `"${v.replace(/"/g, '""')}"`;
  return [cols.join(','), ...items.map((x) => cols.map((key) => escape(String(x[key]))).join(','))].join('\r\n');
}
export function downloadText(name: string, content: string, mime = 'text/plain;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
