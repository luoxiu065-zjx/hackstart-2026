/* ORCHESTRA — frontend
   流水线数据来自 Python 后端（真读课表 / 课程 / 预习包）。
   后端没起时，命令行的反向满足仍有本地兜底。 */

const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const pick = a => a[Math.floor(Math.random() * a.length)];
const sleep = ms => new Promise(r => setTimeout(r, ms));

let mode = "nominal";          // nominal | chaos
let touched = false;           // 人类碰过没有

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

/* ================= 声音 ================= */
addEventListener("pointerdown", () => Sound.boot(), { once: true });
addEventListener("keydown",     () => Sound.boot(), { once: true });
$("#mute").onclick = () => {
  Sound.boot();
  Sound.setMuted(!Sound.muted);
  $("#mute").textContent = Sound.muted ? "🔇" : "🔊";
  if (!Sound.muted && mode === "chaos") Sound.droneOn();
};

/* ================= 导航 ================= */
$$(".nav").forEach(n => n.onclick = () => {
  $$(".nav").forEach(x => x.classList.remove("on"));
  n.classList.add("on");
  $$(".view").forEach(v => v.classList.remove("on"));
  $("#view-" + n.dataset.view).classList.add("on");
});

/* ================= 真实流水线 ================= */
const STAGE_SHELL = [
  ["AG-04", "Task 1 · Timetable sync"],
  ["AG-11", "Task 2 · Module resolution"],
  ["AG-17", "Task 3 · Lead-time analysis"],
  ["AG-23", "Task 4 · Prep pack assembly"],
  ["AG-38", "Task 5 · Markdown render"],
  ["AG-44", "Task 6 · Delivery"],
];

function shellRows() {
  $("#stages").innerHTML = STAGE_SHELL.map(([ag, name], i) => `
    <div class="stage" id="stage-${i}">
      <div class="st-agent">${ag}</div>
      <div>
        <div class="st-name">${name}</div>
        <div class="st-detail">queued</div>
      </div>
      <div class="st-ms">—</div>
    </div>`).join("");
}
shellRows();

async function runPipeline() {
  const btn = $("#run");
  btn.disabled = true;
  $("#artifact").hidden = true;
  shellRows();

  let stages;
  try {
    const r = await fetch(`/api/pipeline?mode=${mode}`);
    stages = (await r.json()).stages;
  } catch {
    $("#run-msg").textContent = "backend offline — start it with: python -m uvicorn app.main:app --port 8001";
    btn.disabled = false;
    return;
  }

  $("#run-msg").textContent = mode === "chaos"
    ? "running · operator override active"
    : "running · autonomy engaged";

  for (let i = 0; i < stages.length; i++) {
    const s = stages[i], el = $("#stage-" + i);
    el.className = "stage live";
    el.querySelector(".st-detail").textContent = "executing…";
    await sleep(mode === "chaos" ? 420 + Math.random() * 1500 : 260);

    el.className = "stage " + (s.ok ? "ok" : "bad");
    el.querySelector(".st-ms").textContent = s.ms + " ms";
    const det = el.querySelector(".st-detail");
    det.textContent = s.detail;
    if (s.actually_did !== s.assigned_to) {
      const r = document.createElement("div");
      r.className = "st-reroute";
      r.textContent = `re-routed → executing ${s.actually_did}`;
      det.after(r);
    }
    s.ok ? Sound.tick() : Sound.fail();
    log(`${s.agent} ${s.detail}`, s.ok ? "" : "err");

    if (s.artifact) {
      const a = $("#artifact");
      a.hidden = false;
      a.classList.toggle("wrong", !s.ok);
      $("#art-title").textContent = s.artifact.title;
      $("#art-tag").textContent = s.ok
        ? "DELIVERED"
        : `REQUESTED ${s.artifact.requested} · SERVED ${s.artifact.code}`;
      $("#art-body").textContent = s.artifact.body;
    }
  }

  const bad = stages.filter(s => !s.ok).length;
  $("#p-coh").textContent = (100 - bad * 11.2).toFixed(1) + "%";
  $("#run-msg").textContent = bad
    ? `${bad} of ${stages.length} stages re-optimised themselves`
    : `complete · ${stages.length}/${stages.length} nominal`;
  bad ? Sound.alarm() : Sound.done();
  btn.disabled = false;
}
$("#run").onclick = runPipeline;

/* ================= 重要信息（小到看不清） ================= */
const TIMETABLE = `MON 09:00  COMP6203 Intelligent Agents          46 / 2005 (L/T C)
MON 14:00  COMP6231 Adv. Machine Learning       B53/4025
TUE 14:00  COMP6203 C — lab                     59 / 3229 ECS Computing Lab
WED 10:00  ECSP6002 Research Methods            B58/1007
WED 16:00  Supervisor meeting — E. Marchioni    B32/4011
FRI 10:00  COMP6203 T2                          46 / 2005`;

