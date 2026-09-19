/* 三档语言：en（给评委）/ cn（给我自己）/ both（练的时候用）
   动态文本由后端同时给出 en + cn，这里只管界面固定文案。 */

const I18N = {
  "nav.pipeline":  ["Live Pipeline", "实时流水线"],
  "nav.dashboard": ["Dashboard", "仪表盘"],
  "nav.agents":    ["Agent Assignments", "智能体分工"],
  "nav.code":      ["Configuration", "底层配置"],
  "nav.settings":  ["⚙ Settings", "⚙ 设置"],

  "pipe.title": ["STUDY PIPELINE", "学业流水线"],
  "pipe.note":  ["real timetable · real modules · real prep packs",
                 "真实课表 · 真实课程 · 真实预习包"],
  "pipe.run":   ["▶ Run pipeline", "▶ 运行流水线"],

  "card.timetable": ["YOUR TIMETABLE", "你的课表"],
  "card.research":  ["SUPERVISOR RESEARCH INTERESTS", "导师研究方向"],
  "card.deadlines": ["COURSEWORK DEADLINES", "作业死线"],

  "agents.title": ["AGENT ↔ TASK ASSIGNMENT", "智能体 ↔ 任务 分配"],
  "th.agent":    ["AGENT", "智能体"],
  "th.assigned": ["ASSIGNED TO", "本应负责"],
  "th.doing":    ["ACTUALLY DOING", "实际在做"],
  "th.status":   ["STATUS", "状态"],

  "code.title": ["CONFIGURATION", "底层配置"],
  "code.hint":  ["Edit the assignment map to fix a misrouted agent. Changes are validated by the optimiser before they take effect.",
                 "编辑分配表即可修正走错任务的智能体。所有修改需经优化器校验后生效。"],
  "code.apply": ["Apply changes", "应用修改"],

  "settings.title": ["SETTINGS", "设置"],

  "pay.title":   ["Performance is limited on your current plan",
                  "当前套餐下，性能受限"],
  "pay.decline": ["Continue with degraded performance", "继续忍受降级后的性能"],
  "pay.restored":["Performance restored. Thank you for your upgrade.",
                  "性能已恢复。感谢您的升级。"],
};

let LANG = "both";                     // en | cn | both

function t(key) {
  const v = I18N[key];
  if (!v) return key;
  return LANG === "en" ? v[0] : LANG === "cn" ? v[1] : v[0];
}

function tSub(key) {                   // 双语模式下的第二行
  const v = I18N[key];
  return (LANG === "both" && v) ? v[1] : "";
}

/* 把 en / cn 两段文本按当前语言拼成一段显示用的 HTML */
function bi(en, cn) {
  if (LANG === "en") return en;
  if (LANG === "cn") return cn || en;
  return cn ? `${en}<span class="cn">${cn}</span>` : en;
}

function applyLang() {
  /* 按钮标签也归 applyLang 管——之前只在点击时更新，用脚本切语言时会不同步，
     结果「纯英文」模式下按钮上还挂着「中文」两个字。 */
  const btn = document.getElementById("lang");
  if (btn) btn.textContent = LANG === "both" ? "EN / 中文"
                           : LANG === "en"   ? "EN"
                           : "中文";
  document.querySelectorAll("[data-i]").forEach(el => {
    const k = el.dataset.i;
    const sub = tSub(k);
    el.innerHTML = t(k) + (sub ? `<span class="cn">${sub}</span>` : "");
  });
  document.body.dataset.lang = LANG;
}
