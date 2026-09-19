/* 正例：付费版的「今日」。
   数据全部来自真实课表和真实预习包，一个字都不是编的。
   设计上刻意跟混乱版反着来：衬线标题、大留白、暖色、字大到能读。 */

(function () {
  const MONTH = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
                 "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"];
  const WD_EN = { "周一":"MONDAY","周二":"TUESDAY","周三":"WEDNESDAY","周四":"THURSDAY",
                  "周五":"FRIDAY","周六":"SATURDAY","周日":"SUNDAY" };
  const done = new Set();

  let PACKS = [];
  const actionOf = code => (PACKS.find(p => p.code === code) || {}).first_action || "";

  async function render() {
    let today, packs;
    try {
      today = await (await fetch("/api/hub/today")).json();
      packs = (await (await fetch("/api/hub/prep")).json()).packs;
      PACKS = packs;
    } catch { return; }

    const d = new Date(today.date + "T00:00:00");
    document.getElementById("dx-day").textContent = d.getDate();
    document.getElementById("dx-wd").textContent  = WD_EN[today.weekday] || today.weekday;
    document.getElementById("dx-mon").textContent = MONTH[d.getMonth()];

    const items = today.bands.flatMap(b => b.items);
    const first = items[0];

    document.getElementById("dx-kicker").innerHTML =
      bi(today.looking_ahead ? "NEXT TEACHING DAY" : "TODAY",
         today.looking_ahead ? "下一个有课的日子" : "今天");

    document.getElementById("dx-h").innerHTML = first
      ? bi(`${items.length} sessions. First one is ${first.code} at ${first.time}.`,
           `${items.length} 节课。第一节是 ${first.code}，${first.time}。`)
      : bi("Nothing scheduled.", "今天没有安排。");

    document.getElementById("dx-sub").innerHTML = first
      ? bi(`${first.lecturer} teaches it in ${first.location}. `
         + `Your prep pack is written and waiting — about 40 minutes of reading.`,
           `${first.lecturer} 上这节课，教室 ${first.location}。`
         + `预习包已经写好在等你了，大约 40 分钟的阅读量。`)
      : bi("Use the time.", "把时间用掉。");

    /* ---- 时间轴：时间段 + 重要度，不写「9 点做什么」 ---- */
    document.getElementById("dx-timeline").innerHTML = today.bands.map(b => `
      <div class="dx-band">
        <div class="dx-band-h">
          <b>${bi(b.label === "上午" ? "Morning" : b.label === "下午" ? "Afternoon" : "Evening",
                  b.label)}</b>
          <i></i>
          <em>${b.items.length ? b.items.length + (LANG === "cn" ? " 项" : " sessions") : ""}</em>
        </div>
        ${b.items.length ? b.items.map(it => `
          <div class="dx-item ${it.weight}">
            <div class="dx-time">${it.time}<small>${it.end || ""}</small></div>
            <div class="dx-dot"></div>
            <div>
              <div class="dx-name">${it.title}</div>
              <div class="dx-meta">${it.code} · ${it.location}<br>
                <b>${it.lecturer}</b>${it.assessment ? " · " + it.assessment : ""}</div>
              ${actionOf(it.code) ? `<div class="dx-why">
                  <span style="color:#6d7ca4">${bi("Before this:", "课前该做：")}</span>
                  ${actionOf(it.code)}</div>` : ""}
            </div>
          </div>`).join("")
        : `<div class="dx-empty">${bi(b.note, b.note)}</div>`}
      </div>`).join("");

    /* ---- 右栏：预习进度 ---- */
    document.getElementById("dx-prep").innerHTML = `
      <h4>${bi("PREP PACKS READY", "预习包已就绪")}</h4>
      ${packs.map(p => `
        <div class="dx-prep-item${done.has(p.code) ? " done" : ""}" data-code="${p.code}">
          <span class="dx-check${done.has(p.code) ? " on" : ""}">${done.has(p.code) ? "✓" : ""}</span>
          <span><b>${p.code}</b> · ${LANG === "cn" ? "第 " + p.week + " 周" : "week " + p.week}<br>
                <span style="color:#6d7ca4">${p.lecturer}</span></span>
        </div>`).join("")}`;

    document.querySelectorAll(".dx-prep-item").forEach(el => el.onclick = () => {
      const c = el.dataset.code;
      done.has(c) ? done.delete(c) : done.add(c);
      if (window.Sound) Sound.tick();
      render();
    });

    document.getElementById("dx-prov").innerHTML = `
      <p>${bi(
        `Built from <b>${today.counts.sessions}</b> sessions in your own timetable feed, `
        + `<b>${packs.length}</b> prep packs and your supervisors' published research. `
        + `No adverts. Nothing sold. Nothing hidden.`,
        `由你自己的课表订阅里的 <b>${today.counts.sessions}</b> 个时段、`
        + `<b>${packs.length}</b> 份预习包和你导师们公开发表的研究整理而成。`
        + `没有广告，不卖任何东西，不藏任何东西。`)}</p>`;
  }

  window.renderDeluxe = render;
  render();
  setInterval(() => { if (!document.body.classList.contains("hostile")) render(); }, 60000);
})();
