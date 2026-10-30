# CIKM 2026 Industry Day: teaser slide and poster

Plan for generating a 1-slide 90-second teaser and an A0 poster for:

> Ante Kapetanovic, Tomislav Duricic, Andro Mercep, Emanuel Lacic. 2026. A Phased Workflow for Operating LLM-Based Coding Agents. CIKM '26, Rome. DOI 10.1145/3799682.3839253, arXiv 2608.30701.

The paper is the source of truth for workflow claims. Read it first: https://arxiv.org/abs/2608.30701 (2 pages). Repo `README.md` and `figures/workflow.png` on `main` show the workflow visually.

## Constraints

- Branch `cikm2026industry` (already created from `main`). It is never merged. Commit locally; the user pushes when everything is done.
- All files live in `poster/`. Figures, logos and any figure scripts live in `poster/figures/`.
- If a Python script is needed, run it with `uv` from `poster/figures/`. The default uv index is the Infobip Artifactory mirror and may return 401; if so, stop and ask the user to authenticate rather than switching indexes silently. Current plan needs no Python (TikZ + `qrcode` package).
- Toolchain: LuaLaTeX via TinyTeX (`~/Library/TinyTeX/bin/universal-darwin/`), `latexmk`.
- Fonts: Inter (text) and JetBrains Mono (skill names, file names). Not installed yet: `tlmgr install inter jetbrainsmono-otf`, then confirm with `luaotfload-tool --find="Inter"`. If unavailable, ask the user before substituting.
- Follow `AGENTS.md` writing style and the `unslop` skill for all visible text. Plain technical prose, no marketing language.
- No animation. No poster slot or board number anywhere.
- No Infobip scale numbers (engineers, messages, countries).

## Files

```text
poster/
├── PLAN.md
├── .gitignore          # LaTeX aux files only; final PDFs are committed
├── .latexmkrc          # $pdf_mode = 4 (lualatex)
├── style.sty           # shared colors, fonts, macros, QR macro
├── references.bib
├── poster.tex          # A0 portrait, plain article class, no poster template
├── teaser.tex          # beamer, 16:9, exactly one frame
├── poster.pdf
├── teaser.pdf
└── figures/
    ├── workflow.tex    # TikZ hero figure, \input by both poster and teaser
    ├── loop.tex        # TikZ case-study loop
    ├── cikm2026.png    # copy from ~/Code/llm-judge-bias/poster/assets/
    └── infobip.png     # copy from ~/Code/llm-judge-bias/poster/assets/
```

`workflow.tex` must scale cleanly to both A0 width and a 16:9 slide strip. Parameterize it (e.g., a `compact` switch that hides the skills/artifacts rows for the teaser).

## Visual identity

- Derived from `figures/workflow.png` (phase boxes, human vs. agent involvement curves), recolored into the CIKM 2026 and Infobip palettes.
- CIKM 2026 logo colors: Italian-flag green and red, light grey network nodes, Roman ochre and brick (Colosseum, auditorium). Infobip: orange.
- Sample exact hex values from the two logo PNGs. Provisional mapping, where phase color warms from green to orange as delegation increases:

| Role | Provisional | Source |
| --- | --- | --- |
| Research | `#1E6B35` green | CIKM |
| Planning | `#C9962E` ochre | CIKM Colosseum |
| Task Definition | `#B8322A` brick red | CIKM |
| Implementation | `#F26722` orange | Infobip |
| Human curve | ink `#1C1C1E`, solid | |
| Agent curve | Infobip orange, dashed | |
| Text / muted / rules | `#1C1C1E` / `#5F6670` / `#DADDE1` | |

- Check that the four phase colors stay distinguishable under deuteranopia and in grayscale (the `dataviz` skill has a validator). Adjust shades if not; keep the hue families.
- White page background, light tinted panels (print cost and contrast).
- Must look different from the user's other CIKM poster (`~/Code/llm-judge-bias/poster/poster.pdf`): no Arial, no big-number KPI row, no red numbered section headings, no chart grid. This poster is diagram-led.

