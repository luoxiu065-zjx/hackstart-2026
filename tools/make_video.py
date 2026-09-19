"""把 CDP 录下来的帧 + 双语字幕合成演示视频。

在服务器上跑（那边有 ffmpeg 6.1 和中日韩字体）：
    python3 make_video.py /home/ubuntu/vid/frames /home/ubuntu/vid/orchestra-demo.mp4

帧是 2 fps（每帧 0.5 秒），142 帧 ≈ 71 秒。
字幕用 ASS：上面英文小字，下面中文大字，连续相同的合并成一段。
"""
import io
import json
import os
import subprocess
import sys

FPS = 2

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1398
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CN,{cjk},52,&H00EFEFEF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,0,0,2,140,140,120,1
Style: EN,{cjk},38,&H00C9A36A,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,0,0,2,140,140,190,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def cjk_font() -> str:
    """找一个装得上的中日韩字体，找不到就退回 sans-serif（中文会变方块，但不会崩）。"""
    try:
        out = subprocess.run(["fc-list", ":lang=zh", "family"],
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return "sans-serif"
    for want in ("Noto Sans CJK SC", "Noto Sans CJK", "WenQuanYi Zen Hei",
                 "Source Han Sans", "Droid Sans Fallback"):
        if want in out:
            return want
    first = out.strip().splitlines()
    return first[0].split(",")[0] if first else "sans-serif"


def ts(x: float) -> str:
    h = int(x // 3600)
    m = int(x % 3600 // 60)
    s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(s: str) -> str:
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def build_ass(frames_dir: str, font: str) -> str:
    subs = json.load(io.open(os.path.join(frames_dir, "subs.json"), encoding="utf-8"))
    path = os.path.join(frames_dir, "subs.ass")
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(ASS_HEAD.format(cjk=font))
        i = 0
        while i < len(subs):
            j = i
            while j + 1 < len(subs) and subs[j + 1][1] == subs[i][1]:
                j += 1
            t0, t1 = i / FPS, (j + 1) / FPS
            f.write(f"Dialogue: 0,{ts(t0)},{ts(t1)},EN,,0,0,0,,{esc(subs[i][2])}\n")
            f.write(f"Dialogue: 0,{ts(t0)},{ts(t1)},CN,,0,0,0,,{esc(subs[i][1])}\n")
            i = j + 1
    return path


def main() -> int:
    frames_dir = sys.argv[1]
    out = sys.argv[2]
    font = cjk_font()
    print("字幕字体:", font)
    ass = build_ass(frames_dir, font)
    print("字幕文件:", ass, os.path.getsize(ass), "字节")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f%04d.png"),
        "-vf", f"ass={ass},scale=1920:-2,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-movflags", "+faststart",
        out,
    ]
    print("ffmpeg 开始…")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1600:])
        return r.returncode
    print("完成:", out, round(os.path.getsize(out) / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
