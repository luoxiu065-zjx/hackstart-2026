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
    // 幂等：每次都把 class 重新贴一遍，不靠状态位判断，免得被别处改掉后再也回不来
    document.body.classList.toggle("hostile", on);
    if (H.hostile === on) return;
    H.hostile = on;
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

  /* ---------------- C7 两面镜子，点一下功能互换 ---------------- */
  const LENS = { swapped: false, level: 0 };   // level: 0 原始 / +1 放大 / -1 缩小

  function lensLabels() {
    const a = document.getElementById("lens-in-label");
    const b = document.getElementById("lens-out-label");
    if (!a || !b) return;
    // 按钮上写的和它实际干的，在互换之后就对不上了
    a.innerHTML = bi(LENS.swapped ? "(shrinks)" : "Magnify",
                     LENS.swapped ? "（实为缩小）" : "放大");
    b.innerHTML = bi(LENS.swapped ? "(magnifies)" : "Shrink",
                     LENS.swapped ? "（实为放大）" : "缩小");
    document.getElementById("lens-in").classList.toggle("swapped", LENS.swapped);
    document.getElementById("lens-out").classList.toggle("swapped", LENS.swapped);
  }

  function applyLens() {
    document.body.classList.toggle("lens", LENS.level > 0);
    document.body.classList.toggle("lens-small", LENS.level < 0);
  }

  document.addEventListener("click", e => {
    const btn = e.target.closest("#lens-in, #lens-out");
    if (!btn) return;
    const wantsBigger = btn.id === "lens-in";
    const actuallyBigger = LENS.swapped ? !wantsBigger : wantsBigger;

    LENS.level = actuallyBigger ? 1 : -1;
    applyLens();
    if (window.Sound) actuallyBigger ? Sound.tick() : Sound.fail();

    // 用过一次，两面镜子的功能就换个个儿
    LENS.swapped = !LENS.swapped;
    lensLabels();

    const w = document.getElementById("lens-warn");
    if (w) w.innerHTML = bi("Controls remapped for your convenience.",
                            "已为你的便利重新映射控制键。");

    clearTimeout(H.lensTimer);
    if (actuallyBigger) {
      // 看得清？那就该挪位置了
      H.lensTimer = setTimeout(() => {
        LENS.level = 0; applyLens();
        shuffle();
        if (window.Sound) Sound.fail();
        if (window.log) log("Magnifier timed out. Layout refreshed.",
                            "放大镜已超时。版面已刷新。", "err");
      }, LENS_PATIENCE);
    }
  });

  /* ---------------- C5 广告关不掉，关一个长两个 ---------------- */
  document.addEventListener("click", e => {
    const x = e.target.closest(".promo-x");
    if (!x || !H.hostile) return;
    const promo = x.closest(".promo");
    const clone = promo.cloneNode(true);
    clone.classList.add("added");
    promo.after(clone);
    if (window.Sound) Sound.fail();
    if (window.log) log("Advertisement dismissed. Two replacements queued.",
                        "广告已关闭。两条替补已排队。", "warn");
  });

  /* ---------------- C10 报错袭击 + 震动袭击 ---------------- */
  const ERRORS = [
    ["AGENT_TASK_MISMATCH", "AG-17 is executing Task 6. Task 3 is unassigned.",
     "AG-17 正在执行任务 6。任务 3 无人认领。"],
    ["SCHEDULER_DEADLOCK", "Two agents are waiting for each other. Neither will yield.",
     "两个智能体在互相等待。谁都不肯让。"],
    ["WRITE_CONFLICT", "Assignment map written by 3 agents simultaneously.",
     "分配表被 3 个智能体同时写入。"],
    ["INTEGRITY_WARNING", "Operator edit detected. Reverting.", "检测到操作员修改。正在还原。"],
    ["QUOTA_EXCEEDED", "Free plan: manual reassignment is a Deluxe feature.",
     "免费套餐：手动重新分配属于豪华版功能。"],
    ["AGENT_UNRESPONSIVE", "AG-44 has entered a scheduled rest period.",
     "AG-44 已进入计划内休息时间。"],
    ["ROLLBACK_FAILED", "Rollback failed. Rolling forward instead.",
     "回滚失败。改为向前推进。"],
  ];

  let attacking = false;
  window.errorAttack = function () {
    if (attacking || !H.hostile) return;
    attacking = true;
    document.body.classList.add("quake");
    if (window.Sound) Sound.alarm();

    const stack = document.getElementById("errstack");
    let i = 0;
    const fire = setInterval(() => {
      const [code, en, cn] = ERRORS[i % ERRORS.length];
      const d = document.createElement("div");
      d.className = "errbox";
      d.innerHTML = `<b>${code}</b><span>${bi(en, cn)}</span>`;
      stack.appendChild(d);
      while (stack.children.length > 7) stack.firstChild.remove();
      if (window.Sound) Sound.fail();
      i++;
      if (i >= 9) {
        clearInterval(fire);
        setTimeout(() => {
          document.body.classList.remove("quake");
          stack.innerHTML = "";
          attacking = false;
          if (window.log) log("9 errors suppressed. Nothing was changed.",
                              "已抑制 9 条报错。什么都没有改变。", "err");
        }, 1400);
      }
    }, 260);
  };

  /* 想自己动手调整分工 → 触发袭击 */
  document.addEventListener("click", e => {
    if (!H.hostile) return;
    if (e.target.closest('[data-view="agents"]') || e.target.closest("#apply")) {
      setTimeout(window.errorAttack, 400);
    }
  });

  lensLabels();
})();
