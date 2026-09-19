/* 每个 agent 的档案卡：它学过什么、按什么准则干活、分几步干。

   正常时这是一张「凭什么信它」的卡。
   混乱时同一张卡变成解释：它没坏，它是在拿自己的规矩去干别人的活——
   荒谬因此有了来路，而不是随机报错。 */

(function () {
  let PROFILES = null;

  /* 档案正文里有字面量 <title>（AG-38 学过「怎么去掉 <title> 那行」）。
     直接塞进 innerHTML 会被当成真标签，把后面整张卡吞掉——
     渲染器的档案把渲染器搞崩了。所有文本一律转义。 */
  const esc = s => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  async function load() {
    if (PROFILES) return PROFILES;
    try {
      PROFILES = (await (await fetch("/api/agents")).json()).profiles;
    } catch { PROFILES = {}; }
    return PROFILES;
  }

  window.renderProfiles = async function (stages) {
    const host = document.getElementById("profiles");
    if (!host) return;
    const P = await load();

    host.innerHTML = Object.keys(P).map(id => {
      const p = P[id];
      const st = (stages || []).find(s => s.agent === id);
      const bad = st && st.actually_did !== st.assigned_to;
      const learned = LANG === "cn" ? p.learned_cn : p.learned_en;
      const rules   = LANG === "cn" ? p.rules_cn   : p.rules_en;
      const steps   = LANG === "cn" ? p.steps_cn   : p.steps_en;

      return `
      <div class="pf ${bad ? "bad" : ""}" data-id="${id}">
        <div class="pf-head">
          <span class="pf-id">${id}</span>
          <span class="pf-task">${bi(esc(p.task_en), esc(p.task_cn))}</span>
          <span class="pf-toggle">${bi("dossier", "档案")}</span>
        </div>

        ${bad ? `
        <div class="pf-warn">
          <b>${bi("Now executing: " + st.actually_did,
                  "当前在执行：" + st.actually_did_cn)}</b>
          <span>${bi(esc(p.misapply_en), esc(p.misapply_cn))}</span>
        </div>` : ""}

        <div class="pf-body">
          <div class="pf-sec">
            <h5>${bi("Trained on", "学过什么")}</h5>
            <ul>${learned.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
          </div>
          <div class="pf-sec">
            <h5>${bi("Operating rules", "工作准则")}</h5>
            <ul class="pf-rules">${rules.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
          </div>
          <div class="pf-sec">
            <h5>${bi("How it works", "它怎么干")}</h5>
            <ol>${steps.map(x => `<li>${esc(x)}</li>`).join("")}</ol>
          </div>
        </div>
      </div>`;
    }).join("");

    host.querySelectorAll(".pf-head").forEach(h => h.onclick = () => {
      const card = h.parentElement;
      const on = card.classList.toggle("on");
      if (on && window.Sound) Sound.tick();
    });

    /* 混乱态：自动把出问题的那张展开，不用用户去找 */
    if ((stages || []).some(s => s.actually_did !== s.assigned_to)) {
      const first = host.querySelector(".pf.bad");
      if (first) first.classList.add("on");
    }
  };

  /* app.js 先于本文件加载，启动时那次 renderAssign 调不到 renderProfiles，
     所以这里自己补一次首屏渲染。 */
  renderProfiles(null);
})();
