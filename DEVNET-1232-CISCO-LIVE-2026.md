# DevNet-1232 — Swagger into RESTCONF: Navigating the IOS XE API (& DevNet Sandboxes)

**Cisco Live US 2026 · 45-minute breakout · lecture + demos**
**Speaker:** Jeremy Cohoe
**Repo backing the demos:** https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/

> **Tone:** honest engineer war-story. Half "here is a useful site, go use it." Half
> "here is what it actually cost me to build it with an AI agent, what worked, what
> didn't." No keynote polish, no AI hype.

---

## Verified repo facts (as of 2026-05-29)

Use these for any slide or claim. Round at will but don't invent.

| Metric | Value |
|---|---|
| First commit | 2026-02-01 (Sun, 10:06 PT / 19:06 Amsterdam) — 8 days before Cisco Live EMEA |
| Latest commit | 2026-05-25 |
| Calendar span | ~17 weeks |
| Git commits | 379 |
| Shipped polish/feature rounds | 25 |
| Passing tests | 187 |
| Source files (py/js/html/md, ex-archive/releases/yang-trees) | 243 |
| Source LOC (py/js/html/md, ex-archive/releases/yang-trees) | ~63,800 |
| └ Python (generators + tools + tests) | 141 files / 37,799 lines |
| └ JavaScript (site UI) | 24 files / 8,473 lines |
| └ HTML (pages) | 29 files / 7,607 lines |
| └ Markdown (docs) | 49 files / 9,925 lines |
| OpenAPI 2.0 specs (9 viewer categories) | 668 |
| Largest viewer (oper) | 206 specs |
| Largest exported Postman collection | 10,083 requests (IOS-XE 26.1.1 cfg) |
| Release trains tracked | 5 — 17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1 |
| Site URL | https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/ |

**Headline tile for slide 14:** `668 specs · 5 releases · 25 rounds · ~17 weeks · 187 tests · 379 commits`

---

## Project timeline & commit cadence

All timestamps are Pacific Time (commit timezone). Cisco Live EMEA 2026 in Amsterdam ran **Feb 9–13, 2026** (Mon–Fri).

| ISO Week | Date range (PT) | Commits | Notes |
|---|---|---:|---|
| W05 | Jan 26 – Feb 01 | **120** | **Project kickoff Sunday Feb 1, 10:06 AM PT (= 19:06 Amsterdam).** ~80-min initial scaffolding burst followed by all-day Sunday → Monday → Tuesday push. |
| W06 | Feb 02 – Feb 08 | **94**  | Final pre-Amsterdam polish week. |
| W07 | Feb 09 – Feb 15 | 19  | **Cisco Live Amsterdam week — on-site, light commits as expected.** |
| W09 | Feb 23 – Mar 01 | 4   | Post-event lull. |
| W13 | Mar 23 – Mar 29 | 11  | |
| W14 | Mar 30 – Apr 05 | 6   | |
| W17 | Apr 20 – Apr 26 | **63**  | "Rounds 1–10" sweep — PWA, dark mode, accountability, code generator. |
| W19 | May 04 – May 10 | 3   | |
| W20 | May 11 – May 17 | 9   | |
| W21 | May 18 – May 24 | **50**  | "Rounds 18–25" + iOS mobile + search-UX fixes. |

**Two crunch sprints stand out:**
1. **Pre-Cisco-Live Amsterdam (W05 + W06): 214 commits in 14 days.** Built the demo-ready surface area starting from zero exactly 8 days before the show — initial commit was the Sunday-evening-Amsterdam-time before travel week.
2. **Late-April polish (W17: 63 commits).** Followed by a steadier rhythm and a second mini-sprint in W21.

**Activity gaps (W08, W10–W12, W15–W16, W18) are genuine zero-commit weeks** — useful for the "this was nights & weekends around a day job" honest-engineer framing.

---

## Numbers still to fill in before the talk

Mark each one once you have it. They light up slides 14, 18, abstract, Q&A #7.