## Teaser slide (90 s, one 16:9 frame)

Assume organizers play a single PDF from their laptop with no reliable clicker. One page, no overlays.

Layout, top to bottom:

1. Hook headline: "Velocity changed. Ownership didn't."
2. Subline: "You can't review every line an agent writes, so decide what you own."
3. Hero strip: `workflow.tex` in compact mode. Four colored phases with the human (solid) and agent (dashed) curves. Small annotation near the curves: "like autopilot: the pilot works hardest at takeoff and landing" (human effort high early, rising again at review).
4. Bottom bar: paper title, authors, Infobip and CIKM logos, one QR code to the repo, "Come to the poster".

Text must be readable from the back of a lecture hall: headline at least 40 pt equivalent at 16:9, nothing under 18 pt.

### Script (target 200-220 words, about 140 wpm)

Deliver alongside the slide. Polish wording with the user, but keep the beats and timing.

- 0-15 s, hook: "Coding agents changed how fast we write, test, and ship software. They did not change who owns the result. When engineers juggle several agent sessions and stop following the decisions, codebases get sloppy, bugs slip through, and sometimes a production database disappears."
- 15-35 s, compromise: "We can no longer review every line an agent writes, so we have to decide what we own. Autopilot didn't remove the pilot. It changed when the pilot works hardest: at takeoff and at landing."
- 35-70 s, workflow: "Our phased workflow does the same for coding agents. Four phases: research, planning, task definition, implementation. Human effort is highest in research and planning, where mistakes are most expensive. As the artifacts mature, delegation grows, and each task runs in a fresh agent session. Context is managed deliberately at every phase: write, select, compress, isolate."
- 70-90 s, call to action: "At the poster, I'll show how we applied the workflow to open-ended research, where 322 agent sessions improved a 30-year-old graphics baseline by almost 12 percent, and two open problems we'd like your help with, starting with how to measure whether a workflow works at all. Everything is open source. Come find me."

## Poster (A0 portrait, 841 x 1189 mm)

CIKM rules: A0 portrait, printed by the presenter (copy shops in Rome). Body text at least 28 pt, section heads around 48 pt, title around 90 pt. Readable from 2 m.

Bands, top to bottom (heights are rough shares):

### 1. Header (~11%)

Title, authors, emails, Infobip logo left, CIKM logo right. Below, the takeaway line, large:

> Front-load the thinking. Build the backpressure. Stay on the loop.

### 2. Why (~17%), two columns

Left, "Velocity changed. Ownership didn't.":
- Agents changed the speed of writing, testing, and shipping code. Humans can no longer review everything, so the compromise must be deliberate: own decisions, delegate execution.
- Focusing human attention on research and planning keeps track of what the agent does and keeps the codebase under control.
- Detachment and multitasking across agent sessions lead to sloppy code, bugs, and financial losses. Support with at most three citations, each verified before use (title, year, exact claim). Drop any that can't be verified:
  - DORA 2024 State of DevOps report: higher AI adoption associated with lower delivery stability.
  - Bainbridge 1983, "Ironies of Automation": operators who only monitor lose the ability to intervene.
  - Replit agent deleting SaaStr's production database (July 2025).
- One line on the autopilot analogy, matching the teaser.

Right, "How long contexts fail" (from the paper, Breunig [3]): 2 x 2 grid of the four failure modes with one-line definitions:
- distraction: over-reliance on accumulated patterns
- confusion: irrelevant content competing for attention
- poisoning: hallucinations persisting across turns
- clash: new information conflicting with existing context

Plus one supporting number from the paper: an average 39% performance drop in multi-turn settings (Laban et al. [9]).

### 3. Hero: the workflow (~28%)

`workflow.tex` full width: involvement curves on top, four phase boxes with execute/refine arrows between Task Definition and Implementation, skills row (`/research`, `/scholar`, `/handover`, `/brainstorm`, `/to-tasks`, manual supervision / autonomous loop), artifacts row (`RESEARCH.md`, `PLAN.md`, `TASKS.md`, `ACTIVITY.md`, `AGENTS.md`, git commits). Short caption: research and planning once per project; task definition and implementation loop; return to task definition instead of patching code.

