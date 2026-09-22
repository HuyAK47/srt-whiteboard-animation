#!/usr/bin/env python3
"""
Ghép nhiều cảnh: Nối các video hoạt hình bảng trắng MP4 theo thứ tự thành một video hoàn chỉnh.

Ưu tiên dùng ffmpeg hệ thống để ghép nối không suy hao (-c copy, không mã hóa lại); khi kích thước/
chuẩn mã hóa giữa các đoạn không đồng nhất hoặc hệ thống không có ffmpeg, sẽ chuyển sang dùng PyAV
để giải mã và mã hóa lại từng khung hình, đồng thời co giãn/chêm viền về kích thước của đoạn đầu tiên. Các video thành phần vẫn được giữ nguyên.

Cách dùng:
  <ENV_PY> merge_scenes.py --inputs a.mp4 b.mp4 c.mp4 --output final.mp4
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _ffmpeg_concat_copy(inputs: list[Path], output: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for p in inputs:
            f.write(f"file '{p.resolve().as_posix()}'\n")
        list_path = Path(f.name)
    try:
        res = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_path), "-c", "copy", str(output)],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            print(f"  ffmpeg ghép nối không suy hao hoàn tất: {output}")
            return True
        print(f"  [warn] ffmpeg -c copy thất bại, thử mã hóa lại: {res.stderr.strip()[:200]}")
        res = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_path), "-c:v", "libx264", "-crf", "20",
             "-pix_fmt", "yuv420p", "-vf", "scale='trunc(iw/2)*2':'trunc(ih/2)*2'", str(output)],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            print(f"  ffmpeg mã hóa lại và ghép nối hoàn tất: {output}")
            return True
        print(f"  [warn] ffmpeg mã hóa lại cũng thất bại: {res.stderr.strip()[:200]}")
        return False
    finally:
        list_path.unlink(missing_ok=True)


def _pyav_concat(inputs: list[Path], output: Path) -> bool:
    try:
        import av
    except ImportError:
        return False
    import numpy as np  # noqa: F401
    first = av.open(str(inputs[0]))
    vs = first.streams.video[0]
    w, h = vs.codec_context.width, vs.codec_context.height
    rate = vs.average_rate
    first.close()

    out = av.open(str(output), mode="w")
    ostream = out.add_stream("h264", rate=rate)
    ostream.width, ostream.height = w, h
    ostream.pix_fmt = "yuv420p"
    ostream.options = {"crf": "24", "preset": "medium"}
    for p in inputs:
        cont = av.open(str(p))
        for frame in cont.decode(video=0):
            if frame.width != w or frame.height != h:
                frame = frame.reformat(width=w, height=h)
            for pkt in ostream.encode(frame):
                out.mux(pkt)
        cont.close()
    for pkt in ostream.encode(None):
        out.mux(pkt)
    out.close()
    print(f"  PyAV ghép nối hoàn tất: {output}")
    return True


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Ghép nối các video MP4 hoạt hình bảng trắng theo thứ tự")
    p.add_argument("--inputs", nargs="+", required=True, help="Danh sách MP4 theo thứ tự phát")
    p.add_argument("--output", required=True, help="Đường dẫn tệp xuất ra sau khi ghép")
    args = p.parse_args(argv)

    inputs = [Path(x) for x in args.inputs]
    missing = [str(x) for x in inputs if not x.exists()]
    if missing:
        print(f"[err] Thiếu tệp đầu vào: {', '.join(missing)}", file=sys.stderr)
        return 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if _ffmpeg_concat_copy(inputs, output) or _pyav_concat(inputs, output):
        print(f"OUTPUT={output.resolve()}")
        return 0
    print("[err] Ghép nối thất bại: Hệ thống không có ffmpeg và PyAV cũng không khả dụng", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