- [x] **Engineer hours at the keyboard** (commit-timestamp derived): **~90–120 hrs across 27 active days (16 calendar weeks of nights + weekends)** — 60-min idle-gap model ≈ 91 hrs, 120-min ≈ 121 hrs
- [ ] **Tokens consumed** (M input / M output): `__________`
- [ ] **US$ spent on AI tokens**: `__________`
- [ ] **Hand-built equivalent estimate** (person-weeks if delegated to a junior + your reviews): `__________`

---

## Session abstract (for Cisco Live materials, if not already submitted)

> IOS XE exposes hundreds of YANG models across NETCONF, RESTCONF, gNMI, and a
> streaming telemetry surface — but reading the YANG tree, finding the right URI,
> and calling it against a real device is still a multi-tool scavenger hunt for
> most engineers. In this 45-minute session we'll walk a single workflow
> end-to-end against the always-on Catalyst 9000 DevNet Sandboxes (hardware C9K
> and virtual C9Kv): find the model in the browser, expand the path, fire the
> call from Swagger's "Try it out", and walk the same call out to curl, Postman,
> Bruno, and Ansible — without leaving the browser tab. We'll also pull back the
> curtain on how this site itself was built: a single engineer + a coding agent,
> ~16 weeks of nights and weekends, 668 OpenAPI specs auto-generated from pyang
> trees, real numbers on tokens, dollars, and where the AI helped vs. where it
> got stuck. You'll leave with a bookmarked tab, a Postman collection, and an
> honest baseline for what AI-assisted engineering actually costs to deliver
> production software.

---

## 45-minute outline (lecture + 3 demos)

### 0:00 – 0:04 · Cold open — "the scavenger hunt" (4 min)

**Slide 1 — Title**
- "Swagger into RESTCONF — Navigating the IOS XE API (& DevNet Sandboxes)"
- DevNet-1232 · Cisco Live US 2026 · *Jeremy Cohoe*

*Speaker note:* don't open with biography. Open with a problem.

**Slide 2 — The room test**
- "Hands up: who has tried to find the right RESTCONF URI for `interface GigabitEthernet1` description in the last 6 months?"
- Pause. *"Now keep your hand up if it took less than 10 minutes."*
- Most hands drop. That's the talk.

**Slide 3 — Why this is hard**
- IOS-XE 26.1.1 ships **668 OpenAPI specs** across **9 categories** (native cfg, native oper, IETF, OpenConfig, MIB, RPCs, events, …).
- Add NETCONF YANG trees, gNMI paths, MIB OIDs, telemetry sensor paths — same model, four shapes.
- Multiply by **5 release trains** you might be touching this year.
- Result: tab explosion, stale Postman collections, "is this still the right path?" Slack threads.

**Slide 4 — Today's promise**
> By the end of this 45 min you will have:
> 1. A public site that indexes all of it.
> 2. A workflow for going Spec → Try-it-out → curl → Postman in under 60 seconds.
> 3. An honest look at how the site got built so you can decide whether to copy the pattern.

---

### 0:04 – 0:09 · Tour the site (5 min, light demo)

**Slide 5 — The hub**
Screenshot of the index page with the 9 category tiles called out.

**Demo 1 — 90-second site tour (live)**

1. Land on hub → point out 9 viewer categories + global search box.
2. Type `interface` in the global search → fuzzy matches across all 668 specs.
3. Click into `swagger-native-config-model` → show release switcher (17.9 / 17.12 / 17.15 / 17.18 / 26.1).
4. Highlight: YANG Accountability, Tree Compare, Telemetry, Code Generator, Exports, Recent/Favorites.
5. Mention PWA: works offline on the plane after first visit.

*Speaker note:* do NOT navigate deeply yet. Goal is "you know it exists, you know what's on it." Save the deep dive for demo 2.

---

### 0:09 – 0:24 · The main demo — Swagger → RESTCONF on a Sandbox (15 min)

**Slide 6 — Today's lab**
- Target A: **Catalyst 9000V (virtual)** — Always-on DevNet Sandbox.
- Target B: **Catalyst 9300 (hardware)** — Reservable DevNet Sandbox.
- Goal: change an interface description three different ways from the same Swagger page.

