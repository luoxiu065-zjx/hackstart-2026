/* 给每个浏览器一个固定身份，所有 /api 请求都带上它。
   否则两个标签页共用一份服务器状态，会互相把对方的试用期重置掉。 */
(function () {
  let id;
  try {
    id = localStorage.getItem("orchestra-client");
    if (!id) {
      id = "c" + Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem("orchestra-client", id);
    }
  } catch { id = "c" + Math.random().toString(36).slice(2); }

  window.CLIENT_ID = id;

  const real = window.fetch;
  window.fetch = function (input, init) {
    const url = typeof input === "string" ? input : (input && input.url) || "";
    if (url.startsWith("/api/")) {
      init = init || {};
      init.headers = new Headers(init.headers || {});
      init.headers.set("X-Client", id);
    }
    return real(input, init);
  };
})();
