/* 正常态的「过程图」：不是日志，是一张能看出「谁在干什么、干到哪一步」的图。

   六个节点按依赖连成一条链，边上跑一个光点表示数据正在流。
   鼠标移到节点上，展开它这一步具体做了什么、用了哪份数据、产出了什么。
   混乱态时，边会改道——你能亲眼看到数据被送错了地方。 */

(function () {
  const NODES = [
    { id: "fetch_timetable", x: 90,  y: 60,  en: "Timetable sync",   cn: "课表同步",   agent: "AG-04" },
    { id: "resolve_modules", x: 290, y: 60,  en: "Module match",     cn: "课程匹配",   agent: "AG-11" },
    { id: "lead_time",       x: 490, y: 60,  en: "Lead-time",        cn: "提前量",     agent: "AG-17" },
    { id: "build_prep",      x: 490, y: 190, en: "Prep assembly",    cn: "预习包装配", agent: "AG-23" },
    { id: "render",          x: 290, y: 190, en: "Render",           cn: "文档渲染",   agent: "AG-38" },
    { id: "deliver",         x: 90,  y: 190, en: "Delivery",         cn: "投递",       agent: "AG-44" },
  ];
  const ORDER = NODES.map(n => n.id);
  const W = 600, H = 260, R = 26;

  const INPUTS = {
    fetch_timetable: ["data/timetable.ics"],
    resolve_modules: ["data/modules.json", "上一步的 124 条日程"],
    lead_time:       ["每门课的上课时间", "距今天的天数"],
    build_prep:      ["data/prep/*.md"],
    render:          ["预习包 markdown"],
    deliver:         ["渲染好的 HTML", "收件人"],
  };

  let state = null;       // 最近一次 /api/pipeline 的结果
  let anim = null;

  function el(tag, attrs, parent) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function nodeById(id) { return NODES.find(n => n.id === id); }

  /* 把「本应的顺序」和「实际的改派」都画出来 */
  function edges() {
    const out = [];
    for (let i = 0; i < ORDER.length - 1; i++) {
      out.push({ from: ORDER[i], to: ORDER[i + 1], kind: "planned" });
    }
    if (state) {
      state.stages.forEach((s, i) => {
        if (s.actually_did !== s.assigned_to) {
          const target = state.stages.findIndex(x => x.assigned_to === s.actually_did);
          if (target >= 0 && target !== i) {
            out.push({ from: ORDER[i], to: ORDER[target], kind: "rerouted" });
          }
        }
      });
    }
    return out;
  }

  function path(a, b, bend) {
    const dx = b.x - a.x, dy = b.y - a.y;
    const mx = a.x + dx / 2, my = a.y + dy / 2 + (bend || 0);
    return `M ${a.x} ${a.y} Q ${mx} ${my} ${b.x} ${b.y}`;
  }

  window.renderGraph = function (data) {
    state = data || state;
    const host = document.getElementById("graph");
    if (!host) return;
    host.innerHTML = "";

    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "gr" }, host);
    const defs = el("defs", {}, svg);
    const m = el("marker", { id: "arw", viewBox: "0 0 8 8", refX: "7", refY: "4",
                             markerWidth: "6", markerHeight: "6", orient: "auto" }, defs);
    el("path", { d: "M0 0 L8 4 L0 8 z", fill: "rgba(255,255,255,.28)" }, m);

    /* ---- 边 ---- */
    edges().forEach((e, i) => {
      const a = nodeById(e.from), b = nodeById(e.to);
      const bend = e.kind === "rerouted" ? (i % 2 ? 70 : -70) : 0;
      const p = el("path", {
        d: path(a, b, bend),
        class: "gr-edge " + e.kind,
        "marker-end": "url(#arw)",
      }, svg);
      if (e.kind === "planned") p.dataset.i = i;
    });

    /* ---- 节点 ---- */
    NODES.forEach((n, i) => {
      const st = state ? state.stages[i] : null;
      const cls = !st ? "idle" : st.ok ? "ok" : "bad";
      const g = el("g", { class: "gr-node " + cls, transform: `translate(${n.x},${n.y})` }, svg);
      el("circle", { r: R, class: "gr-ring" }, g);
      el("circle", { r: 5, class: "gr-dot" }, g);
      const t1 = el("text", { y: R + 18, class: "gr-t1" }, g);
      t1.textContent = LANG === "cn" ? n.cn : n.en;
      const t2 = el("text", { y: R + 32, class: "gr-t2" }, g);
      t2.textContent = n.agent + (st ? " · " + st.ms + "ms" : "");

      g.addEventListener("mouseenter", () => detail(i));
      g.addEventListener("mouseleave", () => detail(-1));
    });

    detail(-1);
  };

  /* 鼠标移上去：这一步到底在干什么 */
  function detail(i) {
    const box = document.getElementById("graph-detail");
    if (!box) return;
    if (i < 0) {
      box.innerHTML = `<div class="gd-hint">${bi(
        "Hover a node to see what that agent actually did.",
        "把鼠标放到任意一个节点上，看它这一步具体做了什么。")}</div>`;
      return;
    }
    const n = NODES[i], st = state ? state.stages[i] : null;
    const rerouted = st && st.actually_did !== st.assigned_to;
    box.innerHTML = `
      <div class="gd-h">${n.agent} · ${bi(n.en, n.cn)}</div>
      <div class="gd-row"><span>${bi("Reads", "读取")}</span>
           <b>${(INPUTS[n.id] || []).join(" · ")}</b></div>
      <div class="gd-row"><span>${bi("Result", "结果")}</span>
           <b>${st ? bi(st.detail, st.detail_cn) : bi("not run yet", "还没跑")}</b></div>
      ${rerouted ? `<div class="gd-row bad"><span>${bi("Re-routed", "被改派")}</span>
           <b>${bi(st.actually_did, st.actually_did_cn)}</b></div>` : ""}
      <div class="gd-row"><span>${bi("Took", "耗时")}</span>
           <b>${st ? st.ms + " ms" : "—"}</b></div>`;
  }

  /* 一个光点沿着链路跑，表示数据正在流动 */
  window.animateGraph = function (stepIndex) {
    const svg = document.querySelector("#graph svg");
    if (!svg) return;
    const edge = svg.querySelector(`.gr-edge.planned[data-i="${stepIndex}"]`);
    if (!edge) return;
    if (anim) anim.remove();
    anim = el("circle", { r: 4, class: "gr-pulse" }, svg);
    const mo = el("animateMotion", { dur: "0.9s", repeatCount: "1", fill: "freeze" }, anim);
    el("mpath", { href: "#" }, mo);
    mo.setAttribute("path", edge.getAttribute("d"));
  };
})();