**Slide 7 — The workflow**

```
YANG model  ─►  OpenAPI spec  ─►  Try-it-out  ─►  curl / Postman / Bruno / Ansible
   (truth)        (the index)     (the proof)         (your tooling)
```

**Demo 2 — Cat 9000V always-on sandbox (8 min, live)**

1. Open `swagger-native-config-model/26.1.1/Cisco-IOS-XE-native.json` viewer.
2. Filter the path list to `description` → expand `PUT /Cisco-IOS-XE-native:native/interface/GigabitEthernet={name}/description`.
3. In Swagger's "Authorize", paste sandbox base URL + basic-auth header. *(Have the exact URL + creds on the slide — sandbox creds are public.)*
4. "Try it out" → fill `name=1`, body `{"Cisco-IOS-XE-native:description":"DevNet-1232 demo"}`.
5. Execute. **Show the 204 + the curl panel Swagger generates.**
6. Open a terminal split: paste the curl, run it, GET it back, show the description.
7. Hop to **Code Generator** page → same payload → emit Python `requests` + Ansible playbook snippet.
8. Hop to **Exports** page → download the IOS-XE 26.1.1 Postman collection (10,083 requests pre-built) → import → run the same PUT.

*Speaker note:* when the audience sees curl, Postman, and Ansible all calling the same URI from the same source of truth, that's the "oh" moment. Let it land.

**Demo 3 — Cat 9300 hardware sandbox (5 min, live)**

