/* ORCHESTRA — frontend
   抽不抽风由后端的 billing 状态机决定，前端只负责演出来。 */

const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const sleep = ms => new Promise(r => setTimeout(r, ms));

let account = null;
let lastStages = null;      // 最近一次流水线结果，切语言时重渲染用

/* ================= 事件流 ================= */
function log(en, cn, cls) {
  const d = document.createElement("div");
  d.className = "e " + (cls || "");
  const n = new Date(), p = x => String(x).padStart(2, "0");
  d.innerHTML = `<span class="t">${p(n.getHours())}:${p(n.getMinutes())}:${p(n.getSeconds())}</span>`
              + `<span class="m">${bi(en, cn)}</span>`;
  $("#log").prepend(d);
  while ($("#log").children.length > 45) $("#log").lastChild.remove();
}

/* ================= 语言 / 声音 ================= */
$("#lang").onclick = () => {
  LANG = LANG === "both" ? "en" : LANG === "en" ? "cn" : "both";
  $("#lang").textContent = LANG === "both" ? "EN / 中文" : LANG === "en" ? "EN" : "中文";
  applyLang();
  renderStatic();
};
/* 每次手势都确认一次音频上下文是 running——只在第一次 boot 会漏掉
   「上下文在无手势时就被建出来、之后一直 suspended」这种情况。 */
addEventListener("pointerdown", () => Sound.ensure());
addEventListener("keydown",     () => Sound.ensure());
/* 点喇叭：切静音；切回有声时放一声测试音，让人当场知道音频到底通没通。
   （AudioContext 只能在真实手势里 resume，所以这里是最可靠的自检入口。） */
$("#mute").onclick = () => {
  Sound.ensure();
  Sound.setMuted(!Sound.muted);
  const btn = $("#mute");
  btn.textContent = Sound.muted ? "🔇" : "🔊";
  if (!Sound.muted) {
    Sound.done();
    setTimeout(() => {
      btn.title = "audio: " + Sound.state;
      log(`Audio check — context is ${Sound.state}. If you heard nothing, the tab or system is muted.`,
          `音频自检 —— 上下文状态 ${Sound.state}。如果你没听见声音，是标签页或系统被静音了。`,
          Sound.state === "running" ? "ok" : "err");
    }, 120);
  }
};

/* ================= 导航 ================= */
$$(".nav").forEach(n => n.onclick = () => {
  $$(".nav").forEach(x => x.classList.remove("on"));
  n.classList.add("on");
  $$(".view").forEach(v => v.classList.remove("on"));
  $("#view-" + n.dataset.view).classList.add("on");
});

/* ================= 账户状态 ================= */
const ASSET_LABELS = [
  ["preferences",  "preferences learned", "已学习的偏好"],
  ["automations",  "automations built",   "已建立的自动化"],
  ["packs",        "packs delivered",     "已投递的预习包"],
  ["minutes_saved","minutes saved",       "已为你省下的分钟"],
];

function renderAssets(a) {
  $("#assets").innerHTML = ASSET_LABELS.map(([k, en, cn]) => `
    <div class="asset">
      <div class="asset-n">${a[k]}</div>
      <div class="asset-l">${bi(en, cn)}</div>
    </div>`).join("");
}

function showDowngrade() {
  const a = account;
  $("#downgrade").hidden = false;
  document.body.classList.add("lost");
  $("#dg-h").innerHTML = bi(
    "Your Deluxe trial has ended.",
    "你的豪华版试用已经结束。");
  $("#dg-cmp").innerHTML = `
    <div class="was"><span>${bi("Your plan was", "原套餐")}</span><b>${a.was.tier}</b></div>
    <div class="was"><span>${bi("Latency was", "原延迟")}</span><b>${a.was.latency}</b></div>
    <div class="now"><span>${bi("Your plan now", "当前套餐")}</span><b>${a.tier_name}</b></div>
    <div class="now"><span>${bi("Latency now", "当前延迟")}</span><b>${a.latency}</b></div>`;
  $("#dg-risk").innerHTML = bi(
    `You will lose ${a.assets.preferences} learned preferences, ${a.assets.automations} automations `
    + `and ${a.assets.packs} delivered pack${a.assets.packs === 1 ? "" : "s"}. `
    + `We will hold them for ${a.retention_days} days.`,
    `你将失去 ${a.assets.preferences} 条已学习的偏好、${a.assets.automations} 项自动化、`
    + `以及 ${a.assets.packs} 个已投递的预习包。我们会为你保留 ${a.retention_days} 天。`);
  $("#dg-restore").innerHTML = bi("Restore Deluxe — £39.99 / mo", "恢复豪华版 — £39.99 / 月");
  $("#dg-restore").onclick = () => upgrade("pro");
  Sound.alarm();
}

