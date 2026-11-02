# Handover: CIKM 2026 teaser slide and A0 poster

Continue the teaser and poster work in `poster/`. This file is the only brief. It records the constraints, what was built, every decision, and what is still open. The original plan was removed at the user's request; it is in git history (`git show d73eafb:poster/PLAN.md`) but is out of date, so do not work from it.

The paper is the source of truth for workflow claims: https://arxiv.org/abs/2608.30701 (2 pages). For the case study, the source of truth is the blog: https://antekapetanovic.com/blog/phased-agent-normal-estimation.

## Constraints (from the original plan, still in force)

- Branch `cikm2026industry`, created from `main` and never merged. Commit locally only when the user asks; the user pushes.
- All files live in `poster/`. Figures, logos and figure scripts live in `poster/figures/`.
- Toolchain: LuaLaTeX via TinyTeX (`~/Library/TinyTeX/bin/universal-darwin/`), `latexmk`. If Python is ever needed, run it with `uv` from `poster/figures/`.
- No animation. No poster slot or board number anywhere. No Infobip scale numbers (engineers, messages, countries).
- Teaser: organizers play one PDF from their laptop with no reliable clicker, so one page and no overlays. Headline at least 40 pt, nothing under 18 pt.
- Poster: CIKM rules, A0 portrait, printed by the presenter. Body text at least 28 pt, section heads about 48 pt, title about 90 pt. Readable from 2 m.
- Must look different from the user's other CIKM poster (`~/Code/llm-judge-bias/poster/poster.pdf`): no Arial, no big-number KPI row, no red numbered section headings, no chart grid. This poster is diagram-led.
- Verify every new citation (title, year, exact claim) before use; drop any that cannot be verified.

## Teaser script (90 s, target 200-220 words at about 140 wpm)

Spoken alongside the slide. Polish the wording with the user, but keep the beats and timing. Currently 202 words, about 87 s. The 0-15 s hook still echoes the old headline ("They did not change who owns the result"); see open items.

- 0-15 s, hook: "Coding agents changed how fast we write, test, and ship software. They did not change who owns the result. When engineers juggle several agent sessions and stop following the decisions, codebases get sloppy, bugs slip through, and sometimes a production database disappears."
- 15-35 s, compromise: "We can no longer review every line an agent writes, so we have to decide what we own. Autopilot didn't remove the pilot. It changed when the pilot works hardest: at takeoff and at landing."
- 35-70 s, workflow: "Our phased workflow does the same for coding agents. Four phases: research, planning, task definition, implementation. Human effort is highest in research and planning, where mistakes are most expensive. As the artifacts mature, delegation grows, and each task runs in a fresh agent session. At every phase we manage context on purpose. We write it to files, select what to load, compress discussions, and isolate sessions."
- 70-90 s, call to action: "At the poster, I'll show how we applied the workflow to open-ended research, where 322 agent sessions improved a graphics baseline from 1992 by almost 12 percent. I'll also show two open problems we'd like your help with, starting with how to measure whether a workflow works at all. Everything is open source. Join us during the poster session."

The script is spoken, so the colons in it are fine; the no-colon rule applies to the PDFs.

## Status

- Branch `cikm2026industry`. All poster files are untracked; nothing is committed yet. The user wants to see previews before committing and pushes themselves.
- `poster.pdf` (1 page, A0 portrait, 2383.94 x 3370.39 pt) and `teaser.pdf` (1 page, 16:9) both build cleanly: no errors, no overfull boxes.
- Fonts embedded: Inter (Regular, Bold, Italic) and JetBrains Mono Regular. Nothing else.
- Two sessions so far. Session 1 built everything. Session 2 did an unslop pass, then a redesign so a reader understands the poster without the presenter. It also fixed the teaser and freed vertical space. See "Session 2 changes".
- The poster page is full. The tightest constraint is the gap under the header strip: 24 pt fits, 30 pt pushes the footer to page 2.
- The user reviews rendered previews after each round and replies with screenshots of the details to fix. After every change, render and look at crops before reporting.

## Files

```text
poster/
├── HANDOVER.md        this file
├── .gitignore         LaTeX aux files only; PDFs are committed
├── .latexmkrc         $pdf_mode = 4 (lualatex)
├── style.sty          fonts, colors, chip styles, \repoqr, \papertitle, \authorlist
├── references.bib     12 entries, trimmed for the poster (no URLs or DOIs)
├── poster.tex         A0 portrait, plain article class
├── teaser.tex         beamer, 960 x 540 pt page, one frame
├── poster.pdf, teaser.pdf
└── figures/
    ├── workflow.tex   shared hero figure; \ifwfcompact switches teaser vs poster
    ├── loop.tex       case-study loop (poster only)
    ├── infobip.png    stacked logo supplied by the user (replaced the horizontal one)
    ├── cikm2026.png   from ~/Code/llm-judge-bias/poster/assets/
    ├── github.png     Octocat mark supplied by the user
    └── doi.png        DOI mark supplied by the user
```

