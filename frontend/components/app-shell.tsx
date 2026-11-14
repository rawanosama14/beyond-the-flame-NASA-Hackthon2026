'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { motion, AnimatePresence, MotionConfig } from 'motion/react';
import {
  Activity, ArrowRight, Atom, BookOpenText, ChartNoAxesCombined, ChevronDown, Command, Compass,
  Flame, GitCompareArrows, Menu, Microscope, Moon, Orbit, PanelLeftClose, Search, ShieldCheck,
  Sparkles, Sun, X, ExternalLink
} from 'lucide-react';
import { investigations, scenarios, type Scenario } from '@/lib/research';

interface AppState {
  scenario: Scenario;
  setScenario: (value: Scenario) => void;
  compareIds: [string, string];
  setCompareIds: (value: [string, string]) => void;
}
const Context = createContext<AppState | null>(null);
export function useWorkspace() {
  const ctx = useContext(Context);
  if (!ctx) throw new Error('useWorkspace must be used within AppShell');
  return ctx;
}

const nav = [
  { href: '/dashboard', label: 'Mission control', icon: Compass, caption: 'Overview' },
  { href: '/explorer', label: 'Research explorer', icon: Microscope, caption: 'Investigations' },
  { href: '/compare', label: 'Compare studies', icon: GitCompareArrows, caption: 'Side by side' },
  { href: '/intelligence', label: 'Safety intelligence', icon: ShieldCheck, caption: 'Research relevance' },
  { href: '/visual-lab', label: 'Flame visual lab', icon: Activity, caption: 'Interactive concept' },
  { href: '/copilot', label: 'Research copilot', icon: Sparkles, caption: 'AI-ready' }
];
export const pageNames: Record<string,string> = Object.fromEntries(nav.map(x=>[x.href,x.label]));

function AppLogo() {
  return <Link href="/dashboard" className="brand" aria-label="Beyond the Flame home">
    <span className="brand-icon"><Flame size={23} strokeWidth={1.8}/></span>
    <span className="brand-type"><strong>BEYOND <i>THE FLAME</i></strong><small>SPACE FIRE INTELLIGENCE</small></span>
  </Link>;
}

export function ScenarioSelect({ compact = false }: { compact?: boolean }) {
  const { scenario, setScenario } = useWorkspace();
  return <label className={`scenario-select ${compact ? 'compact' : ''}`}>
    <span className="scenario-select-icon"><Orbit size={16}/></span>
    <span className="scenario-select-copy"><small>MISSION ENVIRONMENT</small><span>{scenario}</span></span>
    <select aria-label="Mission environment" value={scenario} onChange={e => setScenario(e.target.value as Scenario)}>
      {Object.keys(scenarios).map(x => <option key={x} value={x}>{x}</option>)}
    </select>
    <ChevronDown size={15} className="scenario-chevron"/>
  </label>;
}