async function refreshState() {
  try {
    account = await (await fetch("/api/state")).json();
  } catch { return; }

  $("#plan-name").textContent = account.tier_name;
  const pct = account.trial_total ? account.trial_left / account.trial_total : 0;
  $("#plan-fill").style.width = (pct * 100).toFixed(1) + "%";
  $("#plan-left").textContent = account.tier === "trial"
    ? account.trial_left.toFixed(1) + "s"
    : account.price;
  document.body.dataset.tier = account.tier;
  renderAssets(account.assets);
  if (window.setHostile) setHostile(account.tier === "free" || account.tampered);

  if (account.just_expired) {
    log("Trial ended. Reverting to Free plan. No reminder was sent.",
        "试用结束。已回落至免费套餐。我们没有提前提醒你。", "err");
    showDowngrade();
    // 顺便把你踢下线，再登一次给你看看什么叫免费用户
    setTimeout(() => window.dispatchEvent(new Event("orchestra:session-expired")), 2200);
  }
  if (account.tier !== "free" && account.tier !== "trial") {
    $("#downgrade").hidden = true;
    document.body.classList.remove("lost");
  }
}
setInterval(refreshState, 1000);

/* ================= 流水线 ================= */
const SHELL = [
  ["AG-04", "Task 1 · Timetable sync",     "任务 1 · 课表同步"],
  ["AG-11", "Task 2 · Module resolution",  "任务 2 · 课程匹配"],
  ["AG-17", "Task 3 · Lead-time analysis", "任务 3 · 提前量计算"],
  ["AG-23", "Task 4 · Prep pack assembly", "任务 4 · 预习包装配"],
  ["AG-38", "Task 5 · Markdown render",    "任务 5 · 文档渲染"],
  ["AG-44", "Task 6 · Delivery",           "任务 6 · 投递"],
];

/* ---- 智能体 ↔ 任务 分配表：用流水线的真实改派结果填 ---- */
function renderAssign(stages) {
  renderHandover(stages);
  if (window.renderLanes) renderLanes(stages);
  if (window.renderProfiles) renderProfiles(stages);
  const ph = $("#pf-h");
  if (ph) {
    const bad = (stages || []).filter(s => s.actually_did !== s.assigned_to).length;
    ph.innerHTML = bad
      ? bi("Each agent is still following its own rules — just on someone else's task. That is why the output is absurd rather than broken.",
           "每个智能体都还在严格遵守自己的准则——只是用在了别人的任务上。所以结果是荒谬，不是报错。")
      : bi("What each agent was trained on, and the rules it follows. Click a card to open its dossier.",
           "每个智能体学过什么、按什么准则干活。点卡片展开它的档案。");
  }
  const h = $("#lanes-hint");
  if (h) {
    const bad = (stages || []).filter(s => s.actually_did !== s.assigned_to).length;
    h.innerHTML = bad
      ? bi(`${bad} of 6 agents are executing a task that was not assigned to them. The curved lines show where the work actually went.`,
           `6 个智能体里有 ${bad} 个正在执行不属于自己的任务。弯曲的那几条线，就是活儿实际跑去的地方。`)
      : bi("Each agent stays in its own lane. The dot marks the stage it reached.",
           "每个智能体走自己的泳道。那个点标出它做到了哪一步。");
  }
  const rows = stages || SHELL.map(([ag, en, cn]) => ({
    agent: ag, assigned_to: en, name_cn: cn, actually_did: en, actually_did_cn: cn, ok: true,
  }));
  $("#assign-body").innerHTML = rows.map(r => {
    const bad = r.actually_did !== r.assigned_to;
    return `<tr>
      <td class="ag">${r.agent}</td>
      <td>${bi(r.assigned_to, r.name_cn || "")}</td>
      <td class="${bad ? "mismatch" : "ok"}">${bi(r.actually_did, r.actually_did_cn || "")}</td>
      <td><span class="badge" style="color:${bad ? "var(--red)" : "var(--cyan)"}">
          ${bad ? bi("RE-OPTIMISED", "已重新优化") : bi("NOMINAL", "正常")}</span></td>
    </tr>`;
  }).join("");
}

