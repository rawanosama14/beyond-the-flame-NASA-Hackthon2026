'use client';
import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react';
import { ArrowRight, ArrowUpRight, BookOpenText, Bot, CircleHelp, CornerDownLeft, ExternalLink, Info, MessageCircle, RotateCcw, SendHorizontal, ShieldCheck, Sparkles, UserRound } from 'lucide-react';
import { useWorkspace } from './app-shell';
import { DataCaution, DemoBadge, PageHeader } from './ui';
import { NASA_RESOURCES, scenarios } from '@/lib/research';

type Message={role:'assistant'|'user';text:string;refs?:{title:string;url:string}[]};
const initial:Message={role:'assistant',text:'Welcome to your microgravity research desk. Ask me about solid-fuel flammability, smoke detection, flame extinction, or investigation comparisons. I’ll separate what the challenge brief says from what still needs source data.',refs:[{title:'NASA PSI repository',url:'https://psi.nasa.gov/'}]};
const prompts=[
  'Which experiments best inform Moon base fire prevention?',
  'Why does smoke detection change in microgravity?',
  'Compare BASS-II and FLEX for fire suppression.',
  'What do we know about partial gravity on the Moon?'
];
function demoReply(input:string,scenario:string):Message{
  const q=input.toLowerCase();
  const refs=[{title:'NASA PSI research portal',url:'https://psi.nasa.gov/'},{title:'NASA Combustion Science',url:'https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/'}];
  if(/partial|moon gravity|mars gravity|lunar.g/.test(q))return {role:'assistant',text:'According to the challenge brief, NASA PSI currently has no direct partial-gravity combustion datasets for lunar or Martian gravity. ACME’s E-FIELD Flames used electric fields to mimic some gravity-like flame effects, but this is not a substitute for actual partial-g observations. LUCI and FM2 are identified as future research paths. Any transfer of microgravity results to a lunar base needs explicit uncertainty handling.',refs};
  if(/smoke|detect|same|aerosol|sensor/.test(q))return {role:'assistant',text:'SAME and SAME-R are the most directly relevant investigations for spacecraft smoke and aerosol measurement. In low gravity, smoke does not benefit from the same buoyant rise seen on Earth; ventilation and particle transport are therefore important to sensing strategy. DAFT/DAFT-2 also reused an instrument for dust measurements. A real detector recommendation would require run-level particle distributions, airflow conditions, and sensor calibration data.',refs:[{title:'NASA PSI · SAME-R',url:'https://psi.nasa.gov/physci/repo/data/investigations/PSI-101'},...refs]};
  if(/flex|extinguish|suppression|helium|carbon/.test(q))return {role:'assistant',text:'FLEX studied liquid-fuel droplet combustion and flame extinction. The challenge brief describes suppressing flames through atmospheric dilution with carbon dioxide or helium. BASS/BASS-II instead examine solid fuels, so the investigations address different fuel geometries and test conditions. Comparing extinction thresholds responsibly requires actual PSI measurements, not just study descriptions.',refs};
  if(/bass|saffire|material|fabric|plastic|prevent|flammab|oxygen|moon base|rover/.test(q))return {role:'assistant',text:`For a ${scenario.toLowerCase()}, the challenge brief makes solid-material flammability and oxygen conditions especially relevant. BASS and BASS-II study burning/suppression of solids in microgravity; Saffire I–III examine fire behavior at larger scale. The brief suggests future lunar habitats may use ≥30% oxygen at ≤10.2 psi, but those are planning-context figures, not a finalized cabin specification. CFI-G’s up-to-85% oxygen refers to an oxidizer stream at a spherical burner, not a crew atmosphere. Test-by-test comparisons should use original PSI records.`,refs};
  if(/cool flame|cfi.g|cfi-g|acme|electric|bre/.test(q))return {role:'assistant',text:'ACME contains several investigations using shared gaseous-fuel hardware in the Combustion Integrated Rack. BRE focuses on burning-rate behavior relevant to material flammability in still atmospheres. CFI-G (Cool Flames Investigation with Gases) tested inside-out flames with an oxygen–nitrogen burner stream up to 85% O₂. E-FIELD Flames explored electric-field effects on flame ions as a partial-gravity analogue. Their relevance depends on the exact research question; none directly establishes Moon-base fire risk.',refs};
  return {role:'assistant',text:'I can help locate the right research direction from the supplied challenge context, but this offline demo is not connected to NASA PSI or a language model. Try asking about BASS, Saffire, SAME-R, FLEX, oxygen-rich habitats, ACME, or partial gravity. For quantitative findings, the next step is ingesting the source dataset and attaching citations to exact experiment runs.',refs};
}
export default function Copilot(){
  const {scenario}=useWorkspace();
  const [messages,setMessages]=useState<Message[]>([initial]);
  const [input,setInput]=useState('');
  const [busy,setBusy]=useState(false);
  const end=useRef<HTMLDivElement>(null);
  const API=process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/,'')||'';
  useEffect(()=>{end.current?.scrollIntoView({behavior:'smooth',block:'nearest'})},[messages,busy]);
  async function ask(message?:string){
    const question=(message||input).trim();if(!question||busy)return;
    setMessages(old=>[...old,{role:'user',text:question}]);setInput('');
    if(!API){setMessages(old=>[...old,demoReply(question,scenario)]);return}
    setBusy(true);
    try{
      const response=await fetch(`${API}/api/chat`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:question,scenario})});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const data:unknown=await response.json();
      const parsed=data as {answer?:unknown;response?:unknown;citations?:{title?:unknown;url?:unknown}[]};
      const answer=typeof parsed.answer==='string'?parsed.answer:typeof parsed.response==='string'?parsed.response:null;
      if(!answer)throw new Error('No answer in API response');
      const citations=Array.isArray(parsed.citations)?parsed.citations.filter(x=>typeof x.title==='string'&&typeof x.url==='string'&&/^https?:\/\//.test(x.url)).map(x=>({title:String(x.title),url:String(x.url)})):[];
      setMessages(old=>[...old,{role:'assistant',text:answer,refs:citations}]);
    }catch(err){setMessages(old=>[...old,{role:'assistant',text:`The configured research API could not provide a response (${err instanceof Error?err.message:'unknown error'}). No fabricated AI answer has been substituted. Check NEXT_PUBLIC_API_BASE_URL and the POST /api/chat contract.`}])}
    finally{setBusy(false)}
  }
  function submit(e:FormEvent){e.preventDefault();void ask()}
  function onKeys(e:KeyboardEvent<HTMLTextAreaElement>){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();void ask()}}
  return <div>
    <PageHeader index="05" eyebrow="RESEARCH ASSISTANT" title="Research" accent="copilot." description="A quiet place for big questions. Designed for source-aware scientific research, with a working guided demo today." action={<DemoBadge>{API?'EXTERNAL API CONFIGURED':'OFFLINE RESEARCH DEMO'}</DemoBadge>}/>
    <div className="copilot-grid"><section className="chat-surface"><div className="chat-top"><div className="chat-top-icon"><Sparkles size={22}/></div><div><strong>Beyond the Flame <span>Research AI</span></strong><small><span className="tiny-signal"/> {API?'External API configured':'Interactive offline demonstration'}</small></div><button className="icon-button" title="Clear conversation" aria-label="Clear conversation" onClick={()=>setMessages([initial])}><RotateCcw size={18}/></button></div>
      <div className="chat-context"><span>ACTIVE RESEARCH CONTEXT</span><strong>{scenario}</strong><span className="context-point">•</span><span>NASA combustion research</span></div>
      <div className="chat-messages" role="log" aria-live="polite">{messages.map((x,i)=><div key={i} className={`chat-message ${x.role}`}><span className="chat-message-avatar">{x.role==='assistant'?<Sparkles size={19}/>:<UserRound size={18}/>}</span><div className="chat-message-body"><span className="chat-message-author">{x.role==='assistant'?'RESEARCH COPILOT':'YOU'}</span><p>{x.text}</p>{x.refs&&x.refs.length>0&&<div className="chat-message-refs">{x.refs.map((r,j)=><a href={r.url} target="_blank" rel="noopener noreferrer" key={`${r.url}-${j}`}><BookOpenText size={13}/>{r.title}<ArrowUpRight size={13}/></a>)}</div>}{x.role==='assistant'&&<span className="chat-message-foot">{API?'VERIFY ANSWER AGAINST SOURCE':'GUIDED DEMO · NOT GENERATED BY A LIVE AI MODEL'}</span>}</div></div>)}{busy&&<div className="chat-loading"><span/><span/><span/><small>Researching connected sources...</small></div>}<div ref={end}/></div>
      <div className="chat-bottom"><div className="prompt-chips">{prompts.slice(0,2).map(x=><button key={x} onClick={()=>void ask(x)}>{x}<ArrowUpRight size={13}/></button>)}</div><form className="chat-composer" onSubmit={submit}><textarea aria-label="Ask a question about microgravity fire research" placeholder="Ask anything about microgravity combustion..." value={input} onChange={e=>setInput(e.target.value)} onKeyDown={onKeys} rows={2} maxLength={2000}/><button disabled={!input.trim()||busy} type="submit" aria-label="Send question"><ArrowRight size={23}/></button></form><div className="chat-help"><span>NO NASA DATA CONNECTED YET · CHECK SOURCES</span><span><CornerDownLeft size={13}/> Enter to send · Shift + Enter for a new line</span></div></div>
    </section><aside className="copilot-side">
      <section className="surface-panel prompt-starters"><div className="panel-header"><div><span className="micro-label">START WITH CURIOSITY</span><h2>Suggested questions</h2></div><Sparkles size={18}/></div>{prompts.map((x,i)=><button key={x} onClick={()=>void ask(x)}><span>0{i+1}</span><strong>{x}</strong><ArrowUpRight size={17}/></button>)}</section>
      <section className="surface-panel source-list"><div className="panel-header"><div><span className="micro-label">RESEARCH BASE</span><h2>NASA source trail</h2></div><BookOpenText size={19}/></div>{NASA_RESOURCES.map(x=><a key={x.url} href={x.url} target="_blank" rel="noopener noreferrer"><span className="source-list-icon"><BookOpenText size={18}/></span><span><strong>{x.title}</strong><small>{x.detail}</small></span><ArrowUpRight size={17}/></a>)}</section>
      <div className="copilot-notice"><ShieldCheck size={22}/><div><strong>Evidence over confidence.</strong><p>The copilot will be most useful once every answer can point to exact investigations, test conditions and source documents.</p></div></div>
    </aside></div>
    <DataCaution>{API?'A custom backend URL is configured. This frontend cannot independently validate the accuracy of its responses; verify all evidence and citations.':'This is an offline guided response demo, not live SI/AI, not a NASA data search, and not a safety-certified decision system. Connect an actual research RAG backend in a later phase.'}</DataCaution>
  </div>;
}