1. Same viewer, same URI — show that the OpenAPI is **release-pinned**, so switching to 17.12.x changes the schema visibly (fields that don't exist yet in 17.9, are deprecated in 26.1).
2. Run the same curl against the C9300 reservable sandbox.
3. Show **Tree Compare**: pick `Cisco-IOS-XE-native` between 17.15 and 26.1.1, point at the diff.

*Speaker note:* the "same call, different release, see the schema move" beat sells the "this is a reference, not a snapshot" message. ~2 min on it.

**Slide 8 — What you just saw, in one diagram**

Lane diagram: pyang YANG tree → Python generator → OpenAPI 2.0 JSON → Swagger UI → Try-it-out → curl → Sandbox.

---

### 0:24 – 0:36 · The build story — honest, with numbers (12 min)

> **Tone here:** swap from "presenter" to "engineer at the bar." This is the
> section that makes the talk memorable. Don't oversell the agent. Show the
> scars.

**Slide 9 — Who built this**
- One engineer (me), nights + weekends, ~16 weeks.
- A coding agent (GitHub Copilot in agent mode, Claude-class model under the hood).
- No outsourced design, no contractors, no Cisco BU funding.

**Slide 10 — Why I didn't just write it by hand**
- 668 OpenAPI specs to generate, each with paths/schemas/examples → would have been a month of typing before any UI shipped.
- 9 viewer categories × 5 release trains = 45 viewer pages I would never have built solo.
- I wanted to ship, not type.

**Slide 11 — The pattern that worked: "rounds"**
- 25 rounds shipped, each one: tiny scope (1–3 bullet points), tests added/extended, service-worker bumped, CHANGELOG entry, push to dev + push to prod. Same shape every time.
- The agent enforced the discipline. I would have skipped tests under deadline pressure. It didn't.
- *"The agent is more boring than I am, and boring is a feature."*

**Slide 12 — What the agent was actually good at**
- Mechanical regeneration: write the pyang-tree → spec generator once, then run it against five release trains.
- Cross-file refactors that touch 17 HTML files identically (e.g. CSP hardening last week — finished in one shot).
- Writing the regression tests *I would not have written* (44 new security guards in one round).
- Keeping a changelog. Honestly, this alone was worth it.

**Slide 13 — What the agent was bad at**
- **Aesthetic taste.** First-pass UI was generic Bootstrap-soup. Took explicit "no emoji, no cards, monochrome, table-first" guidance before output stopped looking like AI slop.
- **Big architectural calls.** The decision to ship as a static PWA on GitHub Pages (no backend, no auth) was mine. The agent would happily have spun up a Flask service nobody needed.
- **Knowing when to stop.** I had to actively say "no more rounds — call it done" twice this month.
- **Drifting context.** Long sessions hit a compaction wall around hour 4; saving "rules of the repo" into `AGENTS.md` and a `/memories/` folder paid for itself many times over.

**Slide 14 — The numbers**

```
Calendar time      : ~16 weeks (Feb 1 → May 23 2026)
Active days        : 27 (mostly Fri-Sun evenings)
Engineer hours     : ~90-120 hrs (commit-timestamp derived)
                     = 2-3 full-time 40-hr weeks of focused work
Tokens consumed    : <<TODO: M input / M output>>
Token cost (US$)   : $<<TODO>>
Repo output        : 668 OpenAPI specs · 374 commits · 25 rounds
                    · 187 passing tests · ~63,800 LOC · 5 releases
Hand-built estimate: <<TODO: e.g. "12-18 person-weeks" delegated
                    to a junior with my reviews>>
Net speedup        : <<TODO: e.g. "~5x wall-clock at roughly
                    1/10th the fully-loaded cost.">>
```

**When the work happened** (from 374 commit timestamps):

```
Day-of-week distribution         Hour-of-day peaks (local)
  Sun  ##########################  127     10-12  late morning  (78 commits)
  Fri  #############################  85    16-22  evening block (187 commits)
  Sat  ##################  55              <1% between midnight and 7am
  Mon  ##############  44
  Tue  ###########  34
  Wed  ########  26
  Thu  #  3

71% of commits land Fri-Sun. Half the project (~200 commits)
shipped in the first week of February; everything after is
polish, hardening, and additional release trains.
```

*Speaker note:* the audience will photograph this slide. Make sure the numbers are right and you can defend each one.

**Slide 15 — The decisions, in plain English**
- **Static site, no backend.** Cheaper to run ($0/mo), impossible to breach in interesting ways, works offline.
- **OpenAPI 2.0 not 3.0.** Swagger UI + Postman/Bruno round-trip is friction-free on 2.0; 3.0 features weren't worth losing the import path.
- **Auto-generate, never hand-edit specs.** Re-run the generator every release. If you ever touch a generated file by hand you've already lost.
- **Pin every CDN dependency with SRI.** Already paid off — security review last week flagged it as the one thing that didn't need fixing.
- **No analytics, no tracking.** It's a reference. It loads fast. Don't ruin that.

---

### 0:36 – 0:42 · Outcomes & what changed (6 min)

**Slide 16 — Before / after, for the team**
- Before: "What's the URI for X?" Slack thread, 3 people, 30 minutes.
- After: bookmark, search, copy curl. Average answer time anecdotally **< 1 minute**.

**Slide 17 — What it unlocks**
- New engineer onboarding: hand them the URL, not a wiki.
- TAC + Field: link to a specific operation in a specific release; the URL is the bug report.
- Customer demos: live Swagger → live sandbox in one tab.
- Release diffing: "what API changed in 26.1.1?" is now a hyperlink, not a 2-day question.

**Slide 18 — What it cost the org**
- Zero hosting fees (GitHub Pages).
- One engineer's nights & weekends.
- $<<TODO>> in AI tokens.

*Speaker note:* the dollar number lands harder than any other slide. Let it sit for a beat before moving on.

---

### 0:42 – 0:45 · CTAs + Q&A (3 min)

**Slide 19 — Go do this today**
- 🔗 `ciscodevnet.github.io/cisco-ios-xe-openapi-swagger` ← bookmark it now
- 🔗 DevNet Sandbox: Always-On Cat 9000V (no reservation required)
- 🔗 DevNet Sandbox: Reservable Cat 9300 hardware
- File an issue / star the repo on `CiscoDevNet/cisco-ios-xe-openapi-swagger`

**Slide 20 — Takeaways**
1. Stop hunting URIs. The index exists. Use it.
2. The Sandboxes are real targets — you have no excuse not to try the calls.
3. AI-assisted engineering is real, but only if you bring taste and discipline. The agent does the typing; you do the thinking.

**Slide 21 — Q&A**
Just name, email, GitHub handle, thank-you. No more bullets.

---

## Demo cheat-sheet (print this for the podium)

```
DEMO 2 — Cat 9000V always-on
  URL    : https://sandbox-iosxe-latest-1.cisco.com/restconf
  Auth   : developer / <sandbox creds — confirm on developer.cisco.com day-of>
  Path   : /data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1/description
  Body   : {"Cisco-IOS-XE-native:description":"DevNet-1232 demo"}
  Verb   : PUT     Expected: 204

  Backup curl (if Swagger UI hates the network):
    curl -k -u developer:<creds> \
      -H "Content-Type: application/yang-data+json" \
      -X PUT https://sandbox-iosxe-latest-1.cisco.com/restconf/data/\
Cisco-IOS-XE-native:native/interface/GigabitEthernet=1/description \
      -d '{"Cisco-IOS-XE-native:description":"DevNet-1232 demo"}'

DEMO 3 — Cat 9300 reservable
  Reserve before session at developer.cisco.com/site/sandbox/.
  Same payload, swap base URL. Switch the viewer to 17.12.x to show
  schema drift between IOS-XE versions.

If the live sandbox is flaky:
  Have a recorded 30-second clip of demo 2 on the laptop desktop.
  Don't apologize — say "the sandbox is real infrastructure, here's
  the rehearsal," and play it. Audience will thank you.
```

> ⚠️ Confirm sandbox creds + base URLs on the morning of the talk — they rotate.

---

## Q&A prep — the 10 questions you'll actually get

1. **"How do I know the spec matches what's on my actual device?"**
   → The specs are generated from the same pyang trees Cisco publishes per release. They're a reference, not a discovery probe. For absolute truth, point your client at the device's own `restconf/data/ietf-yang-library:modules-state`.

2. **"How often is it updated?"**
   → Every IOS-XE release. The generator runs on the YANG tarball. The 5-release set on the site today covers ~2 years of trains.

3. **"Why OpenAPI 2.0 and not 3.0/3.1?"**
   → Swagger UI + Postman + Bruno round-trip on 2.0 with zero friction. 3.0 features (callbacks, anyOf, etc.) don't map well to YANG anyway. Pragmatism wins.

4. **"Is this Cisco-supported?"**
   → It's published under CiscoDevNet on GitHub Pages. It's a documentation reference, not a product. File issues, contributions welcome.

5. **"What happens if I PUT/DELETE on the sandbox and break it?"**
   → The always-on sandboxes reset on a schedule. Reservable ones reset between reservations. That's the point.

6. **"What model did you use? ChatGPT? Claude? Copilot?"**
   → GitHub Copilot in agent mode, Claude-class model under the hood. The choice of model mattered less than the discipline of small rounds, tests, and CHANGELOG entries.

7. **"How much did it actually cost?"**
   → $<<TODO>> in tokens, plus my evenings. The fully-loaded equivalent of having a junior do it would have been <<TODO>> person-weeks at <<TODO>> $/week.

8. **"Where did the agent get it wrong?"**
   → Aesthetic taste, knowing when to stop, and architectural calls. The classes of bug it shipped were the same a tired human ships at midnight — and they were caught by tests it also wrote.

9. **"Could I do this for IOS-XR / NX-OS / FXOS?"**
   → Yes. The pipeline (pyang → Python generator → OpenAPI 2.0 → static site) is platform-agnostic. The repo's generators are open, fork away.

10. **"What's next?"**
    → Per-release diff page (already shipped as Tree Compare), gNMI overlay, and a Bruno collection runner against the Sandboxes. Open issues on the repo if you want to vote.

---

## Open follow-ups (post-talk)

- [ ] Confirm sandbox creds + URLs on day-of (Always-On 9000V + reserved C9300).
- [ ] Pre-record 30-second backup video of demo 2 in case the wifi at the venue dies.
- [ ] Bring a printed copy of the demo cheat-sheet.
- [ ] Have the repo open in a second browser window on the same desktop.
- [ ] Decide whether to publish this MD as a blog companion afterwards.
