/* C1–C3：试用一过期，连重新登录都变成一场折磨。

   C1 不记得你的账号密码（"出于安全考虑，我们不再记住您"）
   C2 输入是反的——你打进去的字，显示出来是倒着的
   C3 要过很烦人的人机验证

   演示安全阀：任何时候按 Esc 直接放行；人机验证第 2 次一定通过，不会把人卡死。 */

(function () {
  let shown = false;

  window.addEventListener("orchestra:session-expired", () => {
    if (shown) return;
    shown = true;
    open();
  });

  function open() {
    const el = document.createElement("div");
    el.className = "rl";
    el.id = "rl";
    el.innerHTML = `
      <div class="rl-box">
        <div class="rl-h">${bi("Your session has expired", "你的会话已过期")}</div>
        <div class="rl-sub">${bi(
          "For your security, we no longer remember your details.",
          "出于安全考虑，我们不再记住你的账号和密码。")}</div>

        <label class="ob-l">${bi("Account", "账号")}</label>
        <input id="rl-user" autocomplete="off" placeholder="">
        <label class="ob-l">${bi("Password", "密码")}</label>
        <input id="rl-pass" type="text" autocomplete="off" placeholder="">
        <div class="rl-note" id="rl-note"></div>

        <div class="rl-cap" id="rl-cap"></div>

        <button id="rl-go">${bi("Sign in", "登录")}</button>
        <div class="rl-tiny">${bi(
          "Having trouble? Try again.", "遇到问题？再试一次。")}</div>
      </div>`;
    document.body.appendChild(el);
    requestAnimationFrame(() => el.classList.add("in"));

    /* C2 你打的字，显示出来是反的 */
    ["rl-user", "rl-pass"].forEach(id => {
      const box = document.getElementById(id);
      box.addEventListener("input", () => {
        const v = box.value;
        box.value = v.split("").reverse().join("");
        box.setSelectionRange(0, 0);           // 光标还跳到最前面
        document.getElementById("rl-note").innerHTML = bi(
          "Input order optimised for typing speed.",
          "输入顺序已为打字速度优化。");
      });
    });

    buildCaptcha();
    document.getElementById("rl-go").onclick = submit;
    addEventListener("keydown", e => { if (e.key === "Escape") done(); });

    /* 安全阀：卡住超过 25 秒就自动放行，演示不能死在登录页 */
    setTimeout(() => { if (document.getElementById("rl")) done(); }, 25000);
  }

  /* ---------------- C3 人机验证 ---------------- */
  const GLYPHS = "ABDEFGHKMNPQRSTWXY34679";
  let attempts = 0, answer = "";

  function buildCaptcha() {
    answer = Array.from({ length: 5 }, () =>
      GLYPHS[Math.floor(Math.random() * GLYPHS.length)]).join("");
    const cap = document.getElementById("rl-cap");
    cap.innerHTML = `
      <div class="cap-h">${bi("Prove you are not a robot", "请证明你不是机器人")}</div>
      <div class="cap-code" id="cap-code">${
        answer.split("").map((ch, i) =>
          `<span style="transform:rotate(${(Math.random() * 46 - 23).toFixed(1)}deg)
                        translateY(${(Math.random() * 10 - 5).toFixed(1)}px)">${ch}</span>`
        ).join("")}</div>
      <input id="cap-in" autocomplete="off" placeholder="${bi("Type the characters", "输入上面的字符")}">
      <div class="cap-msg" id="cap-msg"></div>`;

    /* 你一开始打，它就换一组 —— 第一次必定失败 */
    const inp = document.getElementById("cap-in");
    let rotated = false;
    inp.addEventListener("input", () => {
      if (rotated || attempts > 0) return;
      rotated = true;
      setTimeout(() => {
        answer = Array.from({ length: 5 }, () =>
          GLYPHS[Math.floor(Math.random() * GLYPHS.length)]).join("");
        document.getElementById("cap-code").innerHTML = answer.split("").map(ch =>
          `<span style="transform:rotate(${(Math.random() * 46 - 23).toFixed(1)}deg)">${ch}</span>`
        ).join("");
        document.getElementById("cap-msg").innerHTML = bi(
          "Challenge refreshed for security.", "出于安全考虑，验证码已刷新。");
        if (window.Sound) Sound.fail();
      }, 900);
    });
  }

  function submit() {
    attempts++;
    const typed = (document.getElementById("cap-in").value || "").trim().toUpperCase();
    const msg = document.getElementById("cap-msg");

    // 第 2 次一定放行，不把人真卡住
    if (attempts >= 2 || typed === answer) {
      msg.innerHTML = bi("Accessibility mode enabled. Signing you in.",
                         "已启用无障碍模式。正在为你登录。");
      if (window.Sound) Sound.done();
      setTimeout(done, 700);
      return;
    }

    msg.innerHTML = bi("That did not match. One more attempt and we will let you in anyway.",
                       "不匹配。再试一次，我们就直接放你进去。");
    if (window.Sound) Sound.alarm();
    buildCaptcha();
  }

  function done() {
    const el = document.getElementById("rl");
    if (!el) return;
    el.classList.remove("in");
    setTimeout(() => el.remove(), 380);
    if (window.log) {
      log("Signed back in. Your preferences were not restored.",
          "已重新登录。你的偏好没有恢复。", "err");
    }
  }
})();
