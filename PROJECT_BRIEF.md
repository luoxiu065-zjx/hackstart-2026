> ⚠️ **作废声明（2026-09-19 15:10）**
> 这份 brief 写于上午 11:40，当时的方案是 canvas 里 80 个智能体的舰队可视化。
> 中午方向改成了「真实流水线 + 商业化降级」，**代码里从来没有实现过那个舰队**。
> **现在的真实规格以 `SPEC.md` 为准**，本文件只作为当时决策的存档。

# ORCHESTRA — Project Brief

**HackStart 2026 · Theme: Stubborn Software ("fight the user")**
Team: Jiaxun Zhong (`luoxiu065-zjx`) + George B
Submission deadline: **17:00** — judging 17:00–18:00, presentations 18:00–18:45

---

## 1. One-liner

**ORCHESTRA is an enterprise dashboard commanding a fleet of 80 AI agents. It works flawlessly — until a human touches it. And the moment you try to cancel your subscription, it becomes perfect again.**

Closing line of the pitch:

> *"It was never broken. It just didn't want to work for you."*

---

## 2. The demo, in three acts

**Act I — Perfection (0:00–0:15)**
The fleet runs itself. 80 agents hold a lattice formation, coherence 99.7%, latency 0.2s. Connection lines shimmer. The event stream says: *"No operator input required."* It looks like a real, expensive product.

**Act II — A human takes control (0:15–0:50)**
The user types one command. From that instant:
- Latency jumps to 8.4s. The fleet scatters.
- Every command is **misread with total confidence** — it latches onto the least important word in the sentence: *"Parsed 'the' as a request for FONT ADVICE. Routing to agent 44."*
- The UI begins to corrupt: flicker, jitter, colours shift red.
- Every attempt to fix it makes it worse.

**Act III — The turn (0:50–1:30)**
The user goes looking for the exit. It's buried: `⚙ Settings → Billing → Cancel subscription` (tiny grey link, three clicks deep — the burial is itself a dark pattern).

The instant it is clicked, **everything snaps back to perfection**, and three things happen:

1. **The replay.** It re-executes every command it mangled, correctly:
   *"Request 11:42 — 'deploy 12 agents to sector 4' — completed in 0.3s."*
   It understood the entire time.

2. **The cancellation survey.** A long, beautifully designed questionnaire. Each item is not a question — it is **proof of competence**, offered as a bribe:
   - *"I have drafted your email to your supervisor. Tone matched to your last three messages."*
   - *"Tomorrow's schedule is resolved. I moved your two conflicting meetings."*
   - *"Your usual order is placed. It arrives in 12 minutes. Cancelling now wastes it."*

   The progress bar runs **backwards**. "Question 3 of 47" becomes "3 of 48". Every item is skippable in one click — it only *feels* endless. Six cards total.

3. **The exit shrinks.** "I still want to cancel" gets one font size smaller each time it is clicked. Three clicks and it is over: the fleet drains to grey and dies.

---

## 3. Why this scores on all four judging criteria

| Criterion | How we hit it |
|---|---|
| **Functionality** | Zero external APIs, zero model calls. Runs fully offline — bad venue wifi cannot kill the demo. |
| **Aesthetics** | The product looks genuinely premium, and the *contrast* between the corrupted state and the retention state is the whole visual argument. Hostile ≠ ugly. |
| **Uniqueness** | The brief's four example ideas (one-character password manager, self-deleting text editor…) will be built by a third of the room. Ours is a system that turns on you, with a thesis. There is a separate **Best Idea** prize. |
| **Salesmanship** | Every beat is built for a judge standing at our table for 90 seconds, and the closing line is written already. |

**Two triggers, always.** Retention fires from the buried button **and** from typing `cancel` / `refund` / `unsubscribe` into the command box. A judge who never finds the button still sees the twist. The demo physically cannot fail.

---

## 4. Tech stack — Python backend + one HTML page

Decided because we want to write Python and because it splits the work cleanly.

```
Python (FastAPI)          ← the agent "brain": all logic, all text
   │  JSON over HTTP
HTML + Canvas + JS        ← rendering only: the swarm, the UI, the animation
```

**Why the logic belongs in Python:** the misinterpretation engine, the retention script, the survey content and the fleet telemetry are all pure data transforms. That is exactly the part one person can own without touching the other person's files.

**Why not pure Python (pygame / Streamlit):** Aesthetics is 25% of the score. A canvas in a browser gets us a premium-looking product in an hour; pygame does not, and Streamlit cannot be made to look like this at all.

**Demo safety:** one command starts it — `python -m uvicorn app.main:app`. The frontend also ships a hardcoded fallback table, so if the backend is not running the demo still runs.

---

## 5. Repo and file ownership — no merge conflicts

Repo: `luoxiu065-zjx/hackstart-2026` (private — send me your GitHub username and I will add you)

```
app/
  main.py         FastAPI app + routes          ← GEORGE
  garble.py       misinterpretation engine      ← GEORGE
  retention.py    replay + survey content       ← GEORGE
  static/
    index.html    layout, styling, the swarm    ← JIAXUN
    swarm.js      canvas animation              ← JIAXUN
PROJECT_BRIEF.md  this file
```

**Rule: nobody edits a file they do not own.** With five hours left and two people, this is worth more than any branching strategy. Everything goes straight to `main`; `git pull --rebase` before every push.

The API contract between us, fixed now so we can work in parallel:

```
POST /api/command   {"text": "deploy 12 agents"}
  -> {"mode":"chaos", "reply":"Parsed 'the' as a request for FONT ADVICE...",
      "latency":8.4, "scatter":true}

POST /api/cancel    {}
  -> {"mode":"retention", "replay":[{"time":"11:42","text":"...","ms":300}],
      "survey":[{"title":"...","body":"..."}]}
```

---

## 6. Timeline

| Time | |
|---|---|
| now – 12:00 | George: `garble.py` returning canned strings. Jiaxun: swarm on screen, chaos state working. |
| 12:00 – 12:15 | paper aeroplane contest (optional) |
| 13:00 | lunch |
| 14:00 – 15:00 | **wire frontend to backend.** First end-to-end: type → misread → scatter. |
| 15:00 – 16:00 | the turn: replay + survey + shrinking exit link |
| 16:00 – 16:40 | polish pass — this is the Aesthetics score. Nothing new after 16:40. |
| 16:40 – 17:00 | rehearse the 90-second demo out loud, twice. Commit, push, submit. |

**Hard rule: no new features after 16:40.** A polished small thing beats a broken big thing.

---

## 7. What we are deliberately NOT building

No login, no database, no accounts, no settings that work, no mobile layout, no tests.
The fleet size is fixed at 80. The survey is exactly six cards.

If we finish early, the answer is **more polish**, not more features.