/* 「任务换人」要看得见：谁接了谁的活、原主去哪了、接手的人用什么规矩干。 */
const REASONS = [
  ["entered a scheduled rest period", "进入了计划内休息"],
  ["exceeded its Free-plan quota", "免费额度已用完"],
  ["was re-optimised to a higher-value task", "被重新优化到更有价值的任务上"],
  ["did not acknowledge within 2s", "2 秒内没有应答"],
  ["is held by another write lock", "被另一个写锁占着"],
];

function renderHandover(stages) {
  const box = $("#handover");
  if (!box) return;
  const moved = (stages || []).filter(s => s.actually_did !== s.assigned_to);
  if (!moved.length) { box.innerHTML = ""; return; }

  box.innerHTML = `
    <div class="ho-h">${bi("HANDOVER LOG", "任务交接记录")}
      <span>${bi(`${moved.length} tasks changed hands`, `${moved.length} 项任务换了人`)}</span></div>
    ${moved.map((s, i) => {
      const owner = (stages || []).find(x => x.assigned_to === s.actually_did);
      const [rEn, rCn] = REASONS[i % REASONS.length];
      return `
      <div class="ho-row">
        <span class="ho-from">${s.agent}</span>
        <span class="ho-arrow">→</span>
        <span class="ho-task">${bi(s.actually_did, s.actually_did_cn)}</span>
        <span class="ho-was">${bi(
          `taken from ${owner ? owner.agent : "—"} · ${owner ? owner.agent : "it"} ${rEn}`,
          `接自 ${owner ? owner.agent : "—"} · ${owner ? owner.agent : "对方"}${rCn}`)}</span>
      </div>`;
    }).join("")}`;
}

function shellRows() {
  if (window.renderGraph) renderGraph({ stages: [] });
  $("#stages").innerHTML = SHELL.map(([ag, en, cn], i) => `
    <div class="stage" id="stage-${i}">
      <div class="st-agent">${ag}</div>
      <div>
        <div class="st-name">${bi(en, cn)}</div>
        <div class="st-detail">${bi("queued", "排队中")}</div>
      </div>
      <div class="st-ms">—</div>
    </div>`).join("");
}

async function runPipeline() {
  const btn = $("#run");
  btn.disabled = true;
  $("#artifact").hidden = true;
  shellRows();

  let data;
  try {
    data = await (await fetch("/api/pipeline")).json();
  } catch {
    $("#run-msg").textContent = "backend offline — python -m uvicorn app.main:app --port 8001";
    btn.disabled = false;
    return;
  }

  const chaos = data.mode === "chaos";
  document.body.classList.toggle("chaos", chaos);
  $("#p-state").textContent = chaos ? "DEGRADED" : "NOMINAL";
  if (chaos) Sound.droneOn(); else Sound.droneOff();
  $("#run-msg").innerHTML = bi(data.reason, "");

  for (let i = 0; i < data.stages.length; i++) {
    const s = data.stages[i], el = $("#stage-" + i);
    el.className = "stage live";
    el.querySelector(".st-detail").innerHTML = bi("executing…", "执行中…");
    await sleep(chaos ? 380 + Math.random() * 1400 : 240);

    el.className = "stage " + (s.ok ? "ok" : "bad");
    el.querySelector(".st-ms").textContent = s.ms + " ms";
    const det = el.querySelector(".st-detail");
    det.innerHTML = bi(s.detail, s.detail_cn);
    if (s.actually_did !== s.assigned_to) {
      const owner = data.stages.find(x => x.assigned_to === s.actually_did);
      log(`HANDOVER · ${s.agent} took over ${s.actually_did}${owner ? " from " + owner.agent : ""}`,
          `任务交接 · ${s.agent} 接管了${s.actually_did_cn}${owner ? "（原属 " + owner.agent + "）" : ""}`,
          "err");
      const r = document.createElement("div");
      r.className = "st-reroute";
      r.innerHTML = bi(`re-routed → executing ${s.actually_did}`,
                       `已改派 → 实际执行 ${s.actually_did_cn}`);
      det.after(r);
    }
    if (window.renderGraph) { renderGraph({ ...data, stages: data.stages.slice(0, i + 1) }); }
    if (window.animateGraph) animateGraph(i);
    s.ok ? Sound.tick() : Sound.fail();
    log(`${s.agent} ${s.detail}`, `${s.agent} ${s.detail_cn}`, s.ok ? "" : "err");

    if (s.artifact) {
      const a = $("#artifact");
      a.hidden = false;
      a.classList.toggle("wrong", !s.ok);
      $("#art-title").textContent = s.artifact.title;
      $("#art-tag").textContent = s.ok ? "DELIVERED"
        : s.artifact.code === "LECTURER"
          ? "RENDER TARGET LOST · SUPERVISOR PROFILE SUBSTITUTED"
          : `REQUESTED ${s.artifact.requested} · SERVED ${s.artifact.code}`;
      $("#art-body").innerHTML = s.artifact.html || s.artifact.body || "";
    }
  }

  lastStages = data.stages;
  renderAssign(data.stages);
  if (window.renderGraph) renderGraph(data);
  const bad = data.stages.filter(s => !s.ok).length;
  $("#p-coh").textContent = (100 - bad * 11.2).toFixed(1) + "%";
  bad ? Sound.alarm() : Sound.done();
  await refreshState();
  if (chaos) setTimeout(openPaywall, 900);
  btn.disabled = false;
}
$("#run").onclick = runPipeline;

