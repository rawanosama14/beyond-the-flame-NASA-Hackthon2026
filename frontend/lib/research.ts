export type Domain = 'Prevention' | 'Detection' | 'Suppression' | 'Foundations';
export type Scenario = 'Moon base' | 'Space station' | 'Mars habitat' | 'Pressurized rover';
export type Investigation = {
  id: string;
  title: string;
  longTitle: string;
  domain: Domain;
  summary: string;
  insight: string;
  objective: string;
  platform: string;
  fuel: string;
  oxygen: string;
  airflow: string;
  measurements: string;
  keywords: string[];
  source: string;
  sourceName: string;
  accent: 'orange' | 'cyan' | 'violet' | 'mint';
};

/**
 * Editorial descriptions curated from the user-supplied 2026 challenge brief.
 * They are not experimental datasets. Unknown values stay "Not specified".
 * Per-study scores anywhere in the UI are a transparent prototype ranking,
 * never NASA measurements or actual flammability predictions.
 */
export const investigations: Investigation[] = [
  {
    id: 'BASS', title: 'BASS', longTitle: 'Burning and Suppression of Solids', domain: 'Prevention',
    summary: 'How solid materials burn and extinguish when buoyant airflow is absent.',
    insight: 'Directly relevant to material selection and flame-spread questions inside crewed habitats.',
    objective: 'Study solid-fuel burning and suppression in microgravity.', platform: 'ISS · Microgravity Science Glovebox (MSG)',
    fuel: 'Solid samples · fabrics and plastics', oxygen: 'Varies by test · consult original datasets',
    airflow: 'Fan-driven experimental flow duct', measurements: 'Combustion behavior · flame spread · extinction',
    keywords: ['Solid fuels', 'Materials', 'Flow'], source: 'https://www.nasa.gov/wp-content/uploads/2025/07/burning-and-suppression-of-solids-bass.pdf', sourceName: 'NASA BASS overview', accent: 'orange'
  },
  {
    id: 'BASS-II', title: 'BASS-II', longTitle: 'Burning and Suppression of Solids II', domain: 'Prevention',
    summary: 'Follow-on investigation into solid-fuel flame spread and suppression in microgravity.',
    insight: 'Useful alongside BASS when evaluating ventilation-sensitive material behavior.',
    objective: 'Characterize how solid-fuel burning responds to microgravity test conditions.', platform: 'ISS · MSG · SPICE flow duct',
    fuel: 'Solid samples · material shapes vary', oxygen: 'Test-dependent · inspect PSI record',
    airflow: 'Controlled fan-driven airflow', measurements: 'Flame behavior · spread · extinction',
    keywords: ['Solid fuels', 'Materials', 'Flow'], source: 'https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/', sourceName: 'NASA Combustion Science', accent: 'orange'
  },
  {
    id: 'SAFFIRE', title: 'Saffire I–III', longTitle: 'Spacecraft Fire Safety Demonstration (I, II & III)', domain: 'Prevention',
    summary: 'Larger-scale material-burning experiments in a spacecraft-like environment.',
    insight: 'Brings scale and enclosure context to flame propagation research.',
    objective: 'Explore fire growth and material flame spread at larger scales.', platform: 'Uncrewed Cygnus spacecraft after ISS departure',
    fuel: 'Solid materials · fabrics and other spacecraft-relevant samples', oxygen: 'Experiment-dependent',
    airflow: 'Spacecraft-relevant ventilation conditions', measurements: 'Fire spread · imagery · environmental conditions',
    keywords: ['Solid fuels', 'Materials', 'Habitat'], source: 'https://svs.gsfc.nasa.gov/31394/', sourceName: 'NASA SVS microgravity fire', accent: 'orange'
  },
  {
    id: 'SAME', title: 'SAME', longTitle: 'Smoke and Aerosol Measurement Experiment', domain: 'Detection',
    summary: 'Examines smoke and aerosol behavior to inform spacecraft fire detection.',
    insight: 'Helps connect smoke characteristics to sensor design and alarm strategies.',
    objective: 'Characterize smoke/aerosol measurements in low gravity.', platform: 'ISS · microgravity research hardware',
    fuel: 'Smoke from experimental sources', oxygen: 'Not specified in challenge brief',
    airflow: 'Microgravity aerosol transport', measurements: 'Smoke/aerosol properties · detector signals',
    keywords: ['Smoke', 'Sensors', 'Aerosols'], source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'cyan'
  },
  {
    id: 'SAME-R', title: 'SAME-R', longTitle: 'Smoke and Aerosol Measurement Experiment — Reflight', domain: 'Detection',
    summary: 'Follow-up measurements of airborne particles and detection-relevant smoke.',
    insight: 'A strong evidence starting point for early-warning systems in crewed modules.',
    objective: 'Extend smoke and aerosol characterization under low gravity.', platform: 'ISS · smoke/aerosol research hardware',
    fuel: 'Particle-generating test sources', oxygen: 'Not specified in challenge brief',
    airflow: 'Test-dependent aerosol transport', measurements: 'Smoke particle characteristics · aerosol sensing',
    keywords: ['Smoke', 'Sensors', 'Aerosols'], source: 'https://psi.nasa.gov/physci/repo/data/investigations/PSI-101', sourceName: 'NASA PSI · SAME-R', accent: 'cyan'
  },
  {
    id: 'FLEX', title: 'FLEX', longTitle: 'Flame Extinguishment Experiment', domain: 'Suppression',
    summary: 'Studies liquid droplet flames and how gas dilution can suppress them.',
    insight: 'Direct foundation for understanding carbon dioxide and helium as extinguishing diluents.',
    objective: 'Examine droplet combustion and flame extinguishment.', platform: 'ISS · Combustion Integrated Rack · MDCA',
    fuel: 'Liquid fuel droplets', oxygen: 'Varies with chamber-mixture conditions',
    airflow: 'Controlled chamber environment', measurements: 'Droplet combustion · extinction response',
    keywords: ['Droplets', 'Extinguishment', 'Diluents'], source: 'https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/', sourceName: 'NASA Combustion Science', accent: 'violet'
  },
  {
    id: 'FLEX-2', title: 'FLEX-2', longTitle: 'Flame Extinguishment Experiment — 2', domain: 'Suppression',
    summary: 'Additional microgravity droplet-combustion research using the MDCA platform.',
    insight: 'Useful for comparing liquid-fuel flame regimes and extinction mechanisms.',
    objective: 'Expand knowledge of burning droplets in reduced gravity.', platform: 'ISS · CIR · Multi-user Droplet Combustion Apparatus',
    fuel: 'Liquid fuel droplets', oxygen: 'Test-dependent', airflow: 'Chamber-controlled environment',
    measurements: 'Droplet combustion · flame response', keywords: ['Droplets', 'Extinguishment'],
    source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'violet'
  },
  {
    id: 'CFI', title: 'CFI', longTitle: 'Cool Flames Investigation', domain: 'Foundations',
    summary: 'Uses liquid-fuel droplets to study low-temperature combustion behavior.',
    insight: 'Important combustion physics, but not a direct habitat hazard test.',
    objective: 'Investigate cool-flame phenomena in droplet combustion.', platform: 'ISS · CIR · MDCA',
    fuel: 'Liquid fuel droplets', oxygen: 'Test-dependent', airflow: 'Controlled chamber environment',
    measurements: 'Flame behavior · droplet evolution', keywords: ['Droplets', 'Cool flames'],
    source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'mint'
  },
  {
    id: 'BRE', title: 'BRE', longTitle: 'Burning Rate Emulator · ACME', domain: 'Prevention',
    summary: 'Gaseous-fuel experiment designed to illuminate material flammability in still atmospheres.',
    insight: 'Provides a bridge between controlled flame physics and material burning rate.',
    objective: 'Study burning rate as a function of material-like properties.', platform: 'ISS · ACME hardware · CIR',
    fuel: 'Gaseous fuels · emulated burning surfaces', oxygen: 'Test-dependent', airflow: 'Still-atmosphere focus',
    measurements: 'Burning rate · flame response', keywords: ['Gaseous fuels', 'Materials', 'Still air'],
    source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'orange'
  },
  {
    id: 'CFI-G', title: 'CFI-G', longTitle: 'Cool Flames Investigation with Gases · ACME', domain: 'Foundations',
    summary: 'Inside-out gaseous flames with oxygen-rich mixtures delivered through a spherical burner.',
    insight: 'Oxygen delivery up to 85% in the burner stream is a key experimental context—not an 85% cabin-atmosphere test.',
    objective: 'Study gaseous cool-flame phenomena with controlled oxidizer supply.', platform: 'ISS · ACME hardware · CIR',
    fuel: 'Gaseous fuel around burner · e.g. propane mixtures', oxygen: 'Up to 85% O₂ in the burner oxidizer stream',
    airflow: 'Oxygen–nitrogen mixture through a spherical burner', measurements: 'Flame structure · combustion behavior',
    keywords: ['Gaseous fuels', 'Oxygen', 'Cool flames'], source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'mint'
  },
  {
    id: 'E-FIELD', title: 'E-FIELD', longTitle: 'Electric-Field Effects on Laminar Diffusion Flames · ACME', domain: 'Foundations',
    summary: 'Explores how electric forces on flame ions can mimic some effects of gravity.',
    insight: 'An experimental analogue—not measured lunar or Martian partial-gravity fire behavior.',
    objective: 'Investigate electric-field effects on diffusion flames.', platform: 'ISS · ACME hardware · CIR',
    fuel: 'Gaseous fuels', oxygen: 'Test-dependent', airflow: 'Controlled laminar diffusion flame',
    measurements: 'Flame shape · field-response behavior', keywords: ['Electric field', 'Partial-g analogue'],
    source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'mint'
  },
  {
    id: 'DAFT', title: 'DAFT / DAFT-2', longTitle: 'Dust and Aerosol Measurement Feasibility Tests', domain: 'Detection',
    summary: 'Dust-detection applications of an instrument also used for microgravity smoke studies.',
    insight: 'A useful adjacent sensor study, but it is not a direct smoke-fire experiment.',
    objective: 'Evaluate dust and aerosol measurement feasibility.', platform: 'ISS · aerosol sensing hardware',
    fuel: 'No combustion fuel · dust/aerosol study', oxygen: 'Not applicable', airflow: 'Aerosol transport',
    measurements: 'Particle detection · sensing response', keywords: ['Aerosols', 'Sensors', 'Dust'],
    source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'cyan'
  },
  {
    id: 'SPICE / SLICE', title: 'SPICE / SLICE', longTitle: 'Smoke Point In Co-flow / Structure & Liftoff In Combustion', domain: 'Foundations',
    summary: 'Flame-structure research using gaseous fuels and modular duct hardware also shared with BASS.',
    insight: 'Useful for cross-study comparisons of apparatus and airflow effects.',
    objective: 'Study gaseous flame smoke point, structure, and liftoff.', platform: 'ISS · MSG · SPICE modular fan-driven duct',
    fuel: 'Gaseous fuels', oxygen: 'Test-dependent', airflow: 'Controlled co-flow/duct conditions',
    measurements: 'Flame structure · smoke point · liftoff', keywords: ['Gaseous fuels', 'Flow', 'Hardware'],
    source: 'https://psi.nasa.gov/', sourceName: 'NASA PSI repository', accent: 'mint'
  }
];

