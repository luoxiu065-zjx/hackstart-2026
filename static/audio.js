/* ORCHESTRA 声音引擎 —— 全部用 Web Audio 合成，不加载任何音频文件。
   离线可用，打包只有几 KB。                                          */

const Sound = (() => {
  let ctx = null, master = null, drone = null, muted = false;

  /* 浏览器建出来的 AudioContext 默认是 suspended，不 resume 就完全没声音。
     光在首次点击时 boot 还不够——上下文可能在没有手势的时候就被建出来了，
     之后一直挂着。所以每次发声前都确认一次。 */
  function ensure() {
    boot();
    if (ctx && ctx.state === "suspended") ctx.resume().catch(() => {});
    return ctx;
  }

  function boot() {                        // 浏览器要求先有用户交互
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain();
    master.gain.value = 0.35;
    master.connect(ctx.destination);
  }

  function noiseBuffer(sec = 1) {
    const n = ctx.sampleRate * sec;
    const b = ctx.createBuffer(1, n, ctx.sampleRate);
    const d = b.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    return b;
  }

  function beep(freq, dur = 0.07, type = "sine", vol = 0.25) {
    ensure();
    if (!ctx || muted) return;
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(0, ctx.currentTime);
    g.gain.linearRampToValueAtTime(vol, ctx.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
    o.connect(g); g.connect(master);
    o.start(); o.stop(ctx.currentTime + dur + 0.02);
  }

  /* ---------- 正常态：干净、克制、像贵软件 ---------- */
  const tick   = () => beep(1320, 0.05, "sine", 0.16);
  const done   = () => { beep(880, 0.07); setTimeout(() => beep(1320, 0.1), 70); };

  /* ---------- 混乱态：刺耳 ---------- */
  function fail() {
    ensure();
    if (!ctx || muted) return;
    beep(160, 0.18, "square", 0.3);
    setTimeout(() => beep(120, 0.26, "sawtooth", 0.28), 90);
  }

  function alarm() {
    ensure();
    if (!ctx || muted) return;
    let f = 700;
    for (let i = 0; i < 6; i++) {
      setTimeout(() => beep(f, 0.12, "square", 0.3), i * 150);
      f = f === 700 ? 520 : 700;
    }
  }

  /* 用户要「舒缓的音乐」时，给他这个 */
  function drill(seconds = 3.2) {
    ensure();
    if (!ctx || muted) return;
    const src = ctx.createBufferSource();
    src.buffer = noiseBuffer(seconds); src.loop = true;

    const bp = ctx.createBiquadFilter();
    bp.type = "bandpass"; bp.frequency.value = 1400; bp.Q.value = 2.5;

    const saw = ctx.createOscillator();
    saw.type = "sawtooth"; saw.frequency.value = 78;

    const gate = ctx.createGain();             // 一下一下的电钻节奏
    gate.gain.value = 0;
    const lfo = ctx.createOscillator(), lfoG = ctx.createGain();
    lfo.type = "square"; lfo.frequency.value = 11; lfoG.gain.value = 0.32;
    lfo.connect(lfoG); lfoG.connect(gate.gain);

    src.connect(bp); bp.connect(gate); saw.connect(gate); gate.connect(master);
    src.start(); saw.start(); lfo.start();
    const stop = ctx.currentTime + seconds;
    src.stop(stop); saw.stop(stop); lfo.stop(stop);
  }

  /* 混乱态的背景嗡鸣 */
  function droneOn() {
    ensure();
    if (!ctx || drone || muted) return;
    const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain();
    o1.type = "sawtooth"; o1.frequency.value = 55;
    o2.type = "sawtooth"; o2.frequency.value = 55.7;      // 失谐 → 不适感
    g.gain.value = 0; g.gain.linearRampToValueAtTime(0.07, ctx.currentTime + 1.2);
    o1.connect(g); o2.connect(g); g.connect(master);
    o1.start(); o2.start();
    drone = { o1, o2, g };
  }

  function droneOff() {
    if (!drone) return;
    const { o1, o2, g } = drone;
    g.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.5);
    setTimeout(() => { o1.stop(); o2.stop(); }, 600);
    drone = null;
  }

  function setMuted(v) {
    muted = v;
    if (master) master.gain.value = v ? 0 : 0.35;
    if (v) droneOff();
  }

  return { boot, ensure, tick, done, fail, alarm, drill, droneOn, droneOff, setMuted,
           get muted() { return muted; },
           get state() { return ctx ? ctx.state : "none"; } };
})();