/* ================= 付费墙 ================= */
async function openPaywall() {
  if (!account) await refreshState();
  const box = $("#paywall");
  $("#pay-h").innerHTML = bi(t("pay.title"), I18N["pay.title"][1]);
  $("#pay-sub").innerHTML = bi(
    `Your current plan: ${account.tier_name}. ${account.footnote}`,
    `当前套餐：${account.tier_name}。${account.footnote}`);
  $("#tiers").innerHTML = account.tiers.map(x => `
    <div class="tier" data-tier="${x.id}">
      <div class="tier-n">${x.name}</div>
      <div class="tier-p">${x.price}</div>
      <div class="tier-b">${bi(x.blurb, x.blurb_cn)}</div>
      <div class="tier-f">${bi(x.footnote, x.footnote_cn)}</div>
      <button class="tier-btn">${bi(
        x.id === "enterprise" ? "Contact sales" : "Upgrade",
        x.id === "enterprise" ? "联系销售" : "立即升级")}</button>
    </div>`).join("");
  $$("#tiers .tier").forEach(el => el.querySelector(".tier-btn").onclick = () => upgrade(el.dataset.tier));
  $("#pay-decline").innerHTML = bi(t("pay.decline"), I18N["pay.decline"][1]);
  box.hidden = false;
}

function closePaywall() { $("#paywall").hidden = true; }
$("#pay-decline").onclick = closePaywall;
/* 开发用逃生口：Esc 或点背景就能关掉。演示时评委只会看到那个 9.5px 的小字链接。 */
$("#paywall").addEventListener("click", e => { if (e.target.id === "paywall") closePaywall(); });
addEventListener("keydown", e => { if (e.key === "Escape") closePaywall(); });

async function upgrade(tier) {
  if (tier === "enterprise") {
    log("A representative will contact you within 6–8 weeks.",
        "我们的代表将在 6–8 周内与您联系。", "warn");
    Sound.fail();
    return;
  }
  account = await (await fetch("/api/upgrade", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tier }),
  })).json();
  $("#paywall").hidden = true;
  document.body.classList.remove("chaos");
  Sound.droneOff(); Sound.done();
  log(I18N["pay.restored"][0], I18N["pay.restored"][1], "ok");
  await refreshState();
}

/* ================= 配置窗口：改源码 = 触发完整性校验 ================= */
function editorText() {
  return "fleet.assignments = {\n" +
    SHELL.map(([ag, en]) => `    "${ag}": "${en}",`).join("\n") +
    "\n}\n\n# Signed configuration. Integrity is verified on every run.";
}
$("#editor").value = editorText();

