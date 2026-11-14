import { Suspense } from 'react';
import Explorer from '@/components/explorer';
export const metadata = { title: 'Research Explorer' };
export default function Page() {
  return <Suspense fallback={<div className="route-loading">Loading research explorer...</div>}><Explorer/></Suspense>;
}
