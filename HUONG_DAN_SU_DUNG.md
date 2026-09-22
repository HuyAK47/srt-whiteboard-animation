# Hướng Dẫn Sử Dụng: SRT Whiteboard Animation

Quy trình và công cụ tự động hóa sản xuất video hoạt hình vẽ tay trên bảng trắng (Whiteboard Animation) từ tệp phụ đề SRT, kết hợp kỹ thuật dàn dựng mặt nạ vùng và nét vẽ dòng chảy liên tục (streaming stroke).

---

## Mục Lục
1. [Giới Thiệu & Mục Đích](#1-giới-thiệu--mục-đích)
2. [Nguyên Lý Kỹ Thuật Cốt Lõi](#2-nguyên-lý-kỹ-thuật-cốt-lõi)
3. [Yêu Cầu Hệ Thống & Môi Trường](#3-yêu-cầu-hệ-thống--môi-trường)
4. [Cài Đặt Môi Trường Ảo](#4-cài-đặt-môi-trường-ảo)
5. [Quy Trình Sản Xuất Video Chi Tiết](#5-quy-trình-sản-xuất-video-chi-tiết)
   - [Bước 1: Phân tích phụ đề SRT](#bước-1-phân-tích-phụ-đề-srt-và-chia-phân-cảnh)
   - [Bước 2: Chuẩn bị ảnh minh họa](#bước-2-chuẩn-bị-ảnh-minh-họa-line-art)
   - [Bước 3: Định nghĩa chú thích & Tọa độ vùng](#bước-3-định-nghĩa-chú-thích--tọa-độ-vùng-annotationjson)
   - [Bước 4: Xem trước & Tinh chỉnh trực quan](#bước-4-xem-trước--tinh-chỉnh-trên-giao-diện-web)
   - [Bước 5: Render video phân cảnh](#bước-5-render-video-từng-phân-cảnh)
   - [Bước 6: Ghép nối video thành phẩm](#bước-6-ghép-nối-các-phân-cảnh-thành-video-hoàn-chỉnh)
6. [Bảng Tra Cứu Tham Số Dòng Lệnh (CLI)](#6-bảng-tra-cứu-tham-số-dòng-lệnh-cli)
7. [Tích Hợp Với Trợ Lý AI (AI Agent Skill)](#7-tích-hợp-với-trợ-lý-ai-ai-agent-skill)
8. [Khắc Phục Sự Cố Thường Gặp](#8-khắc-phục-sự-cố-thường-gặp)

---

## 1. Giới Thiệu & Mục Đích

Dự án **`srt-whiteboard-animation`** giải quyết bài toán biến nội dung kịch bản hoặc bài giảng (dưới dạng tệp phụ đề `.srt`) thành video hoạt hình vẽ tay chân thực trên nền giấy màu vàng kem ấm áp (`#F5EBD7`).

Phù hợp cho:
- Video bài giảng kiến thức, khóa học trực tuyến.
- Tóm tắt sách, kể chuyện truyền cảm hứng.
- Video ngắn giải thích khái niệm (Notion-style doodle/explainer video).

---

## 2. Nguyên Lý Kỹ Thuật Cốt Lõi

Khác với các phần mềm vẽ bảng thông thường (thường xóa mở hình chữ nhật cứng nhắc hoặc vẽ ngẫu nhiên từ trên xuống dưới):

1. **Dẫn dắt theo ngữ nghĩa câu chuyện (Narrative-driven):** Các đối tượng xuất hiện theo đúng dòng thời gian lời thoại phụ đề, tuân theo trình tự ngữ nghĩa:  
   `Bối cảnh nền` → `Nhân vật / Chủ thể chính` → `Hành động / Biến chuyển` → `Kết quả / Phản ứng`.
2. **Nét vẽ dòng chảy liên tục (Streaming stroke):** Ngòi bút bám sát khung xương nét vẽ (`skeleton`) hoặc ô lưới (`grid`) để hạ mực liên tục:
   - **Giai đoạn phác thảo (`ink`):** Ngòi bút vẽ ra các nét đen phác họa (chiếm 2/3 thời lượng vùng).
   - **Giai đoạn tô màu (`color`):** Quét màu gốc lấp đầy (chiếm 1/3 thời lượng vùng).
3. **Mặt nạ bảo vệ vùng chồng lấn (`protectedRegions`):** Mỗi vùng chỉ được vẽ trong mặt nạ cho phép. Các vùng xuất hiện sau sẽ bị ẩn hoàn toàn, tránh lộ nét vẽ trước thời điểm xuất hiện trong lời thoại.
4. **Canvas dùng chung bền vững:** Các phần tử sau khi vẽ xong sẽ được giữ nguyên trên canvas cho đến hết cảnh.

---

## 3. Yêu Cầu Hệ Thống & Môi Trường

- **Hệ điều hành:** Linux, macOS, hoặc Windows.
- **Python:** Phiên bản 3.9 trở lên (kèm `venv`, `pip`).
- **FFmpeg:** *(Khuyến nghị cài đặt trên hệ thống)* để ghép nối video không suy hao và chuyển mã H.264 nhanh nhất. Nếu hệ thống chưa có FFmpeg, script sẽ tự động dùng thư viện `PyAV`.

---

## 4. Cài Đặt Môi Trường Ảo

Mã nguồn đi kèm script tự động thiết lập và cô lập môi trường ảo:

```bash
# 1. Kiểm tra môi trường xem đã sẵn sàng chưa
python3 scripts/prepare_env.py --check

# 2. Tạo môi trường ảo .venv và tự động cài đặt các thư viện cần thiết
python3 scripts/prepare_env.py
```

Khi chạy xong, terminal sẽ in ra đường dẫn trình thông dịch, ví dụ:
```text
ENV_PY=/duong-dan/srt-whiteboard-animation/.venv/bin/python
```
> Hãy sử dụng biến hoặc đường dẫn `ENV_PY` này cho các lệnh render ở các bước tiếp theo.

---

## 5. Quy Trình Sản Xuất Video Chi Tiết

```text
[Tệp SRT] ──(1. parse_srt.py)──> [Kế hoạch phân cảnh]
    │
[Tạo ảnh] ──(2. Chuẩn 16:9 Notion)──> [scene-01.png]
    │
[Gắn nhãn] ──(3. preview.html)──> [scene-01.annotation.json]
    │
[Render] ──(4. render_stream_whiteboard.py)──> [scene-01.mp4]
    │
[Ghép nối] ──(5. merge_scenes.py)──> [final.mp4]
```

### Bước 1: Phân tích phụ đề SRT và chia phân cảnh
Chạy script phân tích để chia kịch bản thành từng cảnh (khuyến nghị 25–35 giây/cảnh):

```bash
python3 scripts/parse_srt.py <duong-dan-file.srt> --target-sec 30 --min-sec 25 --max-sec 35
```

- Lệnh sẽ in ra bản tóm tắt phân cảnh trên màn hình và xuất JSON cấu trúc gồm các câu phụ đề (`cues`) và danh sách cảnh đề xuất (`scenes`).

### Bước 2: Chuẩn bị ảnh minh họa (Line Art)
Tạo ảnh minh họa độ phân giải 16:9 (ví dụ: `1920x1080` hoặc `1672x941`) cho từng phân cảnh:
- **Màu nền giấy:** Màu vàng kem ấm `#F5EBD7`.
- **Phong cách:** Nét vẽ tay tối giản (doodle/sketch phong cách Notion), nhiều khoảng trắng.
- **Quy tắc bắt buộc:** **Không** chèn chữ, nhãn, số; không dùng hiệu ứng 3D tả thực hay kết cấu phức tạp.
- Đặt tên tệp theo quy ước: `scene-01-<ten>.png`.

### Bước 3: Định nghĩa chú thích & Tọa độ vùng (`annotation.json`)
Tạo tệp JSON cùng tên với ảnh (ví dụ: `scene-01-<ten>.annotation.json`):

```json
{
  "sceneId": "scene-01",
  "canvas": { "width": 1920, "height": 1080 },
  "storyBasis": "Tóm tắt nội dung cảnh",
  "sceneDurationMs": 28000,
  "elements": [
    {
      "id": "background",
      "label": "Bối cảnh nền",
      "sequence": 1,
      "narrativeRole": "Thiết lập không gian",
      "subtitle": "Câu phụ đề tương ứng...",
      "type": "structure",
      "region": { "x": 100, "y": 150, "width": 600, "height": 800 },
      "reveal": {
        "direction": "top_to_bottom",
        "startMs": 500,
        "durationMs": 4000,
        "protectedRegions": []
      },
      "handPath": { "start": [400, 150], "end": [400, 950], "easing": "easeInOut" }
    }
  ]
}
```

### Bước 4: Xem trước & Tinh chỉnh trên giao diện web
1. Mở tệp [assets/preview.html](assets/preview.html) trên trình duyệt (hỗ trợ Chrome, Edge).
2. Nhấn nút **"Mở thư mục"** và chọn thư mục chứa các cặp `.png` và `.annotation.json`.
3. Giao diện trực quan cho phép:
   - Kéo chỉnh các góc khung chữ nhật để định vị vùng (`region`).
   - Kéo thanh timeline để xem tiến trình mở nét vẽ.
   - Sắp xếp thứ tự vẽ (`sequence`), điều chỉnh thời gian `startMs`, `durationMs` khớp với câu phụ đề.
4. Bấm **"Lưu chú thích"** để ghi đè cập nhật vào tệp `.annotation.json`.

*(Tùy chọn: Chạy `python3 scripts/render_annotation_preview.py <anh.png> <chu_thich.json> <xem_truoc.png>` để xuất ảnh kiểm tra khung số thứ tự).*

### Bước 5: Render video từng phân cảnh
Sử dụng script tích hợp kết hợp với ảnh bàn tay vẽ [assets/drawing-hand.png](assets/drawing-hand.png):

```bash
.venv/bin/python scripts/render_stream_whiteboard.py \
  scene-01.png \
  scene-01.annotation.json \
  scene-01.mp4 \
  assets/drawing-hand.png \
  --ink-path grid \
  --color-fill contour-wipe
```

- Video kết quả `scene-01.mp4` sẽ được tự động chuyển mã chuẩn **H.264 (yuv420p)** để tương thích với mọi trình phát.

### Bước 6: Ghép nối các phân cảnh thành video hoàn chỉnh
Khi đã render xong tất cả các cảnh đơn lẻ, ghép lại theo thứ tự phát:

```bash
.venv/bin/python scripts/merge_scenes.py \
  --inputs scene-01.mp4 scene-02.mp4 scene-03.mp4 \
  --output video_hoan_thanh.mp4
```

---

## 6. Bảng Tra Cứu Tham Số Dòng Lệnh (CLI)

### `render_stream_whiteboard.py`
| Tham số | Giá trị mặc định | Mô tả |
|---|:---:|---|
| `image` | *(Bắt buộc)* | Đường dẫn tệp ảnh vẽ nét |
| `annotation` | *(Bắt buộc)* | Đường dẫn tệp `annotation.json` |
| `output` | *(Bắt buộc)* | Đường dẫn video MP4 xuất ra |
| `hand` | `assets/drawing-hand.png` | Ảnh bàn tay cầm bút |
| `--total-ms` | Theo `sceneDurationMs` | Tổng thời lượng video (ms) |
| `--bare-tip` | `False` | Không vẽ phủ hình ảnh bàn tay |
| `--ink-path` | `grid` | Đường đi nét phác thảo: `grid` (nội suy lưới, ổn định) hoặc `skeleton` (bám xương nét vẽ) |
| `--color-fill` | `contour-wipe` | Kiểu quét màu: `contour-wipe` (quét từ trên xuống theo đường viền) hoặc `brush` (quét theo cọ) |
| `--fps` | `60` | Tốc độ khung hình (frame rate) |
| `--cap-long-edge` | `1080` | Giới hạn độ phân giải cạnh dài (giảm xuống ví dụ 720 để render nhanh khi test) |

### `parse_srt.py`
| Tham số | Giá trị mặc định | Mô tả |
|---|:---:|---|
| `srt` | *(Bắt buộc)* | Đường dẫn tệp phụ đề `.srt` |
| `--target-sec` | `30.0` | Số giây mục tiêu cho mỗi phân cảnh |
| `--min-sec` | `25.0` | Số giây tối thiểu cho mỗi phân cảnh |
| `--max-sec` | `35.0` | Số giây tối đa cho mỗi phân cảnh |

### `merge_scenes.py`
| Tham số | Giá trị mặc định | Mô tả |
|---|:---:|---|
| `--inputs` | *(Bắt buộc)* | Danh sách các tệp video MP4 theo thứ tự |
| `--output` | *(Bắt buộc)* | Đường dẫn tệp video tổng hợp xuất ra |

---

## 7. Tích Hợp Với Trợ Lý AI (AI Agent Skill)

Dự án được chuẩn hóa theo kiến trúc Skill của các trợ lý AI (Codex, Antigravity, Claude):
- **Cấu hình Skill:** [SKILL.vi.md](SKILL.vi.md) và [SKILL.md](SKILL.md).
- **Giao diện Agent:** [agents/openai.yaml](agents/openai.yaml).

Khi muốn trợ lý AI thực hiện toàn bộ quy trình, bạn chỉ cần tải tệp SRT lên và ra lệnh:
> *"Sử dụng skill srt-whiteboard-animation để tạo hoạt hình bảng trắng từ tệp phụ đề này."*

Quy trình sẽ thực hiện tuần tự qua các cổng xác nhận: Duyệt kịch bản phân cảnh → Duyệt ảnh vẽ nét → Kiểm tra chú thích qua bàn xem trước → Render thành phẩm.

---

## 8. Khắc Phục Sự Cố Thường Gặp

1. **Lỗi `ModuleNotFoundError: No module named 'cv2'`:**
   - Bạn đang dùng Python mặc định của hệ điều hành thay vì Python trong môi trường ảo. Hãy dùng đường dẫn `.venv/bin/python` (hoặc `.venv\Scripts\python.exe` trên Windows).
2. **Nét vẽ bị lộ sớm khi chưa đến lời thoại:**
   - Kiểm tra lại trường `protectedRegions` trong `annotation.json`. Nếu vùng A nằm đè lên vùng B nhưng vẽ trước, hãy thêm tọa độ của vùng B vào `protectedRegions` của vùng A.
3. **Cảnh video kết thúc quá nhanh sau khi vẽ xong:**
   - Script mặc định sẽ tự động dừng hình (`gaze`) tối thiểu 0.5 giây sau khi nét vẽ cuối cùng hoàn tất để người xem chiêm ngưỡng toàn bộ tác phẩm.
4. **Không mở được thư mục trên `preview.html`:**
   - Đảm bảo bạn đang sử dụng trình duyệt hỗ trợ File System Access API (Google Chrome hoặc Microsoft Edge).