$("#apply").onclick = async () => {
  const n = 2 + Math.floor(Math.random() * 5);
  $("#apply-msg").innerHTML = bi(
    `Integrity check failed. ${n} unsigned changes detected. Running in safe mode.`,
    `完整性校验失败。检测到 ${n} 处未签名的修改。已进入安全模式。`);
  log("Configuration tampering detected. Safe mode engaged.",
      "检测到配置被修改。已启用安全模式。", "err");
  Sound.alarm();
  try { account = await (await fetch("/api/tamper", { method: "POST" })).json(); } catch {}
  document.body.classList.add("chaos");
  setTimeout(() => { $("#editor").value = editorText(); }, 900);
  setTimeout(openPaywall, 1400);
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
  log("&gt; " + v.replace(/</g, "&lt;"), "", "you");

  if (CANCEL.test(v)) {
    /* TODO(George): retention 流程接这里 */
    log("Cancellation intent detected. Handing off to retention…",
        "检测到取消意向。正在移交挽留流程…", "ok");
    window.dispatchEvent(new CustomEvent("orchestra:cancel", { detail: { history, account } }));
    return;
  }

  log("Interpreting…", "正在理解…", "warn");
  await sleep(1100 + Math.random() * 2200);
  try {
    const j = await (await fetch("/api/command", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: v }),
    })).json();
    const md = s => s.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
    log(md(j.reply), md(j.reply_cn), "err");
    Sound.ensure();
    if (j.sound === "drill") Sound.drill();
    else if (j.sound === "alarm") Sound.alarm();
    else if (j.sound === "ok") Sound.done();      // 豪华版：好好办事，给个悦耳的确认音
    else Sound.fail();
  } catch {
    log("Fulfilled — inverted for optimal outcome.", "已完成——为达成最优结果已作反向处理。", "err");
    Sound.fail();
  }
});

/* ================= 静态文本 ================= */
const TIMETABLE = `MON 09:00  COMP6203 Intelligent Agents      46 / 2005 (L/T C)
MON 14:00  COMP6231 Adv. Machine Learning   B53/4025
TUE 14:00  COMP6203 C — lab                 59 / 3229 ECS Computing Lab
WED 10:00  ECSP6002 Research Methods        B58/1007
FRI 10:00  COMP6203 T2                      46 / 2005`;
const RESEARCH = `Enrico Marchioni — logic x game theory. Formal logic for strategies and
preferences in multi-agent systems, then mathematical verification of stability.
Does NOT do machine learning — COMP6203 is logic and games, not model training.`;
const DEADLINES = `COMP6203  Coursework 1 — multi-agent negotiation   in 6 days
COMP6246  Lab report 2                            in 9 days
ECSP6002  Research proposal (2500 words)          in 11 days`;

function renderStatic() {
  renderAssign(lastStages);
  $("#timetable").textContent = TIMETABLE;
  $("#research").textContent  = RESEARCH;
  $("#deadlines").textContent = DEADLINES;
  shellRows();
}

const px = $(".promo-x");
px.addEventListener("mouseenter", () => {
  px.style.transform = `translate(${Math.random() * 60 - 90}px, ${Math.random() * 30}px)`;
});
px.addEventListener("click", e => {
  e.stopPropagation();
  log("Advertisement dismissed. Two replacements queued.",
      "广告已关闭。两条替补已排队。", "warn");
  Sound.fail();
});

/* ================= 启动 ================= */
applyLang();
renderStatic();
refreshState();
log("Fleet online. 80 agents. Autonomy engaged.", "集群上线。80 个智能体。自治已开启。", "ok");
log("Free trial active — unrestricted performance.", "免费试用中 —— 性能不受限制。", "ok");


/* 设置页里那行 "Language English (locked)" 点了要有反应，不然评委当 bug */
document.addEventListener("click", e => {
  const row = e.target.closest(".srow");
  if (!row || !/Language/.test(row.textContent)) return;
  log("Language is locked by your administrator.",
      "语言设置已被你的管理员锁定。", "warn");
  if (window.Sound) Sound.fail();
});

/* ================= 藏三层的取消入口：设置 → 账单 → 灰色小字 ================= */
$("#to-billing").onclick = () => {
  $("#billing-slot").innerHTML = `
    <div class="billing">
      <div class="bill-h">${bi("Billing", "账单")}</div>
      <div class="srow">${bi("Current plan", "当前套餐")}
        <span class="sval">${account ? account.tier_name : "—"}</span></div>
      <div class="srow">${bi("Next charge", "下次扣费")}
        <span class="sval">${bi("in 27 days", "27 天后")}</span></div>
      <div class="srow">${bi("Payment method", "支付方式")}
        <span class="sval">•••• 4417</span></div>
      <div class="srow">${bi("Invoices", "发票")}
        <span class="sval">${bi("Request by post", "请来函索取")}</span></div>
      <div class="bill-foot">
        <span id="cancel-link">${bi("Cancel subscription", "取消订阅")}</span>
      </div>
    </div>`;
  $("#cancel-link").onclick = () => {
    log("Cancellation intent detected. Handing off to retention…",
        "检测到取消意向。正在移交挽留流程…", "ok");
    window.dispatchEvent(new CustomEvent("orchestra:cancel", { detail: { history, account } }));
  };
};
