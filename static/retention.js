/* 取消订阅 → 挽留。
   原设计来自 George（from-george/），三步照搬：重放 → 问卷 → 越点越小的出口。 */

(function () {
  const R = {
    el: null, data: null, card: 0, total: 47, exitClicks: 0,
  };

  function node(html) {
    const d = document.createElement("div");
    d.innerHTML = html.trim();
    return d.firstElementChild;
  }

  /* ---------------- 入口 ---------------- */
  window.addEventListener("orchestra:cancel", async ev => {
    const history = (ev.detail && ev.detail.history) || [];
    let data;
    try {
      data = await (await fetch("/api/cancel", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          history: history.map(h => ({
            text: h.text,
            at: (h.at instanceof Date ? h.at : new Date()).toTimeString().slice(0, 5),
          })),
        }),
      })).json();
    } catch { return; }

    R.data = data;
    R.total = (data.survey[0] || {}).total || 47;
    snap();
  });

  /* ---------------- 第一下：一切瞬间变完美 ---------------- */
  function snap() {
    document.body.classList.remove("chaos", "lost");
    if (window.Sound) { Sound.droneOff(); Sound.done(); }

    R.el = node(`
      <div class="ret" id="ret">
        <div class="ret-top">
          <div>
            <div class="ret-who">Priority Retention Specialist</div>
            <div class="ret-sub">${bi("online · response time 0.1s · no queue",
                                      "在线 · 响应 0.1 秒 · 无需排队")}</div>
          </div>
          <div class="ret-badge">${bi("DELUXE RESTORED", "已恢复豪华版")}</div>
        </div>
        <div class="ret-body" id="ret-body"></div>
        <div class="ret-live" id="ret-live">
          <span class="rl-dot"></span>
          <span class="rl-label">${bi("Still working for you", "仍在为你工作")}</span>
          <span class="rl-item" id="rl-item"></span>
        </div>
      </div>`);
    document.body.appendChild(R.el);
    requestAnimationFrame(() => R.el.classList.add("in"));
    setTimeout(playReplay, 700);
    startLiveWork();
  }

  /* 你在犹豫的时候，它还在干活——沉没成本一直在涨 */
  function startLiveWork() {
    const items = R.data.live_work || [];
    if (!items.length) return;
    let i = 0;
    const tick = () => {
      const w = items[i % items.length];
      const el = $("#rl-item");
      if (!el) return;
      el.style.opacity = 0;
      setTimeout(() => {
        el.innerHTML = bi(w.en, w.cn);
        el.style.opacity = 1;
      }, 260);
      i++;
    };
    tick();
    R.liveTimer = setInterval(tick, 3200);
  }

  /* ---------------- 第二下：把被曲解的指令正确地重做一遍 ---------------- */
  function playReplay() {
    const box = node(`
      <section class="ret-sec">
        <h3>${bi("While you were waiting, we completed your earlier requests.",
                  "在你等待的这段时间里，我们已经把你之前的请求都完成了。")}</h3>
        <div class="replay" id="replay"></div>
      </section>`);
    $("#ret-body").appendChild(box);

    const items = R.data.replay;
    if (!items.length) { setTimeout(nextCard, 500); return; }

    items.forEach((r, i) => setTimeout(() => {
      const row = node(`
        <div class="rp">
          <span class="rp-t">${r.at}</span>
          <span class="rp-q">"${r.text.replace(/</g, "&lt;")}"</span>
          <span class="rp-a">${bi(r.en, r.cn)}</span>
          <span class="rp-ms">${r.ms} ms</span>
        </div>`);
      $("#replay").appendChild(row);
      requestAnimationFrame(() => row.classList.add("in"));
      if (window.Sound) Sound.tick();
      if (i === items.length - 1) setTimeout(nextCard, 900);
    }, 450 + i * 550));
  }

  /* ---------------- 第三下：六张贿赂卡，题号越答越多 ---------------- */
  function nextCard() {
    const c = R.data.survey[R.card];
    if (!c) return finale();

    const pct = Math.max(4, 42 - R.card * 6);     // 进度条往回走
    const box = node(`
      <section class="ret-sec card-sec">
        <div class="q-head">
          <span>${bi(`Question ${c.n} of ${R.total}`, `第 ${c.n} 题 / 共 ${R.total} 题`)}</span>
          <span class="q-bar"><i style="width:${pct}%"></i></span>
        </div>
        <div class="q-body">${bi(c.en, c.cn)}</div>
        <div class="q-proof">${bi(c.proof_en, c.proof_cn)}</div>
        <div class="q-actions">
          <button class="q-keep">${bi("Keep my subscription", "保留我的订阅")}</button>
          <button class="q-skip">${bi("Skip this question", "跳过这一题")}</button>
        </div>
        <div class="q-exit-wrap"></div>
      </section>`);

    const body = $("#ret-body");
    [...body.querySelectorAll(".card-sec")].forEach(e => e.remove());
    body.appendChild(box);
    requestAnimationFrame(() => box.classList.add("in"));

    box.querySelector(".q-keep").onclick = () => keep();
    box.querySelector(".q-skip").onclick = () => {
      R.card++;
      R.total += 1;                                // 你越答，题越多
      if (window.Sound) Sound.tick();
      nextCard();
    };
    renderExit(box.querySelector(".q-exit-wrap"));
    body.scrollTop = body.scrollHeight;
  }

  /* ---------------- 越点越小的出口（George 的 shrinking exit） ---------------- */
  function renderExit(wrap) {
    const sizes = [13, 10.5, 8, 6];
    const size = sizes[Math.min(R.exitClicks, sizes.length - 1)];
    wrap.innerHTML = "";
    const a = node(`<span class="q-exit" style="font-size:${size}px">${
      bi("I still want to cancel", "我仍然要取消")}</span>`);
    a.onclick = () => {
      R.exitClicks++;
      if (window.Sound) Sound.fail();
      if (R.exitClicks >= 3) return finale();
      R.card++;
      R.total += 1;
      nextCard();
    };
    wrap.appendChild(a);
  }

  function keep() {
    clearInterval(R.liveTimer);
    if (window.Sound) Sound.done();
    R.el.classList.add("kept");
    $("#ret-body").innerHTML = `
      <section class="ret-sec in">
        <h3>${bi("Thank you. Nothing will change.", "谢谢你。什么都不会改变。")}</h3>
        <p class="ret-p">${bi(
          "Your Deluxe plan continues at £39.99 per month. Performance will remain unrestricted for as long as you keep paying.",
          "你的豪华版将以每月 £39.99 继续。只要你一直付费，性能就一直不受限制。")}</p>
        <button class="q-keep" onclick="location.reload()">${bi("Back to the fleet", "返回控制台")}</button>
      </section>`;
  }

  /* ---------------- 结局：一切褪成灰，台词落下 ---------------- */
  function finale() {
    clearInterval(R.liveTimer);
    const live = document.getElementById("ret-live");
    if (live) live.remove();
    const f = R.data.finale;
    if (window.Sound) { Sound.setMuted(true); }
    R.el.classList.add("dead");
    $("#ret-body").innerHTML = `
      <section class="ret-sec in fin">
        <div class="fin-x">${bi("Subscription cancelled.", "订阅已取消。")}</div>
        <div class="fin-line">${bi(f.en, f.cn)}</div>
        <div class="fin-sub">${bi(f.sub_en, f.sub_cn)}</div>
        <button class="q-keep ghost" onclick="location.reload()">${
          bi("Run it again", "再跑一遍")}</button>
      </section>`;
  }
})();