## Build and check

```bash
cd poster
export PATH=~/Library/TinyTeX/bin/universal-darwin:$PATH
latexmk -interaction=nonstopmode -halt-on-error poster.tex teaser.tex
grep -nE "^!|Overfull|undefined" poster.log teaser.log   # expect nothing
pdfinfo poster.pdf | grep -E "Pages|Page size"            # 1 page, A0
pdfinfo teaser.pdf | grep -E "Pages|Page size"            # 1 page, 956.41 x 537.98 bp
pdffonts poster.pdf; pdffonts teaser.pdf                  # Inter + JetBrains Mono only
pdftoppm -png -r 30 poster.pdf /tmp/poster_preview        # look at it
pdftoppm -png -r 72 teaser.pdf /tmp/teaser_preview
```

Use crops (`pdftoppm -r 60 -x .. -y .. -W .. -H ..`) to check details; the 30 dpi full view hides collisions.

Environment notes:
- `tlmgr install` was run for `inter`, `jetbrainsmono-otf`, `enumitem`, `colortbl` (`colortbl` is no longer used).
- `uv` against the Infobip Artifactory index returns 401. No Python is needed for the build. If Python is needed, ask the user to authenticate; do not switch indexes.
- `zbarimg` and ImageMagick are not installed. QR decoding was never verified by tool; ask the user to scan it.
- The user denied one command that rewrote `poster.tex` through an inline Python script and deleted files in `/tmp`. Edit files with the Edit tool, and avoid `rm` in compound commands. In session 2, `HANDOVER.md` was rewritten once with an inline `python3 -I` script; the user has not objected, but prefer the Edit tool.
- Careful with `sed` on `poster.tex`: a regex over `^\vspace{..pt}$` matches five lines (header strip gap, header gap, hero top 28 pt, under figure 8 pt, footer 26 pt). Address lines explicitly.
- Logo measurement helper from session 2 lived in `/tmp/logo_scripts/rows.py` (dark-row runs in a PGM from `pdftoppm -gray`). `/tmp` may be cleared; rewrite it if needed.

## Visual identity (decided)

Phase palette in `style.sty`. Sampled logo colors: Infobip orange `#FC6322`, Infobip ink `#0B1A2B`, CIKM green `#0F5004`, red `#CC0902`, Colosseum ochre `#FED079`, brick `#A55C24`/`#963C12`.

| Role | Hex | Note |
| --- | --- | --- |
| Research | `#1F6B30` | CIKM green family, L* 40 |
| Planning | `#E6B84A` | Colosseum ochre family, L* 77 |
| Task Definition | `#6E1F16` | brick family, L* 25 |
| Implementation | `#FC6322` | Infobip orange, L* 61 |
| Human curve | `ink` `#1C1C1E`, solid | |
| Agent curve | Infobip orange, dashed | |
| ink / muted / rule / panel | `#1C1C1E` / `#5F6670` / `#DADDE1` / `#F4F5F7` | |

- The original plan's provisional palette failed the `dataviz` validator: orange vs ochre had ΔE 1.4 under deuteranopia. The final shades pass all-pairs CVD (worst ΔE 9.5 deutan) and differ by at least 15 L* in grayscale. They intentionally sit outside the validator's chart-mark lightness band. These are labeled boxes, not unlabeled series.
- Chip styles, defined in `style.sty` and used in the figure and the poster text:
  - `chip`: white, mono. Used for skills.
  - `artifact`: grey fill, mono.
  - `mode`: orange tint. Used for manual supervision and autonomous loop.
  - `failure`: outlined, italic. Used for failure modes and for the open-problem candidate metrics.
  - `strategy`: filled ink, bold white. Used for write, select, compress, isolate.- A four-color phase strip appears under the poster header and along the top edge of the teaser. Nowhere else; the user removed the strips from the takeaway cards.
- Orange means agent, ink means human. The two-line headline uses this split on the teaser and on the poster's left "why" heading.
- Writing: `AGENTS.md` style plus the `unslop` skill. No em dashes. No colons in visible text (session 2 removed the last ones). Sentence case. No marketing language; the user rejected "Velocity changed. Ownership didn't." for sounding like marketing.

## Poster content (current, top to bottom)

