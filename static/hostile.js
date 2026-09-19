/* 仪表盘的两副面孔。

   试用期：没有广告，正文 13px，位置固定 —— 一个正常、好用、重点清晰的界面。
   掉档后：广告铺满，正文缩到 3.4px，并且每 30 秒把内容块换一次位置。
           给你一个放大镜，但你一用它，它就提前换位置——不等你看清。 */

(function () {
  const SHUFFLE_MS = 30000;      // 用户定的：每 30 秒换一次位置
  const LENS_PATIENCE = 2600;    // 放大镜用超过这么久，就提前把内容挪走

  const H = { hostile: false, timer: null, lensOn: false, lensTimer: null };

  const EXTRA_PROMOS = [
    `<div class="promo promo-b">
       <div class="promo-big2">🎁 REFER A FRIEND</div>
       <div class="promo-sub">Both of you get 3 months of a feature we are deprecating in October</div>
     </div>`,
    `<div class="promo promo-c">
       <div class="promo-marquee"><span>★ NEW: AGENTS CAN NOW SEND EMOJI ★ DARK MODE (BETA, BREAKS EVERYTHING) ★ NEW: AGENTS CAN NOW SEND EMOJI ★ DARK MODE (BETA, BREAKS EVERYTHING) ★</span></div>
     </div>`,
  ];

  /* ---------------- 干净 ↔ 敌意 ---------------- */
  window.setHostile = function (on) {
    if (H.hostile === on) return;
    H.hostile = on;
    document.body.classList.toggle("hostile", on);
    document.getElementById("promos").hidden = !on;
    document.getElementById("lensbar").hidden = !on;

    const grid = document.getElementById("grid");
    // 顶栏的两个指标也得跟着掉，不然「降级了但一切 99.7% 正常」会穿帮
    const st = document.getElementById("p-state");
    const co = document.getElementById("p-coh");
    if (st) st.textContent = on ? "DEGRADED" : "NOMINAL";
    if (co) co.textContent = on ? "41.2%" : "99.7%";

    if (on) {
      EXTRA_PROMOS.forEach(html => {
        const d = document.createElement("div");
        d.innerHTML = html.trim();
        d.firstElementChild.classList.add("added");
        grid.appendChild(d.firstElementChild);
      });
      refreshLensLabels();
      H.timer = setInterval(shuffle, SHUFFLE_MS);
      countdown();
      if (window.log) {
        log("Layout optimisation enabled. Content positions refresh every 30s.",
            "已启用版面优化。内容位置每 30 秒刷新一次。", "warn");
      }
    } else {
      clearInterval(H.timer);
      [...grid.querySelectorAll(".promo.added")].forEach(e => e.remove());
    }
  };

  /* ---------------- 每 30 秒把内容换位置 ---------------- */
  function shuffle() {
    const grid = document.getElementById("grid");
    const kids = [...grid.children];
    for (let i = kids.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      grid.insertBefore(kids[i], kids[j]);
    }
    [...grid.children].forEach(k => {
      k.classList.remove("moved");
      void k.offsetWidth;
      k.classList.add("moved");
    });
    if (window.Sound) Sound.tick();
    resetCountdown();
  }

  /* ---------------- 倒计时：告诉你它马上又要动 ---------------- */
  let left = SHUFFLE_MS / 1000;
  function countdown() {
    setInterval(() => {
      if (!H.hostile) return;
      left = Math.max(0, left - 1);
      const t = document.getElementById("lens-t");
      if (t) t.innerHTML = bi(`Layout refreshes in ${left}s`, `版面 ${left} 秒后刷新`);
    }, 1000);
  }
  function resetCountdown() { left = SHUFFLE_MS / 1000; }

  /* ---------------- 放大镜：能看清，但看不久 ---------------- */
  function refreshLensLabels() {
    const l = document.getElementById("lens-label");
    if (l) l.innerHTML = bi(H.lensOn ? "Magnifier on" : "Magnifier",
                            H.lensOn ? "放大镜已开" : "放大镜");
    const w = document.getElementById("lens-warn");
    if (w) w.innerHTML = H.lensOn
      ? bi("Legibility is being re-optimised…", "正在重新优化可读性…")
      : "";
  }

  document.addEventListener("click", e => {
    if (!e.target.closest("#lens-on")) return;
    H.lensOn = !H.lensOn;
    document.body.classList.toggle("lens", H.lensOn);
    refreshLensLabels();
    clearTimeout(H.lensTimer);
    if (H.lensOn) {
      if (window.Sound) Sound.tick();
      // 你一开始看，它就开始盘算把内容挪走
      H.lensTimer = setTimeout(() => {
        shuffle();
        H.lensOn = false;
        document.body.classList.remove("lens");
        refreshLensLabels();
        if (window.Sound) Sound.fail();
        if (window.log) {
          log("Magnifier timed out. Layout refreshed.",
              "放大镜已超时。版面已刷新。", "err");
        }
      }, LENS_PATIENCE);
    }
  });
})();
