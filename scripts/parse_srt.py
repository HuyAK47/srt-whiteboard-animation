#!/usr/bin/env python3
"""
Phân tích phụ đề SRT + Đề xuất phân cảnh

Phân tích phụ đề .srt thành các câu phụ đề có cấu trúc, đồng thời gom nhóm phụ đề
thành các cảnh theo khuyến nghị "mỗi cảnh 25-35 giây thuyết minh", đưa ra thời gian
bắt đầu, kết thúc, tổng thời lượng (→ sceneDurationMs) và văn bản của từng cảnh.

Mục đích: Dùng làm dữ liệu đầu vào cho Bước 1 trong quy trình srt-whiteboard-animation:
đọc các sự kiện tường thuật, lập chiến lược minh họa và xác định sceneDurationMs cho chú thích của từng ảnh.

Cách dùng:
  python parse_srt.py <phu-de.srt> [--target-sec 30] [--min-sec 25] [--max-sec 35]

Đầu ra: JSON (stdout), các trường:
  cues    Mỗi câu phụ đề: {index, startMs, endMs, durMs, text}
  scenes  Cảnh đề xuất:   {sceneIndex, startMs, endMs, sceneDurationMs, cueRange, text}
In tóm tắt dễ đọc ra stderr tiêu chuẩn để tiện theo dõi trực tiếp.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_TIME = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{1,3})")


def _to_ms(h: str, m: str, s: str, ms: str) -> int:
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms.ljust(3, "0"))


def parse_srt(text: str) -> list[dict]:
    """Phân tích văn bản SRT thành danh sách phụ đề. Chấp nhận dòng trống thừa, BOM, dấu phẩy/chấm phân cách mili-giây."""
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues: list[dict] = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        # Tìm dòng chứa mốc thời gian
        time_line_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if time_line_idx is None:
            continue
        times = _TIME.findall(lines[time_line_idx])
        if len(times) < 2:
            continue
        start = _to_ms(*times[0])
        end = _to_ms(*times[1])
        body = " ".join(lines[time_line_idx + 1:]).strip()
        cues.append({
            "index": len(cues) + 1,
            "startMs": start,
            "endMs": end,
            "durMs": max(0, end - start),
            "text": body,
        })
    return cues


def group_scenes(cues: list[dict], target_sec: float, min_sec: float, max_sec: float) -> list[dict]:
    """
    Gom các phụ đề liên tiếp thành cảnh theo thời lượng mục tiêu: tích lũy đến gần target thì ngắt cảnh,
    nhưng không nhỏ hơn min và không lớn hơn max (vượt quá max sẽ buộc phải ngắt cảnh).
    """
    scenes: list[dict] = []
    bucket: list[dict] = []
    target_ms, min_ms, max_ms = target_sec * 1000, min_sec * 1000, max_sec * 1000

    def flush() -> None:
        if not bucket:
            return
        start = bucket[0]["startMs"]
        end = bucket[-1]["endMs"]
        scenes.append({
            "sceneIndex": len(scenes) + 1,
            "startMs": start,
            "endMs": end,
            "sceneDurationMs": max(0, end - start),
            "cueRange": [bucket[0]["index"], bucket[-1]["index"]],
            "text": " ".join(c["text"] for c in bucket).strip(),
        })
        bucket.clear()

    for cue in cues:
        # Nếu gộp câu này vào cảnh hiện tại mà vượt quá max, ngắt cảnh trước (tránh cảnh quá dài)
        if bucket:
            span_with = cue["endMs"] - bucket[0]["startMs"]
            if span_with > max_ms:
                flush()
        bucket.append(cue)
        span = bucket[-1]["endMs"] - bucket[0]["startMs"]
        # Đạt thời lượng mục tiêu và không ngắn hơn min thì ngắt cảnh
        if span >= target_ms and span >= min_ms:
            flush()
    flush()
    return scenes


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Phân tích phụ đề SRT + Đề xuất phân cảnh")
    p.add_argument("srt", help="Đường dẫn tệp phụ đề (.srt)")
    p.add_argument("--target-sec", type=float, default=30.0, help="Số giây thuyết minh mục tiêu cho mỗi cảnh (mặc định 30)")
    p.add_argument("--min-sec", type=float, default=25.0, help="Số giây tối thiểu cho mỗi cảnh (mặc định 25)")
    p.add_argument("--max-sec", type=float, default=35.0, help="Số giây tối đa cho mỗi cảnh (mặc định 35)")
    args = p.parse_args(argv)

    try:
        raw = Path(args.srt).read_text(encoding="utf-8-sig")
    except OSError as e:
        print(f"[err] Không thể đọc tệp phụ đề: {e}", file=sys.stderr)
        return 1

    cues = parse_srt(raw)
    if not cues:
        print("[err] Không phân tích được câu phụ đề nào, vui lòng kiểm tra định dạng SRT", file=sys.stderr)
        return 1
    scenes = group_scenes(cues, args.target_sec, args.min_sec, args.max_sec)

    total_ms = cues[-1]["endMs"] - cues[0]["startMs"]
    print(f"Số câu phụ đề: {len(cues)}  Tổng thời lượng: {total_ms/1000:.1f}s  Số cảnh đề xuất: {len(scenes)}", file=sys.stderr)
    for s in scenes:
        print(f"  Cảnh {s['sceneIndex']:>2}  {s['startMs']/1000:6.1f}-{s['endMs']/1000:6.1f}s "
              f"({s['sceneDurationMs']/1000:4.1f}s, Phụ đề {s['cueRange'][0]}-{s['cueRange'][1]}): "
              f"{s['text'][:40]}", file=sys.stderr)

    json.dump({"cues": cues, "scenes": scenes}, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
