'use client';
import { ArrowLeftRight, ArrowRight, ExternalLink, GitCompareArrows, Layers2 } from 'lucide-react';
import { useWorkspace } from './app-shell';
import { DataCaution, DomainTag, PageHeader, StudyVisual } from './ui';
import { investigations } from '@/lib/research';

const rows = [
  ['Objective', 'objective'], ['Safety domain', 'domain'], ['Experimental hardware', 'platform'],
  ['Fuel / material', 'fuel'], ['Oxygen conditions', 'oxygen'], ['Airflow conditions', 'airflow'],
  ['Measurement focus', 'measurements'], ['Research contribution', 'insight']
] as const;
export default function Compare(){
  const {compareIds,setCompareIds}=useWorkspace();
  const a=investigations.find(x=>x.id===compareIds[0])||investigations[0];
  const b=investigations.find(x=>x.id===compareIds[1])||investigations[1];
  const common=a.keywords.filter(x=>b.keywords.includes(x));
  return <div>
    <PageHeader index="02" eyebrow="CROSS-STUDY ANALYSIS" title="Study" accent="comparison." description="Compare objectives, research hardware, atmosphere and measured phenomena—not just investigation titles." action={<span className="tiny-label-status"><Layers2 size={16}/> TWO-SOURCE COMPARISON</span>}/>
    <div className="comparison-selector"><div className="comparison-selector-field"><label>INVESTIGATION A</label><select value={a.id} onChange={e=>setCompareIds([e.target.value,b.id])}>{investigations.map(x=><option key={x.id} value={x.id} disabled={x.id===b.id}>{x.title} — {x.longTitle}</option>)}</select></div><button aria-label="Swap investigations" className="swap-button" onClick={()=>setCompareIds([b.id,a.id])}><ArrowLeftRight size={20}/></button><div className="comparison-selector-field"><label>INVESTIGATION B</label><select value={b.id} onChange={e=>setCompareIds([a.id,e.target.value])}>{investigations.map(x=><option key={x.id} value={x.id} disabled={x.id===a.id}>{x.title} — {x.longTitle}</option>)}</select></div></div>
    <div className="comparison-heading-grid"><div className="comparison-heading"><StudyVisual study={a} size="wide"/><div className="comparison-heading-body"><DomainTag domain={a.domain}/><h2>{a.title}</h2><p>{a.longTitle}</p><a href={a.source} target="_blank" rel="noopener noreferrer">View source <ExternalLink size={14}/></a></div></div><span className="compare-vs">VS</span><div className="comparison-heading"><StudyVisual study={b} size="wide"/><div className="comparison-heading-body"><DomainTag domain={b.domain}/><h2>{b.title}</h2><p>{b.longTitle}</p><a href={b.source} target="_blank" rel="noopener noreferrer">View source <ExternalLink size={14}/></a></div></div></div>
    <section className="comparison-table"><div className="comparison-table-title"><span className="micro-label">INVESTIGATION MATRIX</span><h3>Side by side, detail by detail.</h3></div>{rows.map(([label,key],index)=><div className="comparison-row" key={key}><div className="comparison-value"><span className="comparison-cell-no">A / {String(index+1).padStart(2,'0')}</span>{a[key]}</div><div className="comparison-row-label">{label}</div><div className="comparison-value"><span className="comparison-cell-no">B / {String(index+1).padStart(2,'0')}</span>{b[key]}</div></div>)}</section>
    <section className="comparison-takeaway"><div><span className="micro-label">INTERPRETATION · EDITORIAL</span><h2>What connects these studies?</h2><p>{common.length ? `Both investigations touch on ${common.join(', ').toLowerCase()}. Similar keywords can guide a deeper look, but shared labels do not mean test conditions or measurements are directly comparable.` : `These investigations focus on different research questions. Cross-domain comparison can help connect prevention, detection and suppression needs, but cannot establish experimental equivalence.`}</p></div><GitCompareArrows size={49} strokeWidth={1.1}/></section>
    <DataCaution>This comparison uses curated study summaries. It does not compare raw NASA PSI run-level observations; a scientifically rigorous comparison needs matched experimental conditions and source datasets.</DataCaution>
  </div>;
}
