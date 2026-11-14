
'use client';
import { Orbit } from "lucide-react";
import Link from 'next/link';
import { ArrowRight, ArrowUpRight, Atom, BookOpenText, ChevronRight, CircleHelp, Download, FlaskConical, Gauge, Layers3, Radar, ShieldCheck, Sparkles, TrendingUp, Wind } from 'lucide-react';
import { useWorkspace } from './app-shell';
import { DataCaution, DemoBadge, DomainTag, Eyebrow, FlameHero, Panel, PrimaryLink, SecondaryLink, StatIcon, StudyVisual } from './ui';
import { domains, investigations, rankedInvestigations, scenarios, type Domain } from '@/lib/research';
import { accentForDomain, csvFromInvestigations, downloadText } from '@/lib/utils';

const signals=[
  {index:'01',label:'Elevated oxygen',headline:'More oxygen changes the rules.',copy:'Proposed lunar habitats may use oxygen-rich, lower-pressure atmospheres, making material screening essential.',type:'MATERIALS'},
  {index:'02',label:'Low-gravity smoke',headline:'Smoke does not travel the same way.',copy:'Without buoyant rise, transport and ventilation become important to where detectors can see particles.',type:'DETECTION'},
  {index:'03',label:'Evidence frontier',headline:'Partial gravity is still an open question.',copy:'The challenge reports no direct partial-gravity combustion datasets in NASA PSI at present.',type:'DATA GAP'},
];

function Pillar({domain,index}:{domain:Domain;index:number}){
  const detail=domains.find(x=>x.id===domain)!;
  return <Link href={`/explorer?domain=${encodeURIComponent(domain)}`} className={`pillar-card pillar-${accentForDomain(domain)}`}>
    <span className="pillar-top"><span>{String(index+1).padStart(2,'0')} / FIRE SAFETY</span><ArrowUpRight size={17}/></span>
    <span className="pillar-symbol">{domain==='Prevention'?<ShieldCheck size={27} strokeWidth={1.4}/>:domain==='Detection'?<Radar size={27} strokeWidth={1.4}/>:<Wind size={27} strokeWidth={1.4}/>}</span>
    <strong>{domain}<span className="pillar-period">.</span></strong><p>{detail.description}</p><span className="pillar-bottom">{detail.sub}</span>
  </Link>;
}
function MiniCoverage(){
  const core:Domain[]=['Prevention','Detection','Suppression'];
  const values=core.map(domain=>({domain,count:investigations.filter(x=>x.domain===domain).length}));
  const max=Math.max(...values.map(x=>x.count));
  return <div className="coverage-lines">{values.map(x=><div className="coverage-line" key={x.domain}><span>{x.domain}</span><div className="coverage-track"><span className={`coverage-bar ${accentForDomain(x.domain)}`} style={{width:`${100*x.count/max}%`}}/></div><b>{String(x.count).padStart(2,'0')}</b></div>)}</div>;
}

