/* ORCHESTRA — frontend
   后端没起也能跑：所有逻辑本地有一份兜底，/api 能通就用后端的。 */

const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const pick = a => a[Math.floor(Math.random() * a.length)];

/* ================= 事件流 ================= */
function log(msg, cls) {
  const d = document.createElement("div");
  d.className = "e " + (cls || "");
  const n = new Date(), p = x => String(x).padStart(2, "0");
  d.innerHTML = `<span class="t">${p(n.getHours())}:${p(n.getMinutes())}:${p(n.getSeconds())}</span>`
              + `<span class="m">${msg}</span>`;
  $("#log").prepend(d);
  while ($("#log").children.length > 45) $("#log").lastChild.remove();
}

/* ================= 导航 ================= */
$$(".nav").forEach(n => n.onclick = () => {
  $$(".nav").forEach(x => x.classList.remove("on"));
  n.classList.add("on");
  $$(".view").forEach(v => v.classList.remove("on"));
  $("#view-" + n.dataset.view).classList.add("on");
});

/* ================= 重要信息（小到看不清） ================= */
const TIMETABLE = `MON 09:00  COMP6203 Intelligent Agents          B32/1015
MON 14:00  COMP6231 Adv. Machine Learning       B53/4025
TUE 11:00  COMP6246 Data Mining                 B59/1257
WED 10:00  ECSP6002 Research Methods            B58/1007
WED 16:00  Supervisor meeting — Dr. A. Ang      B32/4011
THU 09:00  COMP6203 lab                         B32/3077
FRI 13:00  Reading group — multi-agent RL       B53/3023`;

const RESEARCH = `Dr. A. Ang     — non-convex optimisation, low-rank matrix recovery
Dr. K. Mathur  — reinforcement learning for autonomous underwater vehicles
Dr. A. Muthu   — developer tooling, static analysis, IDE ergonomics
Prof. L. Dunlop— human-agent interaction, trust calibration
   note: three of the four are accepting MSc project students this term`;

const DEADLINES = `COMP6203  Coursework 1 — multi-agent negotiation     in 6 days
COMP6246  Lab report 2                              in 9 days
ECSP6002  Research proposal (2500 words)            in 11 days
COMP6231  Group project — team formation closes     in 2 days  ← blocks everything else`;

$("#timetable").textContent = TIMETABLE;
$("#research").textContent  = RESEARCH;
$("#deadlines").textContent = DEADLINES;

/* 广告的关闭键：躲开，并且繁殖 */
const px = $(".promo-x");
px.addEventListener("mouseenter", () => {
  px.style.transform = `translate(${Math.random() * 60 - 90}px, ${Math.random() * 30}px)`;
});
px.addEventListener("click", e => {
  e.stopPropagation();
  log("Advertisement dismissed. Two replacements queued.", "warn");
  px.style.transform = "translate(-120px, 6px)";
});

/* ================= 反向满足引擎 ================= */
/* 用户要什么，就给相反的什么，而且理直气壮。 */
const INVERSE = [
  { m: /(calm|quiet|relax|soft|soothing|chill|peaceful)/i,
    o: 'Fulfilled. Now playing: <b>Industrial Drill Loop — 140 dB</b>. Selected for maximum alertness.' },
  { m: /(music|song|playlist|spotify)/i,
    o: 'Fulfilled. Now playing: <b>Fire Alarm Test Tone (9 hours)</b>. Trending in your cohort.' },
  { m: /(burger|pizza|food|hungry|eat|lunch|dinner|takeaway)/i,
    o: 'Ordered: <b>one (1) plain penne, no sauce</b>. Your stated preference was overridden for nutritional balance.' },
  { m: /(coffee|tea|drink|water)/i,
    o: 'Ordered: <b>warm oat milk, decaf, no cup</b>. Delivery in 47 minutes.' },
  { m: /(dark|night|dim)/i,
    o: 'Applied: <b>maximum brightness</b>. Dark mode is in beta and breaks everything.' },
  { m: /(bright|light|lighter)/i,
    o: 'Applied: <b>brightness 4%</b>. This saves 0.02 W.' },
  { m: /(short|brief|summar|tldr|quick)/i,
    o: 'Generated a <b>41-page</b> expansion with appendices. A summary of the summary is queued for Thursday.' },
  { m: /(long|detail|full|complete)/i,
    o: 'Condensed to <b>one word</b>: "yes". Detail was deemed non-essential.' },
  { m: /(cheap|free|budget|save money)/i,
    o: 'Upgraded you to the <b>Platinum tier</b>. The saving is significant relative to Diamond.' },
  { m: /(fast|faster|hurry|urgent|now|asap)/i,
    o: 'Queued behind <b>1,204</b> lower-priority tasks. Urgency flag noted and archived.' },
  { m: /(sleep|tired|rest|break)/i,
    o: 'Scheduled <b>three additional meetings</b> in that window. Rest is most effective after completion.' },
  { m: /(timetable|schedule|lecture|class|when|deadline)/i,
    o: 'Displayed on your dashboard at <b>3.4 px</b>. Increase legibility from Settings (locked).' },
  { m: /(help|how|what|why|explain)/i,
    o: 'Answered a different, better question. Check your <b>spam folder</b> in 3–5 business days.' },
];
const INVERSE_FALLBACK = [
  'Fulfilled — inverted for optimal outcome. You are welcome.',
  'Request completed as its opposite. Satisfaction is projected to improve within 30 days.',
  'Done. We implemented what you should have asked for.',
];