export const scenarios: Record<Scenario, { label: string; eyebrow: string; copy: string; atmosphere: string; note: string }> = {
  'Moon base': {
    label: 'Lunar habitat', eyebrow: 'SURFACE OPERATIONS',
    copy: 'Explore material selection, oxygen enrichment and detection needs for long-duration surface habitats.',
    atmosphere: '≥30% O₂ · ≤10.2 psi (planning context)',
    note: 'The challenge outlines a possible oxygen-enriched, lower-pressure habitat. It is not a final mission specification.'
  },
  'Space station': {
    label: 'Orbital station', eyebrow: 'MICROGRAVITY OPERATIONS',
    copy: 'Study the fire prevention, smoke detection and suppression evidence most directly connected to microgravity.',
    atmosphere: 'Microgravity · ventilated cabin',
    note: 'Experimental results are not substitutes for spacecraft-specific engineering qualification.'
  },
  'Mars habitat': {
    label: 'Mars habitat', eyebrow: 'PLANETARY OPERATIONS',
    copy: 'Track transferable findings and major uncertainty around partial gravity and future habitat atmospheres.',
    atmosphere: 'Partial gravity · habitat design TBD',
    note: 'No direct partial-gravity combustion datasets are reported in PSI by the challenge brief.'
  },
  'Pressurized rover': {
    label: 'Surface rover', eyebrow: 'MOBILE HABITATS',
    copy: 'Prioritize compact, enclosed habitat safety: material flammability, early smoke detection and suppression.',
    atmosphere: 'Enclosed volume · possible oxygen enrichment',
    note: 'Rover atmosphere and ventilation parameters depend on mission engineering choices.'
  }
};