Sizes: title 88 pt, section heads 48 pt, body 30 pt in the "why" band, 28 pt elsewhere (the plan's minimum). Exception: references and acknowledgment are 18 pt so the poster fits.

1. **Header.** Stacked Infobip logo left, title center, authors and emails below it, CIKM logo right. Phase strip underneath (`\phasebar`), then a 24 pt gap before the why band.
2. **Why band, two equal columns (0.48 width each).** Both headings take two lines. The right column, with the legend, sets the band height.
   - "Agents write code faster / than humans can review it". The first line is orange, the second ink, matching the teaser headline. Three bullets: DORA 2024 (a 25% rise in AI adoption, an estimated 7.2% drop in delivery stability) plus the Replit database deletion; "Watching is not enough" plus Bainbridge 1983; autopilot, with "Our workflow puts human effort in the same places."
   - "Long, noisy context / makes agents worse". Laban 39%, Hong. Then a two-column chip legend headed "Failure modes [Breunig]" and "Strategies against them [Martin]". Failure modes: distraction "old patterns dominate", confusion "irrelevant content", poisoning "hallucinations persist", clash "new facts conflict". Strategies: write "save to files", select "load what's needed", compress "keep what's required", isolate "fresh sessions".
3. **Takeaway cards.** Three tinted panels, 0.32 width each, height `\takeawayh` (210 pt). Each has the statement at 48 pt and one explanatory line. The user removed the phase-colored bars to free vertical space. This replaced the single 60 pt takeaway line so the jargon is explained.
   - "Front-load the thinking." Humans own research and planning, where mistakes cost the most.
   - "Build the backpressure." Acceptance criteria and validation reject bad output before you review it.
   - "Stay on the loop." One task per fresh session. You review, and bad tasks go back.
   - `\takeaway{statement}{explanation}`, built on `\panel`.
4. **Hero, "Four phases, with human effort front-loaded".** `figures/workflow.tex`, full mode.
   - **Left label column** (`\wfleft=9` units): "Involvement" with a human (solid) and agent (dashed) key, plus row labels.
   - **Involvement panel.** Each curve holds one flat level per phase and steps smoothly between phases. Levels go from 1 (low) to 4 (high). Agent: 1, 1, 3.2, 4, ending at 4. Human: 4, 4, 1.8, 1, rising to 2.3 at the end (review).
   - **Role text** sits directly on top of its own line.
     - Research. Human: "guides, withholds opinions, validates findings". Agent: "explores with read-only and search tools".
     - Planning. Human: "decides, curates by hand". Agent: "proposes options outside plan mode".
     - Task Definition. Human: "checks each task fits one session [Hong]". Agent: "writes acceptance criteria and validation".
     - Implementation. Human: "supervises, reviews output" (narrower width so it wraps before the review rise). Agent: "implements, validates, logs, commits".
   - **Phase boxes** with one-line subtitles: "Validate the problem context", "Choose the approach", "Write one-session tasks", "One fresh session per task". Execute and refine arrows run between Task Definition and Implementation.
   - **Rows below the boxes**, labeled so they read as a sentence: Prevents, Using, Repo skills, Writes. Values are derived from the paper.
     - Prevents. Research: confusion, distraction. Planning: poisoning. Task Definition: distraction. Implementation: poisoning, distraction.
     - Using. Research: select, isolate, write. Planning: compress, write. Task Definition: write, isolate. Implementation: isolate, select, write.
     - Repo skills. Research: /research, /scholar, /handover. Planning: /brainstorm, /handover. Task Definition: /to-tasks. Implementation: manual supervision, autonomous loop.
     - Writes. Research: RESEARCH.md. Planning: PLAN.md. Task Definition: TASKS.md. Implementation: AGENTS.md, ACTIVITY.md, git commits.
   - **Caption (muted, one line).** Research and planning run once per project. Each repeated agent mistake earns one short line in `AGENTS.md` [Jaroslawicz]. Extends research-plan-implement [Horthy].
   - The curve labels "delegation increases" and "review" appear only on the teaser.
5. **Bottom pair: two tinted panels, equal width (0.485) and equal height (`\bottomh`, 712 pt).**
   - **"Open-ended research, beyond the paper".**
     - Setup: an autonomous implementation loop improved PCA normal estimation (Hoppe 1992) on PCPNet (Guerrero 2018). The agent could edit the estimator but never the scorer.
     - Loop figure: boxes in Implementation colors to tie the loop to that phase; "Protected evaluation" stays white with an ink outline; ink arrows. Boxes are 56 pt tall with rows 140 pt apart, so the vertical arrows have visible shafts; the user found them too short at 118 pt. The "<18 h" stat sits at −128 pt to line up with the lower row.
     - Stats next to the loop: 322 fresh sessions, <18 h wall clock. Below, a large orange −11.7% with "angular RMSE from 16.26° to 14.36°, 95% CI of the difference [−2.23°, −1.59°]".
     - Closing line: no single session found the final estimator. With no control run, the gain is not yet the workflow's (open problem 1). The blog states the missing control run.
   - **"Let's talk about open problems".**
     - Item 1: no metrics for workflow effectiveness, with the candidate metrics stacked as failure-style chips under "Candidate metrics, none tested yet".
     - Item 2: "Research stops at components."
     - Call to action: "Have a metric or a counterexample? Open an issue in the repo."
6. **Footer.**
   - Left: QR code to the repo, next to two aligned rows: GitHub icon + `infobip/agentic-development-workflow`, DOI icon + `10.1145/3799682.3839253`. The acknowledgment (IPCEI-CIS, PK.1.1.07.0001) sits below them.
   - Right: references in 4 columns, `ieeetr` style, numbered in order of citation.
   - `\interlinepenalty=10000` keeps each entry inside one column.
   - The `\qmark` macro (defined in `poster.tex` and used in two bib titles) removes the comma `ieeetr` adds after titles ending in "?".
   - Venue fields were shortened so no entry ends with a word alone on its last line. If you add or edit references, re-check this with a 72 dpi crop of the footer.
   - Vertical space is used up. Any added line overflows a panel or pushes the footer to page 2; check `pdfinfo poster.pdf | grep Pages`.

## Teaser content (current)

- **Page size:** 960 x 540 pt (the PowerPoint 16:9 size), so point sizes are literal. Headline 42 pt, subline 26 pt, phase titles 20 pt, smallest text 18 pt.
- **Phase strip** along the top edge.
- **Headline in two lines:** "Agents write code faster" in Infobip orange (agent), "than humans can review it." in ink (human). Chosen by the user to replace "Velocity changed. Ownership didn't.", which read as marketing.
- **Subline:** "You can't review every line an agent writes, but you have to own it." Wording based on the user's note.
- **Hero:** `workflow.tex` in compact mode. The curves and phase boxes match the poster, with Human/Agent labels on the lines. "delegation increases" sits just before the agent line rises; "review" sits at the end. Above the panel is an italic annotation: "With autopilot, the pilot still works hardest at takeoff and landing." The user asked for the capital W and the period.
- **Teaser figure knobs** (`teaser.tex`): `\wfcurveh` 13.5, `\wfboxh` 5.5, `\wfgap` 4 (so "execute" and "refine" clear the curve panel, per the user), `\wftitlefont` 20 pt (the user asked for smaller phase titles). The figure sits 22 pt below the subline.
- **Bottom bar** (112 pt, light grey):
  - QR code (80 pt).
  - Paper title and authors.
  - An orange pill reading "Join us during the poster session".
  - Stacked Infobip logo at 58 pt, shifted down 10.8 pt so its wordmark shares the CIKM wordmark's baseline, then the CIKM logo at 72 pt. Both wordmarks measure about 14.3 pt tall.

## Sources and verification (done)

- **Paper source:** arXiv 2608.30701 LaTeX source (`main.tex`, `references.bib`). Fetch it again with `curl -sL https://arxiv.org/e-print/2608.30701` into an empty `/tmp` directory if needed. The paper's Laban entry has a stray closing brace; `poster/references.bib` already fixes it.
- **Blog** (https://antekapetanovic.com/blog/phased-agent-normal-estimation), checked:
  - 322 fresh sessions, "just under 18 hours".
  - Same-harness PCA 16.26°, final 14.36°, −11.7%.
  - Paired bootstrap difference −1.90°, 95% CI [−2.23°, −1.59°].
  - "No single prompt invented the final method."
  - Token counts and cost were not recorded.
- **Blog phase mapping** (fetched in session 2, used for the case-study panel): research covered the PCPNet protocol, prior methods and leakage risks; planning set the evaluation tiers and acceptance thresholds; task definition fixed one geometric hypothesis and one removable change per iteration; implementation was the autonomous loop. Of 304 measured candidates, 24 reached validation and 11 replaced the frontier. The final estimator is about 5.1 times slower than PCA, and PFF-Net is still 4.98° better. The blog states there was no randomized run without the workflow.
- **New citations, checked:**
  - DORA 2024 Accelerate State of DevOps Report: a 25% rise in AI adoption came with an estimated 7.2% drop in delivery stability and 1.5% in throughput. Checked only against blogs that quote the report (tsukumo.ch, xsquads.ai), not the report PDF.
  - Bainbridge 1983, Automatica 19(6):775–779.
  - Sharwood, The Register, 21 July 2025 (Replit/SaaStr).
  - Hoppe et al. SIGGRAPH '92, pp. 71–78.
  - Guerrero et al. CGF 37(2):75–85, 2018.
- **Dropped:** Becker et al. 2025 (METR), to keep at most three citations in the left "why" column.
- **No Infobip scale numbers** anywhere, per the plan.

## Session 2 changes (done)

In order:

1. **Session 1 open items closed.** The user confirmed the QR codes and logos. The teaser script now says "a graphics baseline from 1992" and ends with "Join us during the poster session" (202 words, about 87 s at 140 wpm). The unslop pass removed all colons from visible text.
2. **Accuracy fixes against the paper.** Each phase picks the strategies that counter its own failure modes, not all four. "Proposes options outside plan mode". "Checks each task fits one session" replaced "sizes tasks below context limits".
3. **Rating round.** The user asked for 1-5 ratings across rubrics, then asked to fix whatever raises them. The brief was to keep the gist and make the poster more attractive, more understandable, and almost standalone: a reader should get the main point and takeaways without the presenter.
4. **Redesign.** The why headings now state the problem. Explained takeaway cards replaced the slogan line. The figure rows got sentence-style labels. The case study is tied to Implementation and to open problem 1, and there's a closing call to action. Body text is down by about a third.
5. **Teaser fixes the user asked for.**
   - New headline (the user picked it from three options).
   - Smaller Infobip logo, with its wordmark matched to "CIKM 2026".
   - More space around "execute" and "refine".
   - Smaller phase titles.
   - "With autopilot, ... landing."
6. **Last round.** The user removed the color bars from the takeaway cards to free space for the gap under the header strip, and asked for longer vertical arrows in the loop. Both are done. Most of the freed space went into the loop, so the header gap is 24 pt (about 8 mm).

Latest ratings (1-5): visual design 4.5, fidelity 4.5, standalone 4, text density 3.5, cohesiveness 4.5, hero figure clarity 4, flow 4.5, teaser 4.5. What still holds the scores back:
- The curve panel has a lot of empty tinted space in the middle.
- The Prevents and Using rows don't explain why a phase gets its chips.
- DORA is checked against secondary sources only.

## Open items

1. **Commit:** wait until the user asks. Commit `poster/` with `HANDOVER.md` and the PDFs, and the deletion of `PLAN.md` (already deleted from the working tree but not staged; `git add -A poster/` picks it up); LaTeX aux files are ignored. End the message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
2. **Teaser script hook** (section "Teaser script" above) still says "They did not change who owns the result", which echoes the old headline. Offered to rewrite the 0-15 s beat around "Agents write code faster than humans can review it"; the user has not answered.
3. **Call to action** "Open an issue in the repo" assumes the repo accepts issues. Asked the user to confirm; no answer yet. Drop the line if issues are off.
4. **More room under the header strip, if the user asks:** merge the "Autopilot..." bullet into the one before it, which frees about 40 pt. The user asked for that sentence to stand alone earlier, so suggest it rather than doing it.
## Layout knobs (where to change things)

- **Figure geometry, `poster.tex` preamble:**
  - `\wfleft` sets the label column.
  - `\wfboxw` sets the phase width.
  - `\wfcurveh`, `\wfboxh`, `\wfgap`, `\wfrowh`, `\wfstackh` set the vertical sizes.
  - The teaser has its own set in `teaser.tex`.
- **Curve levels and role text:**
  - `\wfcurve{agentline}{...}`, `\wfcurve{humanline}{...}` and the `\wfon{phase}{level}{text}` calls in `figures/workflow.tex`.
  - If two-line labels collide with a curve, spread the levels or pass a narrower width (`\wfon[\wfboxw-7]...`).
- **Panel heights:** `\takeawayh` (210 pt) and `\bottomh` (712 pt). To get a panel's natural height, temporarily replace the `\vbox to` in `\panel` with a box that runs `\typeout` on `\ht + \dp`. If a panel overflows, LaTeX reports an "Overfull \vbox".
- **Legend column widths:** the first argument of `\legend` (chip slot width) and the two inner minipage widths.
- **Pitfalls:**
  - TikZ `step` is a reserved key.
  - Write `text width=(#1)*\wfunit` with parentheses.
  - `Stealth[length=...]` needs a precomputed `\the\dimexpr`.
  - The figure's bounding box is forced to 100 units wide so line widths never cause overfull boxes.
