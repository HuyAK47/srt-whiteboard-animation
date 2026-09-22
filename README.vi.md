# Skill Hoạt Hình Bảng Trắng Từ SRT

Skill chuyển phụ đề SRT thành video hoạt hình vẽ tay trên bảng trắng, vẽ theo đúng trình tự tường thuật. Skill kết hợp **dàn dựng mặt nạ theo vùng** với **vẽ nét mực dạng dòng chảy (streaming)**: mỗi phần tử xuất hiện lần lượt theo phụ đề, ngòi bút liên tục "hạ mực" trong từng vùng, sau đó tô màu dần, cuối cùng xuất ra MP4.

Phù hợp để biến các bài giảng kiến thức, kể chuyện bằng giọng đọc, phụ đề khóa học hoặc kịch bản video ngắn thành hoạt hình vẽ tay trên nền giấy màu vàng kem ấm.

## Ví dụ minh họa

**Bối cảnh: Tranh chuối trên núi khỉ** —— Theo trình tự tường thuật của phụ đề, lần lượt vẽ núi đá giả cùng khỉ con, khỉ lớn giành chuối, và các em nhỏ đứng xem.

![Tranh chuối trên núi khỉ: Demo hoạt hình bảng trắng từ SRT](examples/scene-01-monkey-mountain-stream.gif)

Bản vẽ nét gốc: [Xem file PNG](examples/scene-01-monkey-mountain.png).

## Tính năng cốt lõi

- Phân tích phụ đề SRT và chia cảnh theo thời lượng đề xuất 25–35 giây
- Xuất trước kế hoạch phân cảnh (storyboard) và chiến lược minh họa, đảm bảo mỗi cảnh chỉ truyền tải một ý chính
- Xây dựng thứ tự vẽ có ngữ nghĩa cho các phần tử dựa theo sự kiện phụ đề, chứ không phải tọa độ hình ảnh
- Dùng `annotation.json` để quản lý vùng vẽ, thời gian, liên kết phụ đề và vùng bảo vệ chồng lấp
- Mỗi vùng sử dụng nét vẽ dòng chảy liên tục: trước tiên `ink` (nét mực) để phác thảo, sau đó `color` (tô màu)
- Hỗ trợ bàn xem trước trên trình duyệt để chỉnh sửa vùng, thứ tự, thời gian và liên kết phụ đề
- Hỗ trợ render từng cảnh riêng lẻ và ghép nhiều cảnh, xuất ra MP4 hoàn chỉnh

## Cách hoạt động

Điểm mấu chốt của Skill này là "dẫn dắt bởi phụ đề, xác nhận từng bước". Sau mỗi bước đều chờ xác nhận, tránh lãng phí chi phí render khi storyboard, nét vẽ hoặc chú thích chưa được chốt:

1. Phân tích SRT, xuất storyboard và chiến lược minh họa.
2. Sau khi xác nhận, tạo bản vẽ nét với phong cách thống nhất.
3. Sau khi xác nhận bản vẽ nét, kết hợp phụ đề và ảnh gốc để tạo chú thích (annotation), rồi nạp vào bàn xem trước.
4. Sau khi xác nhận chú thích, tạo ảnh kiểm tra vùng và hướng vẽ.
5. Trên bàn xem trước, chỉnh sửa vùng, thứ tự tường thuật, thời gian và liên kết phụ đề rồi lưu lại.
6. Sau khi xác nhận chú thích cuối cùng, render MP4 theo từng cảnh.
7. Với dự án nhiều cảnh, sau khi xác nhận từng cảnh hoàn thiện thì ghép lại.

## Quy chuẩn hình ảnh

- Nền giấy màu vàng kem ấm: khuyến nghị `#F5EBD7`
- Nét vẽ phác thảo màu xám đậm, màu đỏ, cam, xanh dương chỉ dùng để điểm nhấn khái niệm ở mức tối thiểu
- Phong cách vẽ tay tối giản, nền sạch và nhiều khoảng trắng
- Không sử dụng chữ trong cảnh, nhãn, cảm giác nhiếp ảnh, hiệu ứng 3D hoặc kết cấu phức tạp

## Cài đặt và môi trường

Skill đi kèm script chuẩn bị môi trường ảo Python riêng biệt. Khi chạy lần đầu, thực hiện:

```bash
python scripts/prepare_env.py --check
python scripts/prepare_env.py
```

Sau khi chạy thành công, lệnh đầu tiên sẽ in ra `ENV_PY=<đường dẫn>`; các lần render sau hãy dùng trình thông dịch này để đảm bảo cô lập phụ thuộc.

## Cấu trúc tài nguyên dự án

```text
assets/whiteboard/<tên-dự-án>/
├── scene-01-<tên>.png
├── scene-01-<tên>.annotation.json
├── scene-01-<tên>-whiteboard.mp4
└── scene-01-<tên>-preview.mp4
```

Ảnh và file chú thích phải trùng tên, ví dụ `scene-01-demo.png` tương ứng với `scene-01-demo.annotation.json`.

## Định dạng chú thích (annotation)