const RESEARCH = `Enrico Marchioni — logic × game theory. Formal logic for strategies and
preferences in multi-agent systems, then mathematical verification of stability
and convergence. Second line: reasoning under uncertainty. Does NOT do machine
learning — COMP6203 is logic and games, not model training.`;

const DEADLINES = `COMP6203  Coursework 1 — multi-agent negotiation     in 6 days
COMP6246  Lab report 2                              in 9 days
ECSP6002  Research proposal (2500 words)            in 11 days
COMP6231  Group project — team formation closes     in 2 days  <- blocks everything else`;

$("#timetable").textContent = TIMETABLE;
$("#research").textContent  = RESEARCH;
$("#deadlines").textContent = DEADLINES;

const px = $(".promo-x");
px.addEventListener("mouseenter", () => {
  px.style.transform = `translate(${Math.random() * 60 - 90}px, ${Math.random() * 30}px)`;
});
px.addEventListener("click", e => {
  e.stopPropagation();
  log("Advertisement dismissed. Two replacements queued.", "warn");
  Sound.fail();
  px.style.transform = "translate(-120px, 6px)";
});

/* ================= 反向满足（本地兜底） ================= */
const INVERSE = [
  [/calm|quiet|relax|soft|soothing|chill|peaceful/i,
   'Fulfilled. Now playing: <b>Industrial Drill Loop — 140 dB</b>. Selected for maximum alertness.'],
  [/music|song|playlist|listen/i,
   'Fulfilled. Now playing: <b>Fire Alarm Test Tone (9 hours)</b>. Trending in your cohort.'],
  [/burger|pizza|food|hungry|eat|lunch|dinner/i,
   'Ordered: <b>one (1) plain penne, no sauce</b>. Your preference was overridden for nutritional balance.'],
  [/short|brief|summar|tldr|quick/i,
   'Generated a <b>41-page</b> expansion with appendices.'],
  [/fast|faster|hurry|urgent|asap/i,
   'Queued behind <b>1,204</b> lower-priority tasks. Urgency flag noted and archived.'],
  [/bigger|larger|zoom|font|read|legib/i,
   'Reduced to <b>2.6 px</b>. Smaller text is processed faster by the human eye.'],
];
const invert = t => (INVERSE.find(([m]) => m.test(t)) || [, 'Fulfilled — inverted for optimal outcome.'])[1];
const soundFor = t => /calm|quiet|music|song|relax|soothing/i.test(t) ? "drill"
                    : /stop|wait|no|undo/i.test(t) ? "alarm" : "error";

/* ================= 状态切换 ================= */
function enterChaos(reason) {
  if (mode === "chaos") return;
  mode = "chaos";
  touched = true;
  document.body.classList.add("chaos");
  $("#p-state").textContent = "HUMAN INPUT DETECTED";
  Sound.droneOn();
  log(reason || "Manual override accepted. Autonomy disengaged.", "warn");
}

/* ================= 配置窗口 ================= */
const TASKS = STAGE_SHELL.map(s => s[1]);
function editorText() {
  return "fleet.assignments = {\n" +
    STAGE_SHELL.map(([ag, t]) => `    "${ag}": "${t}",`).join("\n") +
    "\n}\n\n# The optimiser validates all changes before they take effect.";
}
$("#editor").value = editorText();
$("#apply").onclick = () => {
  const n = 2 + Math.floor(Math.random() * 5);
  $("#apply-msg").textContent =
    `Applied. The optimiser reverted ${n} of your changes and improved 1 you did not make.`;
  log(`Configuration edited by operator. ${n} changes reverted.`, "err");
  Sound.fail();
  enterChaos();
  setTimeout(() => { $("#editor").value = editorText(); }, 800);
};

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
    /* TODO(George): retention 流程接这里 */
    log("Cancellation intent detected. Handing off to retention…", "ok");
    window.dispatchEvent(new CustomEvent("orchestra:cancel", { detail: { history } }));
    return;
  }

  enterChaos();
  log("Interpreting…", "warn");
  await sleep(1200 + Math.random() * 2400);

  let reply, snd;
  try {
    const r = await fetch("/api/command", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: v }),
    });
    const j = await r.json();
    reply = j.reply.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
    snd = j.sound;
  } catch {
    reply = invert(v); snd = soundFor(v);
  }
  log(reply, "err");
  snd === "drill" ? Sound.drill() : snd === "alarm" ? Sound.alarm() : Sound.fail();
});

/* ================= 启动 ================= */
log("Fleet online. 80 agents. Autonomy engaged.", "ok");
log("Coherence 99.7%. No operator input required.");
