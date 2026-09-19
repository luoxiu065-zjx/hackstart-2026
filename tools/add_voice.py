"""给英文版演示视频配旁白，并按旁白长度重新对轴。

思路（保证不抢话、不截断）：
  1. 把字幕合并成段（连续相同的算一段）
  2. 每段用 edge-tts 生成英式男声，量出真实时长
  3. 每段的新时长 = max(原时长, 语音时长 + 0.35 秒留白)
  4. 用 concat demuxer 按新时长重排帧，字幕时间轴跟着重算
  5. 语音按新起点 adelay 后 amix 成一条音轨

在服务器上跑：
    python3 add_voice.py /home/ubuntu/vid/frames-en /home/ubuntu/vid/orchestra-demo-en-voiced.mp4
"""
import io
import json
import os
import shutil
import subprocess
import sys

FPS = 2
VOICE = "en-GB-RyanNeural"
RATE = "+6%"          # 稍微快一点，71 秒的片子别拖成两分钟
PAD = 0.35            # 每段说完留的空
TTS = "/home/ubuntu/mailhub/.venv/bin/edge-tts"

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1398
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EN,{font},50,&H00EFEFEF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,0,0,2,150,150,110,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def font():
    out = run(["fc-list", ":lang=en", "family"]).stdout
    for want in ("Noto Sans", "DejaVu Sans", "Liberation Sans"):
        if want in out:
            return want
    return "sans-serif"


def dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def main():
    frames_dir, out = sys.argv[1], sys.argv[2]
    work = os.path.join(frames_dir, "voice")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)

    subs = json.load(io.open(os.path.join(frames_dir, "subs.json"), encoding="utf-8"))

    # ---- 1. 合并成段 ----
    segs, i = [], 0
    while i < len(subs):
        j = i
        while j + 1 < len(subs) and subs[j + 1][1] == subs[i][1]:
            j += 1
        segs.append({"text": subs[i][1], "frames": [r[0] for r in subs[i:j + 1]],
                     "base": (j + 1 - i) / FPS})
        i = j + 1
    print(f"{len(segs)} 段旁白")

    # ---- 2. 逐段 TTS ----
    for k, sg in enumerate(segs):
        mp3 = os.path.join(work, f"v{k:03d}.mp3")
        r = run([TTS, "--voice", VOICE, "--rate", RATE, "--text", sg["text"],
                 "--write-media", mp3])
        if r.returncode != 0 or not os.path.exists(mp3):
            print("TTS 失败:", sg["text"][:40], r.stderr[-200:])
            sg["audio"], sg["alen"] = None, 0.0
        else:
            sg["audio"], sg["alen"] = mp3, dur(mp3)
        sg["len"] = max(sg["base"], sg["alen"] + PAD)
    total = sum(s["len"] for s in segs)
    print(f"配音后总时长 {total:.1f} 秒（原 {sum(s['base'] for s in segs):.1f} 秒）")

    # ---- 3. 帧清单：每段内部平分新时长 ----
    lst = os.path.join(work, "frames.txt")
    with io.open(lst, "w", encoding="utf-8") as f:
        for sg in segs:
            per = sg["len"] / len(sg["frames"])
            for fr in sg["frames"]:
                p = os.path.join(frames_dir, f"f{fr:04d}.png")
                f.write(f"file '{p}'\nduration {per:.3f}\n")
        last = os.path.join(frames_dir, f"f{segs[-1]['frames'][-1]:04d}.png")
        f.write(f"file '{last}'\n")          # concat demuxer 要求最后一帧再写一次

    # ---- 4. 字幕按新时间轴重排 ----
    ass = os.path.join(work, "subs.ass")
    t = 0.0
    with io.open(ass, "w", encoding="utf-8") as f:
        f.write(ASS_HEAD.format(font=font()))
        for sg in segs:
            f.write(f"Dialogue: 0,{ts(t)},{ts(t + sg['len'])},EN,,0,0,0,,{esc(sg['text'])}\n")
            t += sg["len"]

    # ---- 5. 音轨：每段按新起点延迟后混合 ----
    audio_in, filters, labels = [], [], []
    t = 0.0
    idx = 0
    for sg in segs:
        if sg["audio"]:
            audio_in += ["-i", sg["audio"]]
            filters.append(f"[{idx}:a]adelay={int(t*1000)}|{int(t*1000)},volume=1.6[a{idx}]")
            labels.append(f"[a{idx}]")
            idx += 1
        t += sg["len"]
    mix = "".join(labels) + f"amix=inputs={len(labels)}:dropout_transition=0:normalize=0[aout]"
    voice = os.path.join(work, "voice.m4a")
    r = run(["ffmpeg", "-y", *audio_in, "-filter_complex", ";".join(filters + [mix]),
             "-map", "[aout]", "-c:a", "aac", "-b:a", "128k", voice])
    if r.returncode != 0:
        print(r.stderr[-1200:]); return 1
    print("旁白音轨:", round(dur(voice), 1), "秒")

    # ---- 6. 合成 ----
    r = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", voice,
             "-vf", f"ass={ass},scale=1920:-2,format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-shortest", "-movflags", "+faststart", out])
    if r.returncode != 0:
        print(r.stderr[-1500:]); return 1
    print("完成:", out, round(os.path.getsize(out) / 1e6, 1), "MB",
          "|", round(dur(out), 1), "秒")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