Mỗi phần tử sử dụng tọa độ pixel nguyên của ảnh gốc, và liên kết với sự kiện trong phụ đề thông qua `sequence`, `subtitle` và `narrativeRole`. Các vùng nên được sắp xếp theo thứ tự "bối cảnh nền → nhân vật/vật thể chính → hành động hoặc thay đổi → phản ứng/kết quả".

```json
{
  "sceneId": "scene-01",
  "canvas": { "width": 1672, "height": 941 },
  "storyBasis": "Khỉ con cầm chuối trên núi khỉ, khỉ lớn giành lấy chuối, các em nhỏ đứng xem.",
  "sceneDurationMs": 9000,
  "elements": [
    {
      "id": "rockery",
      "label": "Bối cảnh núi khỉ",
      "sequence": 1,
      "narrativeRole": "Bối cảnh nền của câu chuyện",
      "subtitle": "Khỉ con ngồi trên đỉnh núi khỉ, tay cầm quả chuối.",
      "type": "structure",
      "region": { "x": 20, "y": 120, "width": 540, "height": 780 },
      "reveal": {
        "direction": "top_to_bottom",
        "startMs": 300,
        "durationMs": 2600,
        "maskPaddingPx": 22,
        "protectedRegions": []
      },
      "handPath": { "start": [290, 130], "end": [290, 890], "easing": "easeInOut" }
    }
  ]
}
```

`direction` và `handPath` được dùng cho khung chữ nhật đại diện trên bàn xem trước; nét vẽ thật của bản dựng cuối cùng do bộ vẽ dòng chảy tự động tạo ra. Với các đối tượng che khuất lẫn nhau, hãy đánh dấu vùng cần hiển thị muộn hơn trong `protectedRegions` của phần tử xuất hiện trước, để tránh nội dung phía sau lộ ra sớm.

## Các lệnh thường dùng

Phân tích phụ đề và tạo đề xuất phân cảnh:

```bash
python scripts/parse_srt.py <phu-de.srt> --target-sec 30 --min-sec 25 --max-sec 35
```

Tạo ảnh kiểm tra vùng:

```bash
python scripts/render_annotation_preview.py <đường-dẫn-ảnh> <đường-dẫn-chú-thích> <đường-dẫn-ảnh-xem-trước>
```

Mở `assets/preview.html`, dùng chức năng "Mở thư mục" để nạp thư mục cảnh, sau đó có thể chỉnh sửa vùng, thứ tự, thời gian và liên kết phụ đề.

Render một cảnh:

```bash
<ENV_PY> scripts/render_stream_whiteboard.py <đường-dẫn-ảnh> <đường-dẫn-chú-thích> <đầu-ra.mp4> assets/drawing-hand.png \
  --ink-path grid --color-fill contour-wipe
```

Ghép nhiều cảnh:

```bash
<ENV_PY> scripts/merge_scenes.py --inputs canh1.mp4 canh2.mp4 canh3.mp4 --output final.mp4
```

## Kiểm tra chất lượng

- Khung hình đầu tiên là nền giấy màu vàng kem sạch, không có nét vẽ nào lộ ra sớm
- `canvas` khớp với kích thước ảnh gốc, tất cả các vùng đều là tọa độ pixel nguyên nằm trong khung ảnh
- `sequence` và `startMs` khớp với thứ tự tường thuật của phụ đề
- Ở các khung hình giữa, vùng chưa bắt đầu và vùng bảo vệ không xuất hiện sớm
- Ngòi bút bám sát nét vẽ dòng chảy hiện tại; khi nét vẽ đã rõ ràng có thể chọn `--ink-path skeleton`
- Mỗi cảnh kết thúc phải giữ khung hình hoàn chỉnh ít nhất 0,5 giây; thứ tự ghép nhiều cảnh phải khớp với phân cảnh của phụ đề

## Nội dung kho mã nguồn

```text
srt-whiteboard-animation/
├── SKILL.md                         # Toàn bộ quy trình làm việc và ràng buộc
├── assets/
│   ├── drawing-hand.png              # Tài nguyên hình bàn tay
│   ├── preview.html                  # Bàn xem trước và chỉnh sửa cục bộ
├── examples/                         # Tài nguyên ví dụ cho README
├── scripts/
│   ├── parse_srt.py                  # Phân tích phụ đề và đề xuất phân cảnh
│   ├── render_annotation_preview.py  # Ảnh kiểm tra chú thích
│   ├── render_stream_whiteboard.py   # Bộ render MP4 nét vẽ dòng chảy
│   ├── merge_scenes.py               # Ghép nhiều cảnh
│   └── prepare_env.py                # Chuẩn bị môi trường phụ thuộc
└── agents/openai.yaml                # Metadata cho Codex
```

## Đóng góp

Hoan nghênh gửi Issue hoặc Pull Request. Mọi thay đổi liên quan đến logic vẽ đều nên được kiểm tra bằng phụ đề, chú thích và bản dựng thực tế, đảm bảo mặt nạ bảo vệ, thời gian và khung hình cuối cùng chính xác.

## Giấy phép

Dự án này mã nguồn mở theo Giấy phép MIT, chi tiết xem tại [LICENSE](LICENSE).

## Về tác giả

Một ông chú thích nuôi cá / AI Builder / Dùng đội ngũ AI để xây dựng công ty một người.

Douyin, Bilibili, Tài khoản công khai (WeChat): 江哥是老登啊
