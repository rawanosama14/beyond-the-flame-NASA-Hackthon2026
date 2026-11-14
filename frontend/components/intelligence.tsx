'use client';
import { useMemo, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, ArrowUpRight, Atom, ChevronDown, CircleAlert, Gauge, Info, Layers3, ShieldAlert, ShieldCheck, SlidersHorizontal, Sparkles, Wind } from 'lucide-react';
import { useWorkspace } from './app-shell';
import { DataCaution, DemoBadge, DomainTag, PageHeader, Panel, StudyVisual } from './ui';
import { investigations, relevanceScore, scenarios, type Investigation, type Scenario } from '@/lib/research';

export default function Intelligence(){
  const {scenario,setScenario}=useWorkspace();
  const [oxygen,setOxygen]=useState(30);
  const [flow,setFlow]=useState<'Still air'|'Ventilated'>('Ventilated');
  const [selected,setSelected]=useState('BASS');
  const ordered=useMemo(()=>[...investigations].sort((a,b)=>score(b)-score(a)),[scenario,oxygen,flow]);
  function score(x:Investigation){return Math.min(99,relevanceScore(x,scenario,oxygen)+(flow==='Ventilated'&&x.keywords.includes('Flow')?4:0))}
  const focus=investigations.find(x=>x.id===selected)||ordered[0];
  return <div>
    <PageHeader index="03" eyebrow="MISSION-AWARE ANALYSIS" title="Safety" accent="intelligence." description="See which investigations may be relevant to a selected mission scenario—and why. Every match is traceable to a study description." action={<DemoBadge>ILLUSTRATIVE MATCH INDEX</DemoBadge>}/>
    <div className="intel-top-grid"><section className="intel-scenario-card"><div className="intel-scenario-bg"/><div className="intel-scenario-content"><span className="eyebrow"><span className="eyebrow-stroke"/> RESEARCH LENS / 01</span><h2>Designed around<br/><em>your mission.</em></h2><p>{scenarios[scenario].copy}</p><label className="intel-scenario-label">MISSION ENVIRONMENT</label><div className="intel-scenario-select"><Atom size={19}/><select value={scenario} onChange={e=>setScenario(e.target.value as Scenario)}>{(Object.keys(scenarios) as Scenario[]).map(x=><option key={x}>{x}</option>)}</select><ChevronDown size={17}/></div><div className="intel-mission-note">{scenarios[scenario].atmosphere}</div></div><div className="intel-illustration"><span className="orbit-big"/><span className="orbit-small"/><span className="intel-planet"/><span className="intel-planet-satellite"/></div></section>
      <section className="lens-settings surface-panel"><div className="panel-header"><div><span className="micro-label">SCENARIO SETTINGS / DEMO</span><h2>Explore conditions</h2></div><SlidersHorizontal size={19}/></div>
        <div className="lens-field"><div className="lens-label"><span>Oxygen concentration</span><strong>{oxygen}% O₂</strong></div><input type="range" min="21" max="40" step="1" value={oxygen} onChange={e=>setOxygen(Number(e.target.value))} aria-label="Hypothetical oxygen percentage"/><div className="range-labels"><span>21% · EARTH BASELINE</span><span>40% · DEMO LENS</span></div></div>
        <div className="lens-field"><div className="lens-label"><span>Cabin airflow context</span><span className="lens-muted">COMPARISON LENS</span></div><div className="segmented-control"><button className={flow==='Still air'?'active':''} onClick={()=>setFlow('Still air')}>Still air</button><button className={flow==='Ventilated'?'active':''} onClick={()=>setFlow('Ventilated')}>Ventilated</button></div></div>
        <div className="lens-note"><Info size={16}/><p>These controls reorder study relevance in this prototype. They do <strong>not</strong> simulate ignition probability, burn rate, or actual mission risk.</p></div>
      </section></div>

    <div className="intel-results-grid"><section className="surface-panel ranking-panel"><div className="panel-header"><div><span className="micro-label">HEURISTIC · EXPERIMENTAL RELEVANCE</span><h2>Ranked investigations</h2></div><span className="ranking-count">TOP {String(ordered.length).padStart(2,'0')}</span></div><p className="panel-description">Sorted by transparent domain and keyword matching using the chosen context. Scores are editorial UI indices.</p>
      <div className="ranking-list">{ordered.map((s,i)=><button key={s.id} className={`ranking-item ${selected===s.id?'active':''}`} onClick={()=>setSelected(s.id)}><span className="ranking-pos">{String(i+1).padStart(2,'0')}</span><span className="ranking-content"><strong>{s.title}</strong><small>{s.longTitle}</small></span><DomainTag domain={s.domain}/><span className="ranking-bar"><span style={{width:`${score(s)}%`}}/></span><span className="ranking-number">{score(s)}<small>/100</small></span><ArrowUpRight size={16}/></button>)}</div>
    </section><div className="intel-aside">
      <section className="surface-panel selected-intel"><div className="panel-header"><div><span className="micro-label">WHY THIS STUDY?</span><h2>Evidence spotlight</h2></div><ArrowUpRight size={18}/></div><StudyVisual study={focus} size="wide"/><div className="selected-intel-inner"><DomainTag domain={focus.domain}/><h3>{focus.title}</h3><p>{focus.insight}</p><span className="detail-label">WHY IT MATCHES THIS LENS</span><div className="matching-chips">{focus.keywords.map(x=><span key={x}>{x}</span>)}</div><Link href={`/explorer?study=${encodeURIComponent(focus.id)}`} className="btn btn-secondary">Open investigation <ArrowRight size={16}/></Link></div></section>
      <section className="surface-panel evidence-gaps"><div className="panel-header"><div><span className="micro-label">UNCERTAINTY MATTERS</span><h2>Evidence gaps</h2></div><ShieldAlert size={20}/></div><div className="gap-item"><span className="gap-symbol">01</span><div><strong>Partial-gravity combustion</strong><p>No direct lunar-g or Martian-g PSI datasets reported in the challenge brief.</p></div></div><div className="gap-item"><span className="gap-symbol">02</span><div><strong>Habitat-specific conditions</strong><p>Real engineering analysis needs full atmospheric, material and ventilation specifications.</p></div></div><div className="gap-item"><span className="gap-symbol">03</span><div><strong>Measured prediction accuracy</strong><p>No validated flammability prediction model is running in this demo.</p></div></div></section>
    </div></div>
    <section className="research-explanation"><div className="research-explanation-icon"><Sparkles size={25}/></div><div><span className="micro-label">HOW IT WORKS</span><h2>Explainable first. Predictive later.</h2><p>To produce a reliable fire-safety model, the next stage is to ingest documented PSI run-level results, normalize oxygen, pressure, flow and sample geometry, and validate any model against held-out measurements.</p></div><Link href="/explorer" className="btn btn-secondary">Browse evidence <ArrowRight size={16}/></Link></section>
    <DataCaution>Not a NASA rating, fire-probability estimate, mission certification, or safety recommendation. The relevance index ranks editorial study summaries only.</DataCaution>
  </div>;
}
