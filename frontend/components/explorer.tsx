'use client';
import { useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, ArrowRight, ArrowUpRight, Check, Download, ExternalLink, Filter, GitCompareArrows, Microscope, Search, SlidersHorizontal, X } from 'lucide-react';
import { useWorkspace } from './app-shell';
import { DataCaution, DemoBadge, DomainTag, ExternalLinkText, PageHeader, StudyVisual } from './ui';
import { investigations, type Domain } from '@/lib/research';
import { csvFromInvestigations, downloadText } from '@/lib/utils';

const filters = ['All studies', 'Prevention', 'Detection', 'Suppression', 'Foundations'] as const;
type Filter = (typeof filters)[number];
export default function Explorer(){
  const router=useRouter(); const params=useSearchParams();
  const [filter,setFilter]=useState<Filter>('All studies');
  const [query,setQuery]=useState('');
  const [selected,setSelected]=useState<string>('BASS-II');
  const { compareIds,setCompareIds }=useWorkspace();
  useEffect(()=>{
    const d=params.get('domain');const study=params.get('study');
    if(filters.includes(d as Filter))setFilter(d as Filter);
    if(study&&investigations.some(s=>s.id===study))setSelected(study);
  },[params]);
  const matching=useMemo(()=>investigations.filter(x=>{
    const domain=filter==='All studies'||x.domain===filter;
    const text=`${x.id} ${x.title} ${x.longTitle} ${x.summary} ${x.keywords.join(' ')} ${x.fuel}`.toLowerCase();
    return domain&&text.includes(query.toLowerCase().trim());
  }),[filter,query]);
  const detail=investigations.find(x=>x.id===selected)||investigations[0];
  function select(id:string){setSelected(id);router.replace(`/explorer?study=${encodeURIComponent(id)}${filter==='All studies'?'':`&domain=${filter}`}`,{scroll:false})}
  function queueCompare(){if(compareIds[0]===detail.id){router.push('/compare');return}setCompareIds([compareIds[0],detail.id]);router.push('/compare')}
  return <div>
    <PageHeader index="01" eyebrow="RESEARCH LIBRARY" title="Research" accent="explorer." description="An approachable index of microgravity combustion investigations. Search by study, safety domain, material or measurement." action={<button className="btn btn-secondary" onClick={()=>downloadText('research-index.csv',csvFromInvestigations(matching),'text/csv;charset=utf-8')}><Download size={16}/> Export results</button>}/>
    <div className="explorer-toolbar"><div className="search-field"><Search size={19}/><input placeholder="Search experiments, materials, smoke, oxygen..." value={query} onChange={e=>setQuery(e.target.value)}/>{query&&<button aria-label="Clear search" onClick={()=>setQuery('')}><X size={16}/></button>}</div><span className="results-pill">{matching.length} RESULTS</span></div>
    <div className="filter-toolbar"><div className="filter-scroll"><Filter size={17}/>{filters.map(f=><button key={f} className={`filter-chip ${filter===f?'active':''}`} onClick={()=>{setFilter(f);router.replace('/explorer',{scroll:false})}}>{f}{f!=='All studies'&&<span>{investigations.filter(x=>x.domain===f).length}</span>}</button>)}</div><span className="filter-hint"><SlidersHorizontal size={15}/> Curated descriptions</span></div>
    <div className="explorer-grid"><div className="explorer-results">
      {matching.length?matching.map((study,index)=><button key={study.id} onClick={()=>select(study.id)} className={`explorer-study ${selected===study.id?'active':''}`}>
        <StudyVisual study={study} size="small"/><div className="explorer-study-text"><span className="explorer-study-meta"><DomainTag domain={study.domain}/><span>STUDY {String(index+1).padStart(2,'0')}</span></span><strong>{study.title}<small>{study.longTitle}</small></strong><p>{study.summary}</p><span className="explorer-study-keywords">{study.keywords.slice(0,3).map(x=><i key={x}>{x}</i>)}</span></div><ArrowUpRight className="study-forward" size={19}/>
      </button>):<div className="empty-state"><Search size={31}/><h3>No investigations found</h3><p>Try a different keyword or safety category.</p><button className="btn btn-secondary" onClick={()=>{setQuery('');setFilter('All studies')}}>Clear filters</button></div>}
    </div>
    <aside className="study-detail"><div className="study-detail-top"><div><span className="micro-label">STUDY OVERVIEW</span><h2>{detail.title}</h2></div><DemoBadge>CURATED CONTEXT</DemoBadge></div><StudyVisual study={detail} size="wide"/><div className="detail-inner"><DomainTag domain={detail.domain}/><h3>{detail.longTitle}</h3><p className="detail-summary">{detail.insight}</p><div className="detail-label">EXPERIMENT AT A GLANCE</div>
      <div className="detail-fact-list"><div><span>Research objective</span><strong>{detail.objective}</strong></div><div><span>Research hardware</span><strong>{detail.platform}</strong></div><div><span>Fuel / material</span><strong>{detail.fuel}</strong></div><div><span>Oxygen condition</span><strong>{detail.oxygen}</strong></div><div><span>Airflow</span><strong>{detail.airflow}</strong></div><div><span>Measurements to investigate</span><strong>{detail.measurements}</strong></div></div>
      <div className="detail-buttons"><button className="btn btn-primary" onClick={queueCompare}><GitCompareArrows size={16}/> Compare study <ArrowRight size={16}/></button><a className="btn btn-secondary" href={detail.source} target="_blank" rel="noopener noreferrer">Research source <ExternalLink size={15}/></a></div><p className="detail-source-note">Source link: {detail.sourceName}. Some links open the NASA repository or program overview, not a direct dataset.</p></div>
    </aside></div>
    <DataCaution>Descriptions are based on the provided challenge briefing, not a fully indexed NASA PSI database. Where exact test parameters are unavailable, the interface says so rather than inventing measurements.</DataCaution>
  </div>;
}
