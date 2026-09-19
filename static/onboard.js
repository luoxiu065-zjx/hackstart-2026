/* 开场：轻松的登录 + 全程透明的启动。
   这一幕的目的只有一个——让用户放下戒心。
   它问得很少、说得很清楚、还把源码摊开给你看。后面的一切才有得摔。 */

(function () {
  const el = document.createElement("div");
  el.className = "ob";
  el.id = "ob";
  el.innerHTML = `
      <canvas class="ob-bg" id="ob-bg"></canvas>
    <div class="ob-box" id="ob-box">
      <div class="ob-logo">ORCHESTRA<span>▸</span></div>

      <!-- A. 登录 -->
      <div class="ob-step" id="ob-signin">
        <div class="ob-h">Sign in<span class="cn">登录</span></div>
        <label class="ob-l">Account<span class="cn">账号</span></label>
        <input id="ob-user" autocomplete="off" placeholder="you@soton.ac.uk">
        <label class="ob-l">Password<span class="cn">密码</span></label>
        <input id="ob-pass" type="password" placeholder="••••••••">
        <div class="ob-note">
          Masked on screen, like everywhere else.
          <span class="cn">屏幕上打码，跟你平常用的一样。</span>
        </div>
        <button id="ob-go">Continue<span class="cn">继续</span></button>
        <div class="ob-links">
          <span class="ob-tiny" id="ob-why">Why do you need this?<span class="cn">为什么需要这个？</span></span>
          <a class="ob-tiny ob-about" href="/about" target="_blank" rel="noopener">What is this?<span class="cn">这是什么？</span></a>
        </div>
        <div class="ob-why-body" id="ob-why-body" hidden>
          To read your own timetable feed and coursework pages. Nothing is uploaded.
          <span class="cn">用来读你自己的课表订阅和作业页面。不会上传任何东西。</span>
        </div>
      </div>

      <!-- B. 透明启动 -->
      <div class="ob-step" id="ob-boot" hidden>
        <div class="ob-h">Setting up<span class="cn">正在准备</span></div>
        <div class="ob-who" id="ob-who"></div>
        <div class="ob-steps" id="ob-steps"></div>
        <pre class="ob-code" id="ob-code" hidden></pre>
        <button id="ob-enter" hidden>Enter ORCHESTRA<span class="cn">进入</span></button>
      </div>
    </div>`;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add("in"));

  /* ---- 动态背景：水墨晕染 + 金尘。全部现画，不下载任何图片。 ----
     注意：这里必须用 var，而且 startBackdrop() 要放在文件末尾调用。
     之前写成「先调用、后 let 声明」，触发 TDZ 报错，整个脚本后面的
     事件绑定全被跳过——登录按钮点了没反应就是这么来的。 */
  var bgRAF = null;
  function startBackdrop() {
    const cv = document.getElementById("ob-bg");
    if (!cv) return;
    const ctx = cv.getContext("2d");
    let W, H, dust = [], blobs = [];

    function size() {
      W = cv.width = innerWidth * devicePixelRatio;
      H = cv.height = innerHeight * devicePixelRatio;
      cv.style.width = innerWidth + "px";
      cv.style.height = innerHeight + "px";
    }
    size();
    addEventListener("resize", size);

    // 三团慢慢游动的墨
    blobs = [
      { x: .22, y: .28, r: .46, hue: "168,96,79",  a: .16, sx: .000045, sy: .000031 },
      { x: .78, y: .18, r: .40, hue: "201,163,106", a: .13, sx: -.000037, sy: .000043 },
      { x: .55, y: .82, r: .52, hue: "70,86,140",   a: .14, sx: .000029, sy: -.000035 },
    ];
    // 金尘
    for (let i = 0; i < 70; i++) {
      dust.push({
        x: Math.random(), y: Math.random(),
        r: (Math.random() * 1.5 + .5) * devicePixelRatio,
        v: Math.random() * .000055 + .000018,
        drift: (Math.random() - .5) * .00004,
        ph: Math.random() * 6.28,
      });
    }

    let t0 = performance.now();
    function frame(now) {
      const dt = now - t0; t0 = now;
      ctx.clearRect(0, 0, W, H);

      blobs.forEach(b => {
        b.x += b.sx * dt; b.y += b.sy * dt;
        if (b.x < .12 || b.x > .88) b.sx *= -1;
        if (b.y < .10 || b.y > .90) b.sy *= -1;
        const g = ctx.createRadialGradient(b.x * W, b.y * H, 0, b.x * W, b.y * H, b.r * W);
        g.addColorStop(0, `rgba(${b.hue},${b.a})`);
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, W, H);
      });

      dust.forEach(d => {
        d.y -= d.v * dt; d.x += d.drift * dt; d.ph += dt * .0016;
        if (d.y < -.02) { d.y = 1.02; d.x = Math.random(); }
        const tw = .35 + .65 * Math.abs(Math.sin(d.ph));
        ctx.beginPath();
        ctx.arc(d.x * W, d.y * H, d.r, 0, 6.2832);
        ctx.fillStyle = `rgba(201,163,106,${.42 * tw})`;
        ctx.fill();
      });

      bgRAF = requestAnimationFrame(frame);
    }
    bgRAF = requestAnimationFrame(frame);
  }

  const $$$ = id => document.getElementById(id);

  $$$("ob-why").onclick = () => {
    const b = $$$("ob-why-body");
    b.hidden = !b.hidden;
  };

  /* ---- 打码：就像平常那样 ---- */
  function maskAccount(v) {
    v = (v || "").trim() || "xiujosh@soton.ac.uk";
    const [name, domain] = v.includes("@") ? v.split("@") : [v, "soton.ac.uk"];
    const head = name.slice(0, 1), tail = name.slice(-1);
    return `${head}${"*".repeat(Math.max(3, name.length - 2))}${tail}@${domain}`;
  }

  $$$("ob-go").onclick = () => {
    const acct = maskAccount($$$("ob-user").value);
    $$$("ob-signin").hidden = true;
    $$$("ob-boot").hidden = false;
    $$$("ob-who").innerHTML =
      `Signed in as <b>${acct}</b> · password not stored`
      + `<span class="cn">已登录 <b>${acct}</b> · 密码未保存</span>`;
    boot();
  };

  /* ---- 透明启动：每一步都可以点开看真实源码 ---- */
  async function boot() {
    let steps = [];
    try {
      steps = (await (await fetch("/api/manifest")).json()).steps;
    } catch {
      $$$("ob-enter").hidden = false;
      return;
    }

    const box = $$$("ob-steps");
    steps.forEach((s, i) => setTimeout(async () => {
      const row = document.createElement("div");
      row.className = "ob-row";
      row.innerHTML = `
        <span class="ob-tick">✓</span>
        <span class="ob-what">${s.en}<span class="cn">${s.cn}</span></span>
        <span class="ob-src">${s.src_en}</span>
        <span class="ob-view" data-stage="${s.id}">view code<span class="cn">看代码</span></span>`;
      box.appendChild(row);
      requestAnimationFrame(() => row.classList.add("in"));
      if (window.Sound) Sound.tick();

      row.querySelector(".ob-view").onclick = async e => {
        const pre = $$$("ob-code");
        const src = await (await fetch("/api/source?stage=" + e.currentTarget.dataset.stage)).json();
        if (src.error) return;
        pre.hidden = false;
        pre.textContent = `# ${src.file}:${src.line}  （${src.lines} 行，就是刚才跑的那段）\n\n${src.code}`;
        pre.scrollIntoView({ behavior: "smooth", block: "nearest" });
      };

      if (i === steps.length - 1) {
        setTimeout(() => {
          $$$("ob-enter").hidden = false;
          if (window.Sound) Sound.done();
        }, 500);
      }
    }, 350 + i * 420));
  }

  async function enter() {
    if (bgRAF) cancelAnimationFrame(bgRAF);
    /* 试用期从进入的那一刻才开始算，别烧在登录上 */
    try { await fetch("/api/reset", { method: "POST" }); } catch {}
    el.classList.remove("in");
    setTimeout(() => el.remove(), 450);
    if (window.log) {
      log("Deluxe trial activated. Everything is unlocked.",
          "豪华版试用已激活。全部功能解锁。", "ok");
    }
  }
  $$$("ob-enter").onclick = enter;

  /* 演示时要反复重来，留个快捷键：Esc 直接跳过开场 */
  addEventListener("keydown", e => {
    if (e.key === "Escape" && document.getElementById("ob")) enter();
  });

  /* 回车即继续 */
  ["ob-user", "ob-pass"].forEach(id => $$$(id).addEventListener("keydown", e => {
    if (e.key === "Enter") $$$("ob-go").click();
  }));

  /* 所有交互都绑好了，最后才开背景动画 */
  startBackdrop();
})();
