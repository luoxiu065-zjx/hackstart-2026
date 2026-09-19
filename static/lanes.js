/* 泳道图：每个 agent 一条自己的线，线上一个点标出它做到哪一步。

   正常时：六条线各走各的，点停在自己那一格。
   混乱时：线会拐到别人的泳道去——谁跑去干了谁的活，一眼就看出来。 */

(function () {
  const AGENTS = [
    ["AG-04", "Task 1 · Timetable sync",     "任务 1 · 课表同步"],
    ["AG-11", "Task 2 · Module resolution",  "任务 2 · 课程匹配"],
    ["AG-17", "Task 3 · Lead-time analysis", "任务 3 · 提前量计算"],
    ["AG-23", "Task 4 · Prep pack assembly", "任务 4 · 预习包装配"],
    ["AG-38", "Task 5 · Markdown render",    "任务 5 · 文档渲染"],
    ["AG-44", "Task 6 · Delivery",           "任务 6 · 投递"],
  ];
  const W = 900, LANE = 58, PAD_L = 96, PAD_T = 38, TRACK = W - PAD_L - 40;
  const H = PAD_T + AGENTS.length * LANE + 16;
  const STEP = TRACK / 6;

  const ns = "http://www.w3.org/2000/svg";
  const mk = (tag, attrs, parent) => {
    const e = document.createElementNS(ns, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };

  const laneY = i => PAD_T + i * LANE + LANE / 2;
  const stepX = i => PAD_L + i * STEP + STEP / 2;

  window.renderLanes = function (stages) {
    const host = document.getElementById("lanes");
    if (!host) return;
    host.innerHTML = "";
    const svg = mk("svg", { viewBox: `0 0 ${W} ${H}`, class: "ln" }, host);

    /* 顶上的阶段刻度 */
    for (let s = 0; s < 6; s++) {
      const t = mk("text", { x: stepX(s), y: 16, class: "ln-step" }, svg);
      t.textContent = (LANG === "cn" ? "阶段 " : "Stage ") + (s + 1);
      mk("line", { x1: stepX(s), y1: 24, x2: stepX(s), y2: H - 10, class: "ln-grid" }, svg);
    }

    AGENTS.forEach(([id, en, cn], i) => {
      const y = laneY(i);
      const st = stages && stages[i];

      /* 泳道标签 */
      const lab = mk("text", { x: 14, y: y + 4, class: "ln-agent" }, svg);
      lab.textContent = id;

      /* 这条 agent 的轨道 */
      mk("line", { x1: PAD_L, y1: y, x2: PAD_L + TRACK, y2: y, class: "ln-track" }, svg);

      if (!st) {
        const tip = mk("text", { x: PAD_L + 8, y: y - 8, class: "ln-idle" }, svg);
        tip.textContent = LANG === "cn" ? "待命" : "idle";
        return;
      }

      const own = i;                                   // 本应负责的阶段
      const did = AGENTS.findIndex(a => a[1] === st.actually_did);
      const target = did < 0 ? own : did;
      const bad = target !== own;

      /* 已走完的那一段线 */
      mk("line", {
        x1: PAD_L, y1: y, x2: stepX(own), y2: y,
        class: "ln-done " + (st.ok ? "ok" : "bad"),
      }, svg);

      /* 跨泳道的改派线 */
      if (bad) {
        const y2 = laneY(target);
        mk("path", {
          d: `M ${stepX(own)} ${y} C ${stepX(own) + 46} ${y}, ${stepX(target) - 46} ${y2}, ${stepX(target)} ${y2}`,
          class: "ln-jump",
        }, svg);
        const t = mk("text", { x: (stepX(own) + stepX(target)) / 2, y: (y + y2) / 2 - 6, class: "ln-jump-t" }, svg);
        t.textContent = LANG === "cn" ? "改派 →" : "re-routed →";
      }

      /* 「它现在在这个点上」 */
      const g = mk("g", { class: "ln-mark " + (st.ok ? "ok" : "bad"), transform: `translate(${stepX(target)},${laneY(target)})` }, svg);
      mk("circle", { r: 9, class: "ln-halo" }, g);
      mk("circle", { r: 4.5, class: "ln-dot" }, g);

      /* 这一步在干什么。靠右的点把文字放左边，否则会顶出画布、跟别的行叠在一起。 */
      const cx = stepX(target), cy = laneY(target);
      const right = cx > PAD_L + TRACK * 0.58;
      const tx = right ? cx - 16 : cx + 16;
      const anchor = right ? "end" : "start";

      const d = mk("text", { x: tx, y: cy - 9, class: "ln-doing", "text-anchor": anchor }, svg);
      d.textContent = LANG === "cn" ? cn : en;

      const m = mk("text", { x: tx, y: cy + 9, class: "ln-detail", "text-anchor": anchor }, svg);
      const txt = (LANG === "cn" ? st.detail_cn : st.detail) || "";
      m.textContent = (txt.length > 30 ? txt.slice(0, 30) + "…" : txt) + " · " + st.ms + "ms";
    });
  };
})();
