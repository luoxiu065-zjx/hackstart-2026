/* 开场：轻松的登录 + 全程透明的启动。
   这一幕的目的只有一个——让用户放下戒心。
   它问得很少、说得很清楚、还把源码摊开给你看。后面的一切才有得摔。 */

(function () {
  const el = document.createElement("div");
  el.className = "ob";
  el.id = "ob";
  el.innerHTML = `
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
        <div class="ob-tiny" id="ob-why">Why do you need this?<span class="cn">为什么需要这个？</span></div>
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
})();