function CommandMenu({ open, close }: { open: boolean; close: () => void }) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => { if (open) { setQuery(''); window.setTimeout(()=>input.current?.focus(), 40); } }, [open]);
  const suggestions = useMemo(()=>{
    const q = query.trim().toLowerCase();
    const routes = nav.map(x=>({ type:'PAGE', name:x.label, description:x.caption, href:x.href }));
    const studies = investigations.map(x=>({ type:'INVESTIGATION', name:x.title, description:x.longTitle, href:`/explorer?study=${encodeURIComponent(x.id)}` }));
    return [...routes,...studies].filter(x=>!q || `${x.name} ${x.description}`.toLowerCase().includes(q)).slice(0, 9);
  }, [query]);
  function go(href:string){ close();router.push(href); }
  return <AnimatePresence>{open && <motion.div className="overlay-scrim command-scrim" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} onMouseDown={close}>
    <motion.div className="command-panel" role="dialog" aria-modal="true" aria-label="Search pages and investigations" initial={{opacity:0,scale:.96,y:-12}} animate={{opacity:1,scale:1,y:0}} exit={{opacity:0,scale:.96,y:-12}} transition={{type:'spring',bounce:0,duration:.3}} onMouseDown={e=>e.stopPropagation()}>
      <div className="command-input-row"><Search size={19}/><input ref={input} value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search pages and investigations..." onKeyDown={e=>{if(e.key==='Enter'&&suggestions[0])go(suggestions[0].href)}}/><kbd>ESC</kbd></div>
      <div className="command-results"><div className="micro-label">QUICK NAVIGATION</div>
        {suggestions.length ? suggestions.map((x,i)=><button key={`${x.type}-${x.href}`} className="command-result" onClick={()=>go(x.href)}><span className="result-dot">{String(i+1).padStart(2,'0')}</span><span><strong>{x.name}</strong><small>{x.description}</small></span><span className="result-kind">{x.type}</span><ArrowRight size={15}/></button>) : <div className="command-empty">No matching research found.</div>}
      </div>
      <div className="command-footer"><span><kbd>↵</kbd> Open result</span><span><kbd>ESC</kbd> Close</span><span>Research prototype</span></div>
    </motion.div>
  </motion.div>}</AnimatePresence>;
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [scenario, setScenario] = useState<Scenario>('Moon base');
  const [compareIds, setCompareIds] = useState<[string,string]>(['BASS-II', 'SAME-R']);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [theme, setTheme] = useState<'dark'|'light'>('dark');
  const [showScenario, setShowScenario] = useState(false);
  useEffect(()=>{
    try {
      const storedScenario=localStorage.getItem('btf-scenario') as Scenario|null;
      if(storedScenario && storedScenario in scenarios) setScenario(storedScenario);
      const storedTheme=localStorage.getItem('btf-theme');
      if(storedTheme === 'light' || storedTheme === 'dark') setTheme(storedTheme);
    } catch { /* no storage */ }
  },[]);
  useEffect(()=>{try{localStorage.setItem('btf-scenario',scenario)}catch{}},[scenario]);
  useEffect(()=>{document.documentElement.dataset.theme=theme;try{localStorage.setItem('btf-theme',theme)}catch{}},[theme]);
  useEffect(()=>setMobileOpen(false),[pathname]);
  useEffect(()=>{
    const handler=(e:KeyboardEvent)=>{
      if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();setCommandOpen(v=>!v)}
      if(e.key==='Escape'){setCommandOpen(false);setMobileOpen(false);setShowScenario(false)}
      if(e.key==='/' && !['INPUT','TEXTAREA','SELECT'].includes((e.target as HTMLElement).tagName)){e.preventDefault();setCommandOpen(true)}
    };
    window.addEventListener('keydown',handler);return()=>window.removeEventListener('keydown',handler);
  },[]);
  const state = useMemo(()=>({scenario,setScenario,compareIds,setCompareIds}),[scenario,compareIds]);
  return <Context.Provider value={state}><MotionConfig reducedMotion="user">
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen?'sidebar-open':''}`}>
        <div className="side-top"><AppLogo/><button className="icon-button mobile-sidebar-close" onClick={()=>setMobileOpen(false)} aria-label="Close navigation"><PanelLeftClose size={20}/></button></div>
        <div className="nav-eyebrow">WORKSPACE</div>
        <nav className="navigation" aria-label="Primary navigation">{nav.map((item)=>{
          const Icon=item.icon;
          return <Link key={item.href} href={item.href} className={`nav-link ${pathname===item.href?'active':''}`} aria-current={pathname===item.href?'page':undefined}><Icon size={19} strokeWidth={1.8}/><span>{item.label}</span>{pathname===item.href&&<span className="active-glint"/>}</Link>;
        })}</nav>
        <div className="sidebar-lower">
          <div className="nav-eyebrow">MISSION RESOURCES</div>
          <a className="side-external" href="https://psi.nasa.gov/" target="_blank" rel="noopener noreferrer"><BookOpenText size={18}/><span>NASA PSI Repository</span><ExternalLink size={13}/></a>
          <a className="side-external" href="https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/" target="_blank" rel="noopener noreferrer"><Atom size={18}/><span>Combustion Science</span><ExternalLink size={13}/></a>
          <div className="sidebar-mission"><span className="mission-topline"><span className="tiny-signal"/> EXPLORATION BRIEF · 2026</span><div className="mission-planet"><span className="planet-surface"/></div><h3>The next giant leap<br/><em>starts with safety.</em></h3><p>Turning NASA combustion research into clearer mission decisions.</p><span className="mission-bottom">DAY ONE / FRONTEND CONCEPT <ArrowRight size={14}/></span></div>
          <div className="workspace-identity"><span className="workspace-avatar">B</span><span><strong>Research workspace</strong><small>Interactive prototype</small></span><span className="workspace-status"/></div>
        </div>
      </aside>
      {mobileOpen&&<button className="mobile-backdrop" aria-label="Close menu" onClick={()=>setMobileOpen(false)}/>}
      <div className="main-column">
        <header className="topbar">
          <div className="topbar-breadcrumb"><button className="icon-button mobile-menu" onClick={()=>setMobileOpen(true)} aria-label="Open menu"><Menu size={21}/></button><span className="topbar-section">WORKSPACE</span><span className="crumb-divider">/</span><strong>{pageNames[pathname] || 'Mission control'}</strong></div>
          <div className="topbar-actions"><span className="demo-status"><span className="tiny-signal"/> PROTOTYPE DATA</span><button className="top-search" onClick={()=>setCommandOpen(true)} aria-label="Search research and pages"><Search size={16}/><span>Search anything</span><kbd>⌘ K</kbd></button>
            <button className="icon-button theme-toggle" onClick={()=>setTheme(t=>t==='dark'?'light':'dark')} title={`Switch to ${theme==='dark'?'light':'dark'} theme`} aria-label="Toggle theme">{theme==='dark'?<Sun size={19}/>:<Moon size={19}/>}</button>
            <div className="top-scenario-wrap"><button className="top-scenario-button" onClick={()=>setShowScenario(v=>!v)} aria-expanded={showScenario}><span className="scenario-initial">{scenario==='Moon base'?'M':scenario==='Space station'?'S':scenario==='Mars habitat'?'M':'R'}</span><span>{scenario}</span><ChevronDown size={14}/></button>
              <AnimatePresence>{showScenario&&<motion.div className="scenario-popover" initial={{opacity:0,y:-7,scale:.97}} animate={{opacity:1,y:0,scale:1}} exit={{opacity:0,y:-7,scale:.97}} transition={{duration:.16}}>{(Object.keys(scenarios) as Scenario[]).map(x=><button key={x} className={x===scenario?'chosen':''} onClick={()=>{setScenario(x);setShowScenario(false)}}><span>{x}</span><small>{scenarios[x].eyebrow}</small></button>)}</motion.div>}</AnimatePresence>
            </div>
          </div>
        </header>
        <main id="main-content" className="page-container"><motion.div key={pathname} initial={{opacity:0,y:9}} animate={{opacity:1,y:0}} transition={{type:'spring',bounce:0,duration:.4}}>{children}</motion.div></main>
        <footer className="footer"><span>© 2026 BEYOND THE FLAME · SPACE FIRE INTELLIGENCE</span><span>Science first. Sources always. <span className="footer-star">✳</span> Built for exploration.</span></footer>
      </div>
    </div>
    <CommandMenu open={commandOpen} close={()=>setCommandOpen(false)}/>
  </MotionConfig></Context.Provider>;
}
