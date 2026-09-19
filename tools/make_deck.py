"""生成英文版演讲 PPT。

  python tools/make_deck.py

设计沿用产品自己的语言：墨底、金色、Playfair 标题、思源黑体正文、极低对比。
截图直接用英文版录制的帧（frames-en），所以片子里没有一个中文字。
"""
import pathlib
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

SCRATCH = pathlib.Path(
    r"C:\Users\luoxi\AppData\Local\Temp\claude"
    r"\C--Users-luoxi-Desktop\7a049107-9077-4501-8c20-950111cb6bfd\scratchpad")
FRAMES = SCRATCH / "frames-en"
OUT = pathlib.Path(r"C:\Users\luoxi\Desktop\claude图片文档专用\文档\ORCHESTRA-Pitch-EN-v2.pptx")

INK = RGBColor(0x0B, 0x0C, 0x13)
PANEL = RGBColor(0x14, 0x15, 0x1F)
FG = RGBColor(0xE8, 0xE6, 0xEF)
DIM = RGBColor(0x9A, 0x97, 0xAD)
FAINT = RGBColor(0x5F, 0x5D, 0x73)
GOLD = RGBColor(0xC9, 0xA3, 0x6A)
CLAY = RGBColor(0xA8, 0x60, 0x4F)
GREEN = RGBColor(0x5F, 0xBF, 0x95)

DISPLAY = "Georgia"          # Playfair 不一定装了，Georgia 是同一路子且到处都有
BODY = "Segoe UI"
MONO = "Consolas"

W, H = Inches(13.333), Inches(7.5)


def frame(i: int) -> pathlib.Path | None:
    p = FRAMES / f"f{i:04d}.png"
    return p if p.exists() else None


def deck() -> Presentation:
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    return prs


def blank(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = INK
    return s


def text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, spacing=1.0):
    """runs: [(文本, 字号, 颜色, 粗体, 字体, 段前间距)]"""
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, (t, size, color, bold, font, space_before) in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        if space_before:
            p.space_before = Pt(space_before)
        r = p.add_run()
        r.text = t
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold
        r.font.name = font
    return box


def eyebrow(slide, t, y=Inches(0.62)):
    text(slide, Inches(0.9), y, Inches(11), Inches(0.3),
         [(t.upper(), 11, GOLD, False, MONO, 0)])


def rule(slide, y):
    line = slide.shapes.add_shape(1, Inches(0.9), y, Inches(11.5), Emu(9525))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0x26, 0x27, 0x33)
    line.line.fill.background()
    line.shadow.inherit = False


def picture(slide, img, x, y, w):
    if img and img.exists():
        slide.shapes.add_picture(str(img), x, y, width=w)


def stat_row(slide, y, items):
    """大数字一排。items: [(数字, 标签)]"""
    n = len(items)
    if not n:
        return
    gap = Inches(0.25)
    total = Inches(11.5)
    cw = int((total - gap * (n - 1)) / n)
    for i, (num, label) in enumerate(items):
        x = Inches(0.9) + i * (cw + gap)
        card = slide.shapes.add_shape(1, x, y, cw, Inches(1.5))
        card.fill.solid()
        card.fill.fore_color.rgb = PANEL
        card.line.color.rgb = RGBColor(0x22, 0x23, 0x30)
        card.shadow.inherit = False
        text(slide, x + Inches(0.3), y + Inches(0.26), cw - Inches(0.6), Inches(1.0),
             [(num, 40, GOLD, False, DISPLAY, 0),
              (label, 11, FAINT, False, MONO, 6)])



def bar(slide, x, y, w, h, frac, color, label, value, sub=None):
    """一根横条 + 数值。frac 是占满宽度的比例（0-1）。"""
    track = slide.shapes.add_shape(1, x, y, w, h)
    track.fill.solid(); track.fill.fore_color.rgb = RGBColor(0x1C, 0x1D, 0x29)
    track.line.fill.background(); track.shadow.inherit = False
    fill_w = max(int(w * frac), Inches(0.06))
    fg = slide.shapes.add_shape(1, x, y, fill_w, h)
    fg.fill.solid(); fg.fill.fore_color.rgb = color
    fg.line.fill.background(); fg.shadow.inherit = False
    text(slide, x, y - Inches(0.34), w, Inches(0.3),
         [(label, 12, DIM, False, BODY, 0)])
    text(slide, x + w + Inches(0.18), y - Inches(0.12), Inches(2.2), Inches(0.5),
         [(value, 19, color, False, DISPLAY, 0)])
    if sub:
        text(slide, x + w + Inches(0.18), y + Inches(0.26), Inches(2.4), Inches(0.3),
             [(sub, 10, FAINT, False, MONO, 0)])


