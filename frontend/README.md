# BEYOND THE FLAME 🚀

**A premium, Apple-inspired Next.js frontend for the 2026 NASA Space Apps Challenge — “Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion.”**

A complete **Day 1 frontend prototype** with six functional screens, responsive layouts, a command palette, theme switcher, experiment comparison, scenario-aware editorial rankings, an interactive vector visualization, and an offline research copilot demo.

## Quick start

Requirements: Node.js **20.9+** (Node 22 LTS recommended).

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Production check:

```bash
npm run lint
npm run build
npm start
```

> **Important:** This environment could not access the npm registry, so dependency installation / a running Next.js build could not be verified here. The project is provided as complete source code with standard dependency declarations. Run the commands above on a network-enabled development machine.

## Included frontend screens

| Route | What works today |
| --- | --- |
| `/dashboard` | Cinematic flame hero, investigation snapshot, safety pillars, mission context, recommended starting studies, CSV export |
| `/explorer` | Free-text search, domain filter, detailed study inspector, research source links, export filtered index, queue comparison |
| `/compare` | Choose two studies, swap sides, review experimental conditions and sources in a structured matrix |
| `/intelligence` | Select Moon / ISS / Mars / rover environment; oxygen and airflow editorial filters; transparent demo ranking; evidence spotlight |
| `/visual-lab` | Responsive animated original SVG flame, conceptual oxygen control, airflow-style motion, overlays, storyboard scrubber, reset |
| `/copilot` | Functional offline guided research responses, suggested prompts, citations to NASA starting resources, clear conversation |

Other interaction details:
- Press `⌘ K` (macOS) or `Ctrl K` (Windows/Linux) to search pages and investigations.
- Press `/` outside a text field to open the command menu.
- Dark/light theme toggle in the top navigation.
- Selected mission is persisted in `localStorage` between page visits.
- Responsive navigation drawer for tablets/mobile.
- Spring-inspired transitions, instant press feedback, translucent header layers, focus indicators, `prefers-reduced-motion`, and `prefers-reduced-transparency` support.
- Uses **system fonts**. No licensed Apple fonts are bundled or redistributed.

## Scientific integrity

This is a **frontend prototype**, not a production spacecraft hazard model.

- Study descriptions in `lib/research.ts` are curated from the **user-provided challenge briefing**, not ingested directly from NASA PSI datasets.
- The investigation count is the count of **curated groups displayed**, not NASA's total research inventory.
- All `0–100` relevance indices are **illustrative editorial ranking heuristics**. They are not measured flammability, risk probability, experimental data, NASA rankings, or validated recommendations.
- `≥30% O₂` lunar planning context is from the provided challenge; **not a final lunar-base specification**.
- CFI-G = **Cool Flames Investigation with Gases**, *not* a solid-material ignition study. Its reported up-to-85% oxygen refers to the **oxidizer stream from its spherical burner**, not crew cabin atmosphere.
- The provided challenge says PSI does not yet include direct partial-gravity combustion datasets. E-FIELD is an **analogue**, not lunar-g data.
- The visual lab is **original vector art** and an interaction concept, not NASA imagery or experimental frames. It does not run a computer vision model.
- The offline copilot uses a **deterministic set of guided reference answers**, not a connected LLM. It will never pretend to search NASA PSI.
- Never rely on this prototype for actual crew safety decisions.

## Backend / AI integration, later

No backend is needed for the first-day demonstration. When an API exists, set `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-api-host.example
```

Current copilot integration expects:

```http
POST /api/chat
Content-Type: application/json

{ "message": "How does BASS compare to FLEX?", "scenario": "Moon base" }
```

Example response:

```json
{
  "answer": "Evidence-backed answer...",
  "citations": [
    { "title": "NASA investigation source", "url": "https://psi.nasa.gov/" }
  ]
}
```

The frontend shows a network/schema error if this configured endpoint fails, rather than fabricating a model answer. Configure CORS appropriately for your app's origin and implement authentication, citation verification, and timeouts before production.

Suggested next development phases:
1. NASA PSI metadata ingestion + normalized study/run/source tables.
2. Raw data access, precise oxygen/pressure/airflow/sample metadata and run-level comparisons.
3. Evidence-grounded RAG with documents, test runs, confidence and explicit source citations.
4. Validated quantitative models and only then risk-related predictions.
5. Genuine NASA video inputs and versioned CV segmentation / tracking.

## Project layout

```text
app/                       Next.js App Router pages and global styles
  dashboard/               Mission overview
  explorer/                Searchable research library
  compare/                 Two-study comparison
  intelligence/            Scenario ranking demo
  visual-lab/              Conceptual scientific visualization
  copilot/                 Research assistant demo
components/                Reusable layout, art, UI, screen components
lib/research.ts            Curated typed investigations + scenario descriptors
lib/utils.ts               Frontend CSV export helpers
```

## Official starting resources

- [NASA Physical Science Informatics (PSI)](https://psi.nasa.gov/)
- [NASA Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/)
- [NASA PSI · SAME-R record](https://psi.nasa.gov/physci/repo/data/investigations/PSI-101)
- [NASA Scientific Visualization Studio](https://svs.gsfc.nasa.gov/31394/)

## UI identity

Editorial aerospace design, with **deep midnight / blue-black**, subtle scientific grids, warm flame highlights, and cool instrument accents. Rebuilt from the provided static frontend into structured **Next.js App Router + React + TypeScript**, while maintaining its six-screen concept. Based on the supplied **Apple Design** skill's focus on immediacy, spatial consistency, accessible typography, restrained translucent materials, and interruptible motion.

**No third-party imagery or Apple-branded assets are embedded.**