export default function Dashboard(){
  const {scenario}=useWorkspace();
  const ranked=rankedInvestigations(scenario);
  const scenarioMeta=scenarios[scenario];
  return <div className="dashboard-page">
    <div className="dashboard-welcome"><div><Eyebrow>MISSION DASHBOARD / 2026 CHALLENGE</Eyebrow><h1>Good to have you on the mission<span className="hello-dot">.</span></h1><p>Turn decades of microgravity research into a clearer picture of spacecraft fire safety.</p></div><div className="welcome-right"><DemoBadge/><span>RESEARCH CONCEPT · DAY 01</span></div></div>
    <section className="hero-section">
      <div className="hero-text"><div className="hero-top-tag"><span className="tiny-signal"/> SPACE FIRE RESEARCH, REIMAGINED</div>
        <h2>Beyond the<br/><em>flame.</em></h2>
        <p>Understand the invisible forces behind fire in space. Explore the experiments shaping safer habitats for the Moon, Mars, and beyond.</p>
        <div className="hero-buttons"><PrimaryLink href="/explorer">Explore investigations</PrimaryLink><Link href="/intelligence" className="hero-outline">Safety intelligence <ArrowUpRight size={17}/></Link></div>
        <div className="hero-caption"><span className="hero-caption-line"/> FROM MICROGRAVITY DATA TO HUMAN SAFETY</div>
      </div>
      <div className="hero-visual"><FlameHero/><div className="hero-science-tag"><span>MICROGRAVITY FLAME</span><strong>Absence of buoyant convection</strong><small>Artistic scientific concept · not experimental footage</small></div></div>
      <div className="hero-grid-noise"/>
    </section>

    <div className="section-head section-head-first"><div><Eyebrow>AT A GLANCE</Eyebrow><h2>Your research universe</h2></div><span className="section-side-note">CURATED RESEARCH INDEX · NOT COMPLETE PSI INVENTORY</span></div>
    <div className="stat-grid">
      <div className="stat-card"><span className="stat-card-header"><StatIcon><FlaskConical size={20}/></StatIcon><span>CURATED INDEX</span></span><div className="stat-value">{investigations.length.toString().padStart(2,'0')}<span> studies</span></div><p>Investigation groups in this prototype</p><span className="stat-corner">01 / 04</span></div>
      <div className="stat-card"><span className="stat-card-header"><StatIcon><ShieldCheck size={20}/></StatIcon><span>SAFETY PILLARS</span></span><div className="stat-value">03<span> domains</span></div><p>Prevention, detection and suppression</p><span className="stat-corner">02 / 04</span></div>
      <div className="stat-card"><span className="stat-card-header"><StatIcon><Gauge size={20}/></StatIcon><span>MOON HABITAT CONTEXT</span></span><div className="stat-value">30<span>%+ O₂</span></div><p>Potential oxygen enrichment from brief</p><span className="stat-corner">03 / 04</span></div>
      <div className="stat-card stat-card-accent"><span className="stat-card-header"><StatIcon><Atom size={20}/></StatIcon><span>EVIDENCE GAP</span></span><div className="stat-value">00<span> partial-g sets</span></div><p>Direct partial-gravity PSI datasets per brief</p><span className="stat-corner">04 / 04</span></div>
    </div>

    <div className="section-head section-head-spacious"><div><Eyebrow>WHAT MATTERS</Eyebrow><h2>Three pillars of fire safety</h2></div><Link href="/intelligence" className="text-arrow-link">Explore safety intelligence <ArrowUpRight size={16}/></Link></div>
    <div className="pillars-grid"><Pillar domain="Prevention" index={0}/><Pillar domain="Detection" index={1}/><Pillar domain="Suppression" index={2}/></div>

    <div className="dashboard-split">
      <Panel title="Research priorities" eyebrow={`RANKED FOR ${scenario.toUpperCase()} · PROTOTYPE`} action={<Link href="/intelligence" className="small-route">View all <ArrowRight size={16}/></Link>} className="priorities-panel">
        <p className="panel-description">Illustrative editorial matching from investigation descriptions—not measured risk or an official NASA ranking.</p>
        <div className="priorities-list">{ranked.slice(0,4).map((study,index)=><Link href={`/explorer?study=${encodeURIComponent(study.id)}`} className="priority-item" key={study.id}><span className="priority-no">0{index+1}</span><div className="priority-visual"><StudyVisual study={study} size="small"/></div><span className="priority-info"><strong>{study.title}</strong><small>{study.summary}</small></span><DomainTag domain={study.domain}/><ArrowUpRight size={17} className="priority-icon"/></Link>)}</div>
      </Panel>
      <div className="dashboard-side-stack">
        <Panel title="Research coverage" eyebrow="CURATED STUDY GROUPS" className="coverage-panel"><MiniCoverage/><div className="coverage-bottom"><span><Layers3 size={16}/> Four research categories including foundations</span><Link href="/explorer"><ChevronRight size={18}/></Link></div></Panel>
        <section className="scenario-snapshot"><span className="scenario-overline"><span className="tiny-signal"/> ACTIVE MISSION CONTEXT</span><div className="scenario-mainline"><h3>{scenarioMeta.label}</h3><span className="scenario-orbit"><Orbit size={30}/></span></div><p>{scenarioMeta.copy}</p><span className="scenario-atmosphere">{scenarioMeta.atmosphere}</span><Link href="/intelligence">Inspect mission context <ArrowRight size={15}/></Link></section>
      </div>
    </div>

    <div className="section-head section-head-spacious"><div><Eyebrow>SCIENTIFIC SIGNALS</Eyebrow><h2>Questions worth answering</h2></div><span className="section-side-note">DRAWN FROM THE 2026 CHALLENGE BRIEF</span></div>
    <div className="signal-grid">{signals.map((s)=><article key={s.index} className="signal-card"><span className="signal-card-top"><span>{s.index} / RESEARCH NOTE</span><span>{s.type}</span></span><div className="signal-card-orb"><span/></div><h3>{s.headline}</h3><p>{s.copy}</p></article>)}</div>
    <section className="lower-cta"><div><div className="cta-micro"><Sparkles size={16}/> YOUR RESEARCH DESK IS READY</div><h2>Ask better questions.<br/><em>Find stronger evidence.</em></h2><p>Move from scattered study descriptions to a connected research workflow.</p><div className="cta-buttons"><PrimaryLink href="/copilot">Open research copilot</PrimaryLink><button className="btn btn-subtle" onClick={()=>downloadText('beyond-the-flame-curated-investigations.csv',csvFromInvestigations(investigations),'text/csv;charset=utf-8')}><Download size={16}/> Export index (CSV)</button></div></div><div className="cta-symbol"><div className="cta-symbol-inner"><Sparkles size={72} strokeWidth={.8}/></div></div></section>
    <DataCaution>Day-one research UI. Study summaries are editorial interpretations of the supplied challenge description. No experimental datasets, measured risk predictions, live NASA API, or production AI model are included yet.</DataCaution>
  </div>;
}
