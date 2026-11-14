'use client';
import type { ReactNode } from 'react';
import Link from 'next/link';
import { ArrowRight, ArrowUpRight, ChevronRight, ExternalLink, FlaskConical, Info, Activity, Check } from 'lucide-react';
import type { Investigation, Domain } from '@/lib/research';
import { accentForDomain } from '@/lib/utils';

export function Eyebrow({children, className=''}:{children:ReactNode;className?:string}){return <span className={`eyebrow ${className}`}><span className="eyebrow-stroke"/>{children}</span>}
export function PageHeader({index,eyebrow,title,accent,description,action}:{index:string;eyebrow:string;title:string;accent?:string;description:string;action?:ReactNode}){
  return <div className="page-head"><div><Eyebrow>{index} / {eyebrow}</Eyebrow><h1>{title} {accent&&<em>{accent}</em>}</h1><p>{description}</p></div>{action&&<div className="page-head-action">{action}</div>}</div>;
}
export function Panel({title,eyebrow,action,children,className=''}:{title?:string;eyebrow?:string;action?:ReactNode;children:ReactNode;className?:string}){
  return <section className={`surface-panel ${className}`}>{(title||eyebrow||action)&&<div className="panel-header"><div><span className="micro-label">{eyebrow}</span>{title&&<h2>{title}</h2>}</div>{action&&<div className="panel-action">{action}</div>}</div>}{children}</section>;
}
export function DataCaution({children,className=''}:{children:ReactNode;className?:string}){
  return <div className={`data-caution ${className}`}><Info size={17}/><span>{children}</span></div>;
}
export function DemoBadge({children='DEMO DATA'}:{children?:ReactNode}){return <span className="demo-badge"><span className="demo-badge-dot"/>{children}</span>}
export function DomainTag({domain}:{domain:Domain}){return <span className={`domain-tag accent-${accentForDomain(domain)}`}><span className="domain-indicator"/>{domain}</span>}
export function SmallLink({href,children}:{href:string;children:ReactNode}){return <Link className="text-arrow-link" href={href}>{children}<ArrowUpRight size={16}/></Link>}
export function ExternalLinkText({href,children}:{href:string;children:ReactNode}){return <a className="text-arrow-link" href={href} target="_blank" rel="noopener noreferrer">{children}<ExternalLink size={14}/></a>}
export function PrimaryLink({href,children}:{href:string;children:ReactNode}){return <Link className="btn btn-primary" href={href}>{children}<ArrowRight size={17}/></Link>}
export function SecondaryLink({href,children}:{href:string;children:ReactNode}){return <Link className="btn btn-secondary" href={href}>{children}<ArrowUpRight size={16}/></Link>}
export function StudyVisual({study,size='normal'}:{study:Investigation;size?:'normal'|'wide'|'small'}){
  const accent=accentForDomain(study.domain);
  return <div className={`study-visual study-visual-${size} study-tone-${accent}`} aria-label={`Conceptual visual for ${study.title}`} role="img"><div className="study-grid"/><div className="study-orbit orbit-one"/><div className="study-orbit orbit-two"/><div className="study-core"><div className="study-core-inside"/></div><span className="study-visual-cross cross-one">+</span><span className="study-visual-cross cross-two">+</span><div className="study-visual-footer"><span>{study.id}</span><span>μG / CONCEPT</span></div></div>;
}
export function ResearchCard({study,onSelect,selected,score}:{study:Investigation;onSelect?:()=>void;selected?:boolean;score?:number}) {
  return <article className={`research-card ${selected?'selected':''}`}><button className="research-card-main" onClick={onSelect} aria-label={`View ${study.longTitle}`}><StudyVisual study={study} size="small"/><div className="research-card-content"><div className="research-meta-row"><DomainTag domain={study.domain}/><span>{study.platform.split('·')[0].trim()}</span></div><h3>{study.title} <span>{study.longTitle}</span></h3><p>{study.summary}</p><div className="research-card-tags">{study.keywords.slice(0,3).map(t=><span key={t}>{t}</span>)}</div></div><span className="research-card-arrow"><ArrowUpRight size={19}/></span></button>{score!==undefined&&<div className="card-score"><span>PROTOTYPE MATCH</span><strong>{score}<small>/100</small></strong></div>}</article>;
}
export function FlameHero({compact=false,oxygen=30,flow=false}:{compact?:boolean;oxygen?:number;flow?:boolean}){
  return <div className={`flame-scene ${compact?'flame-scene-compact':''} ${flow?'flow-active':''}`} role="img" aria-label="Artistic, non-physical depiction of a spherical flame in microgravity">
    <div className="scene-stars"/><div className="scene-coordinate scene-coordinate-top">0.000° / μG</div><div className="scene-coordinate scene-coordinate-bottom">CONCEPTUAL VISUALIZATION</div>
    <svg viewBox="0 0 600 550" className="scene-svg" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="ambientHalo"><stop offset="0" stopColor="#fcae5a" stopOpacity=".37"/><stop offset=".45" stopColor="#f87942" stopOpacity=".17"/><stop offset="1" stopColor="#ff5b3d" stopOpacity="0"/></radialGradient>
        <radialGradient id="flameGlobe" cx="43%" cy="37%" r="62%"><stop offset="0" stopColor="#fff5c4"/><stop offset=".16" stopColor="#ffd18c"/><stop offset=".35" stopColor="#ff9b5a"/><stop offset=".57" stopColor="#f96f49" stopOpacity=".95"/><stop offset=".77" stopColor="#9a4d9b" stopOpacity=".85"/><stop offset=".96" stopColor="#59b7fa" stopOpacity=".45"/><stop offset="1" stopColor="#64d9ff" stopOpacity="0"/></radialGradient>
        <radialGradient id="flameCore" cx="50%" cy="48%"><stop offset="0" stopColor="#fffde4" stopOpacity="1"/><stop offset=".65" stopColor="#ffdba9" stopOpacity=".65"/><stop offset="1" stopColor="#ffa667" stopOpacity="0"/></radialGradient>
        <linearGradient id="orbitColor" x1="0" x2="1"><stop offset="0" stopColor="#83cbea" stopOpacity="0"/><stop offset=".5" stopColor="#92d9ff" stopOpacity=".28"/><stop offset="1" stopColor="#95ddff" stopOpacity="0"/></linearGradient>
        <filter id="sceneBlur"><feGaussianBlur stdDeviation="13"/></filter><filter id="coreBlur"><feGaussianBlur stdDeviation="4"/></filter>
      </defs>
      <circle cx="304" cy="272" r="245" fill="url(#ambientHalo)" />
      <g className="scene-orbit-rotate"><ellipse cx="302" cy="273" rx="225" ry="112" fill="none" stroke="url(#orbitColor)" strokeWidth="1.3" transform="rotate(-28 302 273)"/><ellipse cx="302" cy="273" rx="222" ry="114" fill="none" stroke="#bfdfff" strokeOpacity=".12" strokeDasharray="3 9" transform="rotate(30 302 273)"/></g>
      <circle cx="302" cy="273" r="183" fill="none" stroke="#acd3ef" strokeOpacity=".11"/><circle cx="302" cy="273" r="148" fill="none" stroke="#c9e1f0" strokeOpacity=".11" strokeDasharray="2 8"/>
      <circle cx="302" cy="273" r={Math.min(124,85+oxygen*.3)} fill="#ff7e58" opacity=".34" filter="url(#sceneBlur)"/>
      <path className="scene-flame-shape" d="M302 161 C345 153 400 198 413 245 C434 308 378 370 320 382 C260 391 205 352 194 298 C179 233 223 177 284 163 C290 160 296 161 302 161Z" fill="url(#flameGlobe)"/>
      <path d="M300 198 C345 192 383 231 388 276 C390 326 348 354 302 349 C263 351 226 323 222 280 C215 235 259 194 300 198Z" fill="url(#flameCore)" opacity=".85" filter="url(#coreBlur)"/>
      <ellipse cx="291" cy="248" rx="60" ry="83" fill="#fff4d6" opacity=".14" filter="url(#sceneBlur)"/>
      <circle cx="205" cy="198" r="3" fill="#90dcff" opacity=".7"/><circle cx="413" cy="222" r="2.5" fill="#fff3da" opacity=".65"/><circle cx="341" cy="393" r="2" fill="#9ad5ff" opacity=".6"/>
      <path d="M90 273h75M440 273h80M302 70v80M302 401v74" stroke="#bad3e6" strokeOpacity=".15" strokeDasharray="4 7"/>
      <g fill="#8ca9bf" fontFamily="monospace" fontSize="10"><text x="88" y="266">01</text><text x="519" y="266">02</text><text x="310" y="82">Y+</text><text x="310" y="471">Y−</text></g>
    </svg>
    {!compact&&<div className="scene-side-measure"><span className="scene-side-line"/>NO BUOYANT PLUME <span className="measure-tiny">DIFFUSION-DOMINATED</span></div>}
  </div>;
}
export function StatIcon({children}:{children:ReactNode}){return <span className="stat-icon">{children}</span>}
export function NumberMark({number}:{number:number|string}){return <span className="number-mark">{String(number).padStart(2,'0')}</span>}
export function FactRow({label,value,highlight}:{label:string;value:string;highlight?:boolean}){return <div className="fact-row"><span>{label}</span><strong className={highlight?'fact-highlight':''}>{value}</strong></div>}
export function StatusSummary(){return <div className="compact-status"><Check size={15}/> INVESTIGATION INDEX READY <ChevronRight size={14}/></div>}