def column(slide, x, y, w, head, items, accent):
    """总结页的一栏。"""
    text(slide, x, y, w, Inches(0.4), [(head.upper(), 11, accent, False, MONO, 0)])
    line = slide.shapes.add_shape(1, x, y + Inches(0.34), w, Emu(9525))
    line.fill.solid(); line.fill.fore_color.rgb = RGBColor(0x2A, 0x2B, 0x38)
    line.line.fill.background(); line.shadow.inherit = False
    runs = []
    for i, (bold_part, rest) in enumerate(items):
        runs.append((bold_part, 12, FG, False, BODY, 0 if i == 0 else 11))
        runs.append((rest, 11, DIM, False, BODY, 1))
    text(slide, x, y + Inches(0.6), w, Inches(4.6), runs, spacing=1.25)


def build():
    prs = deck()

    # ---------- 1 封面 ----------
    s = blank(prs)
    eyebrow(s, "HackStart 2026  ·  Stubborn Software", Inches(0.9))
    text(s, Inches(0.9), Inches(1.7), Inches(11.5), Inches(2.4),
         [("ORCHESTRA", 80, FG, False, DISPLAY, 0)])
    text(s, Inches(0.9), Inches(3.5), Inches(8.6), Inches(1.6),
         [("A study assistant that is excellent when you pay,", 26, GOLD, False, DISPLAY, 0),
          ("and hostile when you don't.", 26, GOLD, False, DISPLAY, 0)], spacing=1.2)
    rule(s, Inches(5.5))
    text(s, Inches(0.9), Inches(5.8), Inches(11.5), Inches(0.6),
         [("Jiaxun Zhong  ·  MSc Artificial Intelligence  ·  built in one day", 13, FAINT, False, MONO, 0)])

    # ---------- 2 前提 ----------
    s = blank(prs)
    eyebrow(s, "The premise")
    text(s, Inches(0.9), Inches(1.25), Inches(11.2), Inches(1.4),
         [("The brief asked for annoying software.", 34, FG, False, DISPLAY, 0),
          ("I asked why software would actually do it.", 34, GOLD, False, DISPLAY, 0)], spacing=1.15)
    rule(s, Inches(3.05))
    text(s, Inches(0.9), Inches(3.4), Inches(5.3), Inches(3),
         [("The examples in the brief were each one annoying feature.", 15, DIM, False, BODY, 0),
          ("ORCHESTRA is a working product whose degradation is a "
           "pricing decision — not a bug, not a joke.", 15, DIM, False, BODY, 10)], spacing=1.4)
    text(s, Inches(6.9), Inches(3.4), Inches(5.5), Inches(3),
         [("The answer is not that it is broken.", 19, FG, False, DISPLAY, 0),
          ("The answer is money.", 19, CLAY, False, DISPLAY, 8)], spacing=1.3)

    # ---------- 3 这些是真的 ----------
    s = blank(prs)
    eyebrow(s, "None of this is invented")
    text(s, Inches(0.9), Inches(1.25), Inches(11.2), Inches(1.1),
         [("Every pattern in this demo already ships.", 34, FG, False, DISPLAY, 0)])
    rule(s, Inches(2.5))
    rows = [
        ("Support you cannot reach", "until you say the word \"cancel\""),
        ("Retention offers", "that appear the second you try to leave"),
        ("Cancellation flows", "buried three clicks deep in grey text"),
        ("Legibility as a lever", "the information is there — at 3.4 pixels"),
    ]
    y = Inches(2.9)
    for a, b in rows:
        text(s, Inches(0.9), y, Inches(4.2), Inches(0.5), [(a, 17, FG, False, BODY, 0)])
        text(s, Inches(5.4), y + Inches(0.05), Inches(7), Inches(0.5),
             [(b, 14, DIM, False, BODY, 0)])
        y += Inches(0.82)
    text(s, Inches(0.9), Inches(6.3), Inches(11.4), Inches(0.8),
         [("They have a name — dark patterns — and regulators in the EU and the UK "
           "are actively legislating against them.", 14, GOLD, False, BODY, 0)])

    # ---------- 4 商业模式（核心） ----------
    s = blank(prs)
    eyebrow(s, "The business model")
    text(s, Inches(0.9), Inches(1.2), Inches(11.2), Inches(1.0),
         [("The punchline is in the footnotes.", 34, FG, False, DISPLAY, 0)])
    tiers = [
        ("FREE", "£0", "Core features, best-effort scheduling.",
         "Performance is not guaranteed on the Free plan.", DIM),
        ("BASIC", "£9.99 / mo", "Reduced interruptions.*",
         "*Around 10 interruptions per month. Three of them total 120 hours. "
         "Interruptions are a feature of the Basic plan.", GOLD),
        ("DELUXE", "£39.99 / mo", "Interruption-free operation.**",
         "**Excludes scheduled interruptions, maintenance interruptions, and "
         "interruptions arising from user input.", CLAY),
    ]
    cw, gap = Inches(3.63), Inches(0.31)
    for i, (name, price, promise, fine, accent) in enumerate(tiers):
        x = Inches(0.9) + i * (cw + gap)
        card = s.shapes.add_shape(1, x, Inches(2.6), cw, Inches(3.6))
        card.fill.solid()
        card.fill.fore_color.rgb = PANEL
        card.line.color.rgb = RGBColor(0x2A, 0x2B, 0x38) if i != 1 else GOLD
        card.shadow.inherit = False
        text(s, x + Inches(0.32), Inches(2.9), cw - Inches(0.64), Inches(3.1),
             [(name, 11, FAINT, False, MONO, 0),
              (price, 26, FG, False, DISPLAY, 6),
              (promise, 14, FG, False, BODY, 12),
              (fine, 11, accent, False, BODY, 14)], spacing=1.35)
    text(s, Inches(0.9), Inches(6.5), Inches(11.4), Inches(0.5),
         [("Ten interruptions a month. Three of them are five days long.", 15, GOLD, False, BODY, 0)])


    # ---------- 数字图 ----------
    s = blank(prs)
    eyebrow(s, "The same product, two price points")
    text(s, Inches(0.9), Inches(1.2), Inches(11.2), Inches(1.0),
         [("Degradation you can measure.", 34, FG, False, DISPLAY, 0)])

    bar(s, Inches(0.9), Inches(2.75), Inches(6.4), Inches(0.42), 1.0, GOLD,
        "Body text you are allowed to read — Deluxe", "13 px")
    bar(s, Inches(0.9), Inches(3.75), Inches(6.4), Inches(0.42), 0.26, CLAY,
        "Body text you are allowed to read — Free", "3.4 px", "same content, still there")

    bar(s, Inches(0.9), Inches(5.0), Inches(6.4), Inches(0.42), 0.024, GOLD,
        "Response time — Deluxe", "0.2 s")
    bar(s, Inches(0.9), Inches(5.65), Inches(6.4), Inches(0.42), 0.37, DIM,
        "Response time — Basic", "3.1 s")
    bar(s, Inches(0.9), Inches(6.3), Inches(6.4), Inches(0.42), 1.0, CLAY,
        "Response time — Free", "8.4 s")

    box = s.shapes.add_shape(1, Inches(9.1), Inches(2.6), Inches(3.3), Inches(4.15))
    box.fill.solid(); box.fill.fore_color.rgb = PANEL
    box.line.color.rgb = RGBColor(0x2A, 0x2B, 0x38); box.shadow.inherit = False
    text(s, Inches(9.4), Inches(2.95), Inches(2.8), Inches(3.6),
         [("BASIC PLAN", 10, FAINT, False, MONO, 0),
          ("10", 46, GOLD, False, DISPLAY, 8),
          ("interruptions a month", 12, DIM, False, BODY, 0),
          ("120", 46, CLAY, False, DISPLAY, 16),
          ("hours — just three of them", 12, DIM, False, BODY, 0),
          ("Five days. Sold as a feature.", 11, CLAY, False, BODY, 14)], spacing=1.15)

    # ---------- 总结：反人类设计清单 ----------
    s = blank(prs)
    eyebrow(s, "Where the hostility actually lives")
    text(s, Inches(0.9), Inches(1.1), Inches(11.2), Inches(0.9),
         [("Nothing here is a bug. Each one is a decision.", 32, FG, False, DISPLAY, 0)])

    design = [
        ("Illegibility as a lever. ", "The timetable is still there — at 3.4 px."),
        ("The magnifier lies by swapping. ", "Three correct clicks, and the buttons trade roles after each."),
        ("Moving targets. ", "Content changes position every 30 seconds."),
        ("Adverts take the space. ", "Close one and it clones itself."),
        ("The exit is 9.5 px of grey. ", "Three clicks deep, and it shrinks as you click."),
        ("Progress that runs backwards. ", "Question 3 of 47 becomes 3 of 49."),
    ]
    language = [
        ("“Optimising legibility.” ", "Said while making the text smaller."),
        ("“Re-optimised.” ", "The word for an agent doing the wrong job."),
        ("“Your preference was overridden ", "for nutritional balance.”"),
        ("Footnotes that cancel the promise. ", "“Excludes interruptions arising from user input.”"),
        ("“Interruptions are a feature ", "of the Basic plan.”"),
        ("Politeness decays. ", "Certainly → Sure → Fine → Again? → (read)"),
    ]
    behaviour = [
        ("No warning before the drop. ", "The product says so, out loud, afterwards."),
        ("Free always degrades. ", "Written in the code, not left to chance."),
        ("Work is reassigned mid-run. ", "Each agent applies its own rules to someone else’s task."),
        ("Trying to fix it is punished. ", "Nine errors, a shaking screen, and nothing changed."),
        ("Paying forgives tampering. ", "The integrity flag is cleared on upgrade."),
        ("Cancelling makes it perfect. ", "Then it replays what it understood all along."),
    ]
    column(s, Inches(0.9), Inches(2.35), Inches(3.5), "Design", design, GOLD)
    column(s, Inches(4.85), Inches(2.35), Inches(3.5), "Language", language, DIM)
    column(s, Inches(8.8), Inches(2.35), Inches(3.5), "Behaviour", behaviour, CLAY)

    text(s, Inches(0.9), Inches(6.95), Inches(11.4), Inches(0.5),
         [("Eighteen patterns. Every one of them copied from software that ships today.",
           14, GOLD, False, BODY, 0)])

    # ---------- 技术 ----------
    # ---------- 5 技术 ----------
    s = blank(prs)
    eyebrow(s, "How it is built")
    text(s, Inches(0.9), Inches(1.2), Inches(11.2), Inches(1.0),
         [("Nothing it needs is on the internet.", 34, FG, False, DISPLAY, 0)])
    rule(s, Inches(2.35))
    text(s, Inches(0.9), Inches(2.7), Inches(5.4), Inches(3.4),
         [("Python and FastAPI on the back, plain HTML and JavaScript on the front — "
           "no build step.", 15, DIM, False, BODY, 0),
          ("Sound is synthesised with Web Audio, so no audio file is ever loaded. "
           "The login background is drawn on a canvas, not downloaded.", 15, DIM, False, BODY, 10),
          ("A language model drives the two personalities; a rule engine takes over the "
           "instant it times out — bad wifi cannot break the demo.", 15, GOLD, False, BODY, 10)],
         spacing=1.42)
    items = [("21", "TESTS PASSING"), ("120", "CONCURRENT REQUESTS"),
             ("110", "THROTTLED"), ("0", "ERRORS")]
    for i, (num, label) in enumerate(items):
        x = Inches(6.9) + (i % 2) * Inches(2.85)
        y = Inches(2.7) + (i // 2) * Inches(1.75)
        card = s.shapes.add_shape(1, x, y, Inches(2.6), Inches(1.5))
        card.fill.solid()
        card.fill.fore_color.rgb = PANEL
        card.line.color.rgb = RGBColor(0x22, 0x23, 0x30)
        card.shadow.inherit = False
        text(s, x + Inches(0.28), y + Inches(0.26), Inches(2.1), Inches(1.0),
             [(num, 38, GREEN if num != "0" else GOLD, False, DISPLAY, 0),
              (label, 10, FAINT, False, MONO, 6)])

    # ---------- 6 收尾 ----------
    s = blank(prs)
    text(s, Inches(0.9), Inches(2.5), Inches(11.5), Inches(2.4),
         [("It was never broken.", 54, FG, False, DISPLAY, 0),
          ("It was priced.", 54, GOLD, False, DISPLAY, 0)], spacing=1.18)
    rule(s, Inches(5.1))
    text(s, Inches(0.9), Inches(5.4), Inches(11.5), Inches(0.8),
         [("Every pattern in this demo is copied from software you already use.",
           16, DIM, False, BODY, 0)])

    # ---------- 7-11 备份：五幕截图 ----------
    acts = [
        ("Act I — Transparent onboarding",
         "Every startup step opens the real source code that just ran.", 14),
        ("Act II — Forty-five seconds of Deluxe",
         "No adverts. 13px body text. Six agents, all green. Real prep pack.", 30),
        ("Act III — The trial ends",
         "No warning was sent. Body text drops to 3.4 pixels.", 47),
        ("Act IV — Absurd, not broken",
         "Every agent still follows its own rules — on someone else's task.", 95),
        ("Act V — Try to cancel",
         "It replays every command it mangled, correctly. Then it starts bribing you.", 118),
    ]
    for title, sub, idx in acts:
        s = blank(prs)
        eyebrow(s, "Backup  ·  live demo capture", Inches(0.5))
        text(s, Inches(0.9), Inches(0.9), Inches(11.4), Inches(0.9),
             [(title, 26, FG, False, DISPLAY, 0),
              (sub, 14, DIM, False, BODY, 6)], spacing=1.2)
        picture(s, frame(idx), Inches(0.9), Inches(2.25), Inches(11.5))

    return prs


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(OUT))
    print("SAVED", OUT, round(OUT.stat().st_size / 1e6, 1), "MB",
          "|", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
