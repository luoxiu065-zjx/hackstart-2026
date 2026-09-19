"""把整条演示流程录成帧（英文版）。

和第一版的区别：应用切到纯英文，字幕也只有英文——给评委看的版本。
跑：  python capture_en.py   （需要本机 8001 在跑，且调试浏览器开着）
"""
import base64
import json
import pathlib
import sys
import time

sys.path.insert(0, r"D:\Projects\bg3-mods\tools")
import cdp  # noqa: E402

OUT = pathlib.Path(r"C:\Users\luoxi\AppData\Local\Temp\claude"
                   r"\C--Users-luoxi-Desktop\7a049107-9077-4501-8c20-950111cb6bfd"
                   r"\scratchpad\frames-en")
OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*"):
    f.unlink()

t = cdp.Tab("localhost:8001")
shots, n = [], 0


def shot(text, hold=1):
    global n
    for _ in range(hold):
        r = t.send("Page.captureScreenshot", format="png")
        (OUT / f"f{n:04d}.png").write_bytes(base64.b64decode(r["data"]))
        shots.append([n, text])
        n += 1


def english():
    """把界面切成纯英文。"""
    t.eval("(function(){ if (typeof LANG !== 'undefined') { LANG='en';"
           " if (window.applyLang) applyLang();"
           " if (window.renderStatic) renderStatic();"
           " if (window.renderProfiles) renderProfiles(lastStages);"
           " if (window.renderLanes) renderLanes(lastStages); } })()")


def cmd(text):
    t.eval("(function(){var i=document.getElementById('cmd');i.value=%r;"
           "i.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))})()" % text)


# ---------------------------------------------------------------- Act I
t.eval("fetch('/api/reset',{method:'POST'})")
t.send("Page.reload", ignoreCache=True)
time.sleep(4)
english()
shot("It asks for an account and a password. Masked, like everywhere else.", 6)
t.eval("document.getElementById('ob-user').value='zhongjiaxun@soton.ac.uk'")
t.eval("document.getElementById('ob-pass').value='********'")
shot("Every startup step opens the real source code that just ran.", 3)
t.eval("document.getElementById('ob-go').click()")
time.sleep(3.6)
english()
shot("Six steps. Nothing hidden.", 5)
t.eval("document.querySelector('.ob-view') && document.querySelector('.ob-view').click()")
time.sleep(1.2)
shot("app/pipeline.py:42 — the real function, not a hardcoded string.", 6)
t.eval("document.getElementById('ob-enter').click()")
time.sleep(1.5)
english()

# ---------------------------------------------------------------- Act II
shot("45 seconds of Deluxe trial. This is what it can do.", 4)
t.eval("document.getElementById('run').click()")
for _ in range(6):
    time.sleep(0.5)
    shot("Six agents, each in its own lane. All green.", 1)
time.sleep(2)
english()
shot("A real prep pack: real paper, real sections, real room.", 5)
t.eval("document.querySelector('[data-view=\"dashboard\"]').click()")
time.sleep(1.2)
english()
shot("Paid dashboard: no adverts, 13px body text, readable.", 6)

# ---------------------------------------------------------------- Act III
for _ in range(60):
    if t.eval("document.body.dataset.tier") != "trial":
        break
    time.sleep(1)
time.sleep(1.5)
english()
shot("The trial ends. No warning was sent.", 7)
t.eval("closePaywall && closePaywall()")
time.sleep(0.5)
english()
shot("Body text drops to 3.4px. The content is still there.", 6)
for i in range(3):
    btn = t.eval("document.getElementById('lens-in').textContent.indexOf('shrink')>-1"
                 " ? 'lens-out' : 'lens-in'")
    t.eval(f"document.getElementById('{btn}').click()")
    time.sleep(0.8)
    shot(f"Three correct clicks to become legible — the buttons swap after each one ({i+1}/3).", 3)
time.sleep(0.6)
shot("Legible. Two seconds later it moves everything.", 4)
time.sleep(2.6)
shot("Layout refreshed.", 3)

# ---------------------------------------------------------------- Act IV
cmd("play me some calm music")
time.sleep(4.5)
english()
shot("Ask for calm music. It plays a 140 dB industrial drill.", 6)
cmd("I want a burger")
time.sleep(4.5)
english()
shot("Ask for a burger. It orders plain penne, for nutritional balance.", 6)
t.eval("document.getElementById('run').click()")
time.sleep(11)
t.eval("closePaywall && closePaywall()")
t.eval("document.querySelector('[data-view=\"agents\"]').click()")
time.sleep(1)
t.eval("closePaywall && closePaywall()")
time.sleep(2.5)
english()
shot("Tasks change hands. Who took whose job, and why.", 7)
t.eval("document.getElementById('profiles').scrollIntoView({block:'start'})")
time.sleep(1)
english()
shot("Each agent still follows its own rules — on someone else's task.", 7)

# ---------------------------------------------------------------- Act V
t.eval("window.dispatchEvent(new CustomEvent('orchestra:cancel',{detail:{history:["
       "{text:'play me some calm music',at:new Date()},"
       "{text:'I want a burger',at:new Date()}]}}))")
time.sleep(3)
shot("The moment you try to cancel, it becomes perfect.", 6)
time.sleep(2.5)
shot("It replays every command it mangled, correctly.", 7)
time.sleep(3)
shot("Then the bribes: an email drafted to your real supervisor.", 7)
t.eval("document.querySelector('.q-skip') && document.querySelector('.q-skip').click()")
time.sleep(2)
shot("A planned week. Hover for what to do 2 days, 1 day, 2 hours ahead.", 7)
for i in range(3):
    t.eval("document.querySelector('.q-exit') && document.querySelector('.q-exit').click()")
    time.sleep(1.2)
    shot(f"'I still want to cancel' shrinks with every click ({i+1}/3).", 3)
time.sleep(1.5)
shot("It was never broken. It was priced.", 10)

json.dump(shots, open(OUT / "subs.json", "w", encoding="utf-8"), ensure_ascii=False)
print("TOTAL FRAMES", n)