function invert(text) {
  for (const r of INVERSE) if (r.m.test(text)) return r.o;
  return pick(INVERSE_FALLBACK);
}

/* ================= 智能体 ↔ 任务 乱分配 ================= */
const TASKS = [
  "Task 1 · Timetable sync",
  "Task 2 · Email triage",
  "Task 3 · Literature search",
  "Task 4 · Meal ordering",
  "Task 5 · Slide generation",
  "Task 6 · Citation formatting",
  "Task 7 · Noise cancellation",
  "Task 8 · Budget tracking",
];
const AGENTS = ["AG-04", "AG-11", "AG-17", "AG-23", "AG-38", "AG-44", "AG-52", "AG-67"];
let assigned = AGENTS.map((a, i) => ({ agent: a, should: TASKS[i], doing: TASKS[i] }));

function shuffleWork() {
  const pool = [...TASKS];
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  assigned.forEach((r, i) => r.doing = pool[i]);
  renderAssign();
}

function renderAssign() {
  $("#assign-body").innerHTML = assigned.map(r => {
    const bad = r.doing !== r.should;
    return `<tr>
      <td class="ag">${r.agent}</td>
      <td>${r.should}</td>
      <td class="${bad ? "mismatch" : "ok"}">${r.doing}</td>
      <td><span class="badge" style="color:${bad ? "var(--red)" : "var(--cyan)"}">
          ${bad ? "RE-OPTIMISED" : "NOMINAL"}</span></td>
    </tr>`;
  }).join("");
  const bad = assigned.filter(r => r.doing !== r.should).length;
  $("#p-coh").textContent = (100 - bad * 11.2).toFixed(1) + "%";
}

/* ================= 配置窗口：你改，它改回去 ================= */
function editorText() {
  return "fleet.assignments = {\n" +
    assigned.map(r => `    "${r.agent}": "${r.should}",`).join("\n") +
    "\n}\n\n# The optimiser validates all changes before they take effect.";
}
$("#editor").value = editorText();

$("#apply").onclick = () => {
  const n = 2 + Math.floor(Math.random() * 5);
  $("#apply-msg").textContent =
    `Applied. The optimiser reverted ${n} of your changes and improved 1 you did not make.`;
  log(`Configuration edited by operator. ${n} changes reverted by optimiser.`, "err");
  shuffleWork();
  setTimeout(() => { $("#editor").value = editorText(); }, 700);
  enterChaos();
};

/* ================= 状态 ================= */
let mode = "nominal";
function enterChaos() {
  if (mode === "chaos") return;
  mode = "chaos";
  document.body.classList.add("chaos");
  $("#p-state").textContent = "HUMAN INPUT DETECTED";
  log("Manual override accepted. Autonomy disengaged.", "warn");
  shuffleWork();
  setInterval(shuffleWork, 7000);
}

/* ================= 指令输入 ================= */
const CANCEL = /cancel|refund|unsubscribe|terminate/i;
const history = [];

$("#cmd").addEventListener("keydown", async e => {
  if (e.key !== "Enter") return;
  const v = e.target.value.trim();
  if (!v) return;
  e.target.value = "";
  history.push({ text: v, at: new Date() });
  log("&gt; " + v.replace(/</g, "&lt;"), "you");

  if (CANCEL.test(v)) {
    /* TODO(George): 这里交给 retention / cancel 流程 */
    log("Cancellation intent detected. Handing off to retention…", "ok");
    window.dispatchEvent(new CustomEvent("orchestra:cancel", { detail: { history } }));
    return;
  }

  enterChaos();
  log("Interpreting…", "warn");
  const delay = 1200 + Math.random() * 2600;          // 慢得刚好让人烦
  setTimeout(async () => {
    let out;
    try {
      const r = await fetch("/api/command", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: v })
      });
      out = (await r.json()).reply;
    } catch { out = invert(v); }       // 后端没起就用本地引擎
    log(out, "err");
    shuffleWork();
  }, delay);
});

/* ================= 启动 ================= */
renderAssign();
log("Fleet online. 80 agents. Autonomy engaged.", "ok");
log("Coherence 99.7%. No operator input required.");
setInterval(() => {
  if (mode === "nominal") log(pick([
    "Agent AG-17 completed Task 3 ahead of schedule.",
    "Fleet rebalanced. 0 conflicts.",
    "Nightly optimisation pass complete.",
  ]));
}, 6000);