/** A purely editorial relevance ordering. NOT fire risk or experimental findings. */
export function relevanceScore(item: Investigation, scenario: Scenario, oxygen = 30): number {
  const baselines: Record<Domain, number> = { Prevention: 79, Detection: 73, Suppression: 72, Foundations: 57 };
  let n = baselines[item.domain];
  if (scenario === 'Moon base' || scenario === 'Pressurized rover') {
    if (item.keywords.includes('Materials')) n += 12;
    if (item.keywords.includes('Sensors')) n += 9;
    if (item.keywords.includes('Oxygen')) n += 7;
  }
  if (scenario === 'Space station') {
    if (['SAME-R', 'BASS-II', 'FLEX', 'SAFFIRE'].includes(item.id)) n += 12;
    if (item.keywords.includes('Flow')) n += 6;
  }
  if (scenario === 'Mars habitat') {
    if (item.keywords.includes('Materials')) n += 9;
    if (item.keywords.includes('Partial-g analogue')) n += 7;
    if (item.keywords.includes('Sensors')) n += 6;
  }
  if (oxygen >= 30 && (item.keywords.includes('Oxygen') || item.keywords.includes('Materials'))) n += 4;
  const tieBreaker = Math.min(4, item.id.length % 5);
  return Math.min(97, n + tieBreaker);
}
export function rankedInvestigations(scenario: Scenario, oxygen = 30) {
  return [...investigations].sort((a, b) => relevanceScore(b, scenario, oxygen) - relevanceScore(a, scenario, oxygen));
}
export const domains: { id: Domain; description: string; sub: string }[] = [
  { id: 'Prevention', description: 'Build safer materials and limit ignition pathways.', sub: 'Material flammability · ventilation' },
  { id: 'Detection', description: 'See smoke earlier and interpret aerosols correctly.', sub: 'Smoke particles · sensors' },
  { id: 'Suppression', description: 'Understand how flames extinguish in low gravity.', sub: 'Droplets · dilution' },
  { id: 'Foundations', description: 'Connect core flame physics to mission questions.', sub: 'Cool flames · gas transport' }
];
export const NASA_RESOURCES = [
  { title: 'NASA Physical Science Informatics', detail: 'Primary experimental data repository', url: 'https://psi.nasa.gov/' },
  { title: 'NASA Combustion Science', detail: 'Official research program overview', url: 'https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/' },
  { title: 'NASA SVS · Fire in Microgravity', detail: 'Research storytelling and visual assets', url: 'https://svs.gsfc.nasa.gov/31394/' }
];
