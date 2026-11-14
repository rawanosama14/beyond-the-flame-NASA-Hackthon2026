'use client';
import { useState } from 'react';
import { Activity, Atom, Box, CircleHelp, Eye, EyeOff, Layers3, RotateCcw, SlidersHorizontal, Sparkles, Wind } from 'lucide-react';
import { DataCaution, DemoBadge, FlameHero, PageHeader, Panel } from './ui';

export default function VisualLab(){
  const [oxygen,setOxygen]=useState(30);
  const [airflow,setAirflow]=useState(false);
  const [overlay,setOverlay]=useState(true);
  const [guides,setGuides]=useState(true);
  const [frame,setFrame]=useState(38);
  function reset(){setOxygen(30);setAirflow(false);setOverlay(true);setGuides(true);setFrame(38)}
  return <div>
    <PageHeader index="04" eyebrow="VISUAL INTERPRETATION" title="Flame visual" accent="lab." description="A hands-on concept for examining what flame imagery could reveal. Every control here is illustrative, not a combustion simulator." action={<DemoBadge>CONCEPT ART · NOT MEASURED</DemoBadge>}/>
    <div className="visual-workbench"><div className="visual-stage"><div className="visual-stage-top"><span><span className="tiny-signal"/> MICROGRAVITY / ARTISTIC MODEL</span><span>SCENE 01 — SPHERICAL FLAME</span></div><FlameHero oxygen={oxygen} flow={airflow}/>
      {overlay&&<div className="visual-mask"><span className="mask-top-left">REGION OF INTEREST</span><span className="mask-bottom-right">ROI // SIMULATED</span></div>}
      {guides&&<div className="visual-guides"><i/><i/><i/><i/></div>}
      <div className="visual-stage-bottom"><span><span className="circle-online"/> VISUALIZATION ACTIVE</span><span>NO TRAINED MODEL CONNECTED</span></div>
    </div><aside className="visual-control-pane"><div className="visual-controls-head"><div><span className="micro-label">VISUAL CONTROL PANEL</span><h2>Experiment lens</h2></div><SlidersHorizontal size={19}/></div>
      <div className="visual-control-block"><div className="lens-label"><span>Concept oxygen input</span><strong>{oxygen}%</strong></div><input type="range" min="21" max="40" value={oxygen} onChange={e=>setOxygen(Number(e.target.value))} aria-label="Visualization oxygen input"/><div className="range-labels"><span>21%</span><span>40%</span></div><p className="visual-field-note">Adjusts the artistic glow only; not physical flame behavior.</p></div>
      <div className="visual-control-block"><div className="lens-label"><span>Visual motion</span><Wind size={18}/></div><button className={`toggle-row ${airflow?'enabled':''}`} role="switch" aria-checked={airflow} onClick={()=>setAirflow(v=>!v)}><span>Enable airflow-style animation</span><i/></button></div>
      <div className="visual-control-block"><div className="lens-label"><span>Observation layers</span><Layers3 size={18}/></div><button className={`toggle-row ${overlay?'enabled':''}`} role="switch" aria-checked={overlay} onClick={()=>setOverlay(v=>!v)}><span>Region-of-interest overlay</span><i/></button><button className={`toggle-row ${guides?'enabled':''}`} role="switch" aria-checked={guides} onClick={()=>setGuides(v=>!v)}><span>Measurement guides</span><i/></button></div>
      <button onClick={reset} className="btn btn-secondary visual-reset"><RotateCcw size={16}/> Reset view</button>
      <div className="visual-warning"><CircleHelp size={17}/><span>No NASA video is being segmented. The image is an original vector illustration and the controls do not represent test results.</span></div>
    </aside></div>
    <div className="visual-secondary-grid"><Panel title="Frame exploration" eyebrow="STORYBOARD / SIMULATION PLANNING"><div className="timeline-info"><span>FRAME PREVIEW</span><strong>{String(frame).padStart(3,'0')} <small>/ 100</small></strong></div><input className="timeline-slider" type="range" min="0" max="100" value={frame} onChange={e=>setFrame(Number(e.target.value))} aria-label="Storyboard frame"/><div className="timeline-axis"><span>START</span><span>SIMULATED FRAMES · NO VIDEO</span><span>END</span></div><p className="timeline-caption">Prototype of how a genuine video scrubber would work once documented experiment imagery is connected.</p></Panel>
      <Panel title="Future computer vision outputs" eyebrow="MEASUREMENT ROADMAP"><div className="future-metrics"><div><span><Activity size={19}/></span><strong>Flame region area</strong><small>Pending segmentation model</small></div><div><span><Box size={19}/></span><strong>Flame centroid</strong><small>Pending validated frames</small></div><div><span><Wind size={19}/></span><strong>Optical flow</strong><small>Pending motion analysis</small></div></div></Panel>
    </div>
    <div className="visual-learnings"><span className="micro-label">SCIENCE NOTE</span><h2>Why does fire look different in microgravity?</h2><p>On Earth, buoyancy carries hot gases upward. In microgravity that mechanism is greatly reduced, so flames can become roughly spherical and oxygen transport may be governed more strongly by diffusion and imposed airflow. This is a conceptual illustration, not a reconstruction of a specific NASA run.</p></div>
    <DataCaution>The visual is not a measured flame, a predictive CFD model, or a NASA asset. Please do not use the sliders or ROI artwork to infer ignition, spreading, extinction or detector thresholds.</DataCaution>
  </div>;
}
