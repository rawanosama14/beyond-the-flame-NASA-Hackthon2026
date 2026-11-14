import type { Metadata } from 'next';
import AppShell from '@/components/app-shell';
import './globals.css';

export const metadata:Metadata={
  title:{default:'BEYOND THE FLAME — Space Fire Intelligence',template:'%s | BEYOND THE FLAME'},
  description:'Explore and interpret microgravity combustion research for safer human space exploration. An interactive research prototype.',
  applicationName:'BEYOND THE FLAME',
};
export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en" suppressHydrationWarning><body><AppShell>{children}</AppShell></body></html>;
}