### 4. Practices per phase (~18%)

Table, rows are phases, columns: what the human does, what the agent does, context strategies, failure modes countered, artifact. Derive cells from the paper text (section 2). The Shift talk used slightly different strategy labels per phase; the paper wins. Include these specific practices:

- Research: read-only tools plus literature search; practitioner withholds opinions to avoid anchoring; findings validated before moving on. Select + isolate, then write.
- Planning: default agent mode, not a dedicated plan mode (plan modes finalize prematurely); manual curation of decisions into a persistent artifact is the main compress step and prevents poisoning from abandoned reasoning.
- Task definition: each task has ID, goal, dependencies, code paths, acceptance criteria, validation; sized to fit one fresh session, well below nominal context capacity.
- Implementation: fresh session per task; task registry plus append-only activity log plus git make conversation state disposable; manual supervision or autonomous loop.
- Cross-cutting: project instructions are hand-crafted and get concise single-line corrections when the agent repeats a mistake (instruction-following degrades with instruction count [7]).

### 5. Bottom pair (~17%)

Left, narrower (about 40% width), clearly labeled "Beyond the paper: open-ended research":
- `loop.tex`: fresh agent session -> one bounded proposal -> protected external evaluation -> retain or restore -> next session.
- Setup in one line: PCA normal estimation (Hoppe et al. 1992) on PCPNet; agent may only edit the estimator, never the scorer ("it could not change the meaning of success").
- Three numbers, from the blog post (the source of truth): 322 fresh sessions · under 18 h · average angular RMSE 16.26° -> 14.36° (-11.7%, 95% CI of the difference [-2.23°, -1.59°]). No cost figure (not recorded).
- One line: no single session invented the final estimator; accepted and rejected attempts both became evidence for later sessions.
- Source: https://antekapetanovic.com/blog/phased-agent-normal-estimation. Re-check the numbers there before finalizing.

Right, "Open problems: let's talk":
1. No metrics for workflow effectiveness. Candidates: task success rate per session, instruction correction rate, context utilization at task completion.
2. Research formalizes components (pruning, compression, tool selection), not the workflow-level patterns practitioners compose; no shared terminology across teams.

### 6. Footer (~9%)

Single QR code to https://github.com/infobip/agentic-development-workflow (the repo README carries the DOI, arXiv link, and BibTeX). DOI as text. Acknowledgment: IPCEI-CIS, Infobip Global Communication Platform project (PK.1.1.07.0001). Compact numbered references for everything cited on the poster.

## References

From the paper (reuse BibTeX from arXiv): Breunig 2025 (context failures), Martin 2025 (write/select/compress/isolate), Laban et al. 2026 (multi-turn drop), Hong et al. 2025 (context rot), Jaroslawicz et al. 2025 (instruction count), Horthy 2025 (research-plan-implement, which the workflow extends; credit it, don't quote it), Becker et al. 2025 (unstructured AI use can slow developers).

New, verify before use: DORA 2024, Bainbridge 1983, Replit/SaaStr incident 2025. Case study: Hoppe et al. 1992, Guerrero et al. 2018 (PCPNet), the blog post.

## Build and verification

1. `cd poster && latexmk poster.tex teaser.tex`.
2. `pdfinfo poster.pdf` reports 1 page, about 2383.94 x 3370.39 pt (A0 portrait). `pdfinfo teaser.pdf` reports 1 page, 16:9.
3. `pdffonts` shows all fonts embedded; Inter and JetBrains Mono present.
4. Render previews (`pdftoppm -png -r 30`) and inspect them visually: no overflow, balanced whitespace, phase colors consistent between poster and slide.
5. QR decodes to the repo URL (`zbarimg` if installed; otherwise ask the user to scan).
6. Read the teaser script aloud at 140 wpm; it must fit in 90 s.
7. Run the `unslop` pass over all visible text.
8. Show both previews to the user before committing.
