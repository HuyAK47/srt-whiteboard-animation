---
name: srt-whiteboard-animation
description: Chuyển phụ đề SRT thành hoạt hình vẽ tay trên bảng trắng, nền giấy màu vàng kem ấm: đọc phụ đề → xuất chiến lược minh họa → sau khi xác nhận thì tạo bản vẽ nét thống nhất phong cách → đánh dấu vùng theo ngữ nghĩa tường thuật → chỉnh sửa trên bàn xem trước → render MP4. Việc dàn dựng vẫn dùng cách "hiển thị theo mặt nạ vùng" (annotation.json / sequence / startMs / protectedRegions), nhưng cách hạ mực trong mỗi vùng được thay bằng nét vẽ dòng chảy (stream) liên tục (khung xương/lưới ink→color). Kích hoạt khi người dùng cung cấp phụ đề SRT và yêu cầu "biến phụ đề thành video vẽ tay bảng trắng/nét vẽ dòng chảy", "tạo hoạt hình bảng trắng từ SRT", "vẽ tay theo phân cảnh dựa trên phụ đề".
---

# Hoạt Hình Bảng Trắng Từ SRT (dàn dựng bằng mask + vẽ theo kiểu stream)

Chuyển phụ đề SRT thành hoạt hình vẽ tay trên bảng trắng: **cách dàn dựng** vẫn dùng kiểu "hiển thị theo mặt nạ vùng" (hiển thị lần lượt từng vùng theo trình tự tường thuật, vùng chưa bắt đầu bị ẩn hoàn toàn, phần chồng lấp được bảo vệ bằng `protectedRegions`); **cách vẽ** được đổi thành nét vẽ dòng chảy — trong phạm vi mặt nạ cho phép của mỗi vùng, ngòi bút trượt liên tục theo khung xương/lưới để hạ mực (phác nét `ink` → tô màu `color`), tất cả các vùng dùng chung một khung vẽ (canvas) bền vững, vùng đã vẽ xong vẫn được giữ lại trên khung vẽ. Toàn bộ nội dung hướng tới người dùng — thuyết minh, phân cảnh, cấu hình và giao diện — phải dùng tiếng Trung (theo skill gốc).

Khác với kiểu nhảy khung hoặc xóa dạng hình chữ nhật: nét vẽ của skill này **liền mạch, trôi chảy**; khác với kiểu stream toàn ảnh: skill này vẽ tuần tự theo **phân vùng tường thuật của phụ đề**, có thể kiểm soát thứ tự xuất hiện và thời gian của từng phần tử.

## Tham số triển khai mặc định

| Hạng mục | Yêu cầu mặc định |
|---|---|
| Nền giấy | Ảnh sinh ra dùng màu giấy cũ vàng kem ấm (khuyến nghị `#F5EBD7`); khi render lấy mẫu màu nền từ vùng lùi vào từ bốn góc của ảnh gốc, cấm dùng màu trắng thuần. |
| Cách vẽ | Mỗi vùng dùng nét vẽ dòng chảy liên tục: phác nét `ink` (lên nét vẽ) → tô màu `color` (khôi phục màu gốc); tỉ trọng `ink:color = 2:1`. |
| Đường đi của nét vẽ | `--ink-path grid` (dạng lưới, mặc định, ổn định) hoặc `skeleton` (bám theo khung xương, phù hợp hơn với minh họa có nét vẽ rõ ràng). |
| Phong cách tô màu | `--color-fill contour-wipe` (quét theo đường viền, mặc định) hoặc `brush` (quét theo quỹ đạo cọ vẽ). |
| Vùng chưa được vẽ | Mặt nạ cho phép của vùng = hình chữ nhật `region` trừ đi «các vùng phía sau + protectedRegions»; vùng chưa bắt đầu bị ẩn hoàn toàn. |
| Nguồn thời lượng | `sceneDurationMs` của mỗi ảnh lấy từ khoảng thời gian phụ đề của cảnh đó (khuyến nghị 25–35 giây/cảnh). |
| Khung chỉnh sửa | Bàn xem trước mặc định hiển thị toàn bộ khung chỉnh sửa có đánh số; khung chỉnh sửa không thuộc nội dung hình ảnh của hoạt hình. |

## Quy chuẩn hình ảnh thống nhất khi tạo ảnh (bắt buộc)

Ảnh gốc của tất cả các cảnh phải tuân theo cùng một ngôn ngữ hình ảnh; trước khi tạo ảnh phải đưa đầy đủ các yêu cầu sau vào prompt tạo ảnh, sau khi tạo xong kiểm tra từng mục:

- **Phong cách và bố cục:** Minh họa vẽ tay tối giản, phong cách phác thảo bút chì thuần túy, thẩm mỹ nguệch ngoạc tiết chế kiểu Notion. Lấy biểu đạt khái niệm làm chính, không theo đuổi tính chân thực; bố cục đơn giản, nền sạch, nhiều khoảng trắng, cảm xúc tổng thể điềm tĩnh, rõ ràng, nét vẽ/nhân vật/màu sắc nhất quán trong cả series.
- **Màu sắc và chất liệu:** Nền giấy màu kem `#F5EBD7`, nét phác thảo màu xám đậm; chỉ được dùng màu đỏ, cam, xanh dương để điểm nhấn khái niệm ở mức tối thiểu. Không được dùng các màu nhấn khác, bảng màu độ bão hòa cao hay kết cấu phức tạp.
- **Nhân vật và đối tượng:** Đối tượng được thể hiện bằng đường viền đơn giản, ít nét vẽ và nhiều khoảng trắng, nhấn mạnh mối quan hệ/sự thay đổi/khái niệm cốt lõi, chứ không phải tỷ lệ thật, chất liệu hay chi tiết.
- **Tuyệt đối cấm:** Bất kỳ chữ, từ, chữ cái, số, phông chữ hay nhãn nào trong ảnh gốc của cảnh; cảm giác chân thực, chi tiết nhiếp ảnh, hiệu ứng 3D, chất cảm hội họa; cảnh phức tạp, nền dày đặc, trang trí rườm rà và hình ảnh độ bão hòa cao.
- **Ngoại lệ khi vẽ bàn tay:** Nếu người dùng nói rõ chữ trên thân bút là logo nhận diện của họ và yêu cầu giữ lại, có thể giữ logo trên thân bút của `drawing-hand.png`; đây không thuộc chữ trong ảnh gốc của cảnh, cũng không cần xóa hay vẽ lại. Khi chưa có xác nhận rõ ràng từ người dùng, vẫn xử lý theo nguyên tắc không chữ trong ảnh.

## Cổng xác nhận (bắt buộc)

Trong quy trình mặc định, **sau khi hoàn thành mỗi bước đều phải dừng lại và chờ người dùng xác nhận rõ ràng** mới được bắt đầu bước tiếp theo. Trước khi được xác nhận, không được tạo ảnh, chú thích, bản xem trước, video hoặc file ghép của bước kế tiếp; không được coi "không phản hồi", "sự cho phép chung chung trước đó" hay "người dùng không phản đối" là đã xác nhận. Khi người dùng yêu cầu sửa lại bước trước, chỉ làm lại đúng bước đó, và sau khi hoàn thành lại tiếp tục chờ xác nhận.

Hành động liên đới duy nhất là: **ngay sau khi tạo xong file JSON chú thích, phải tự động mở bàn xem trước và nạp thư mục chứa file JSON đó**; đây là một phần bàn giao của bước 3, không cần chờ xác nhận riêng cho việc "mở bàn xem trước". Nếu File System Access API của trình duyệt yêu cầu thao tác thủ công từ người dùng, hãy dùng giao diện trình duyệt để chọn đúng thư mục đã xác định này; không được vì vậy mà xin thêm xác nhận từ người dùng hay đổi thành để người dùng tự mở bàn xem trước.

## Quy trình làm việc

1. **Đọc phụ đề, xuất chiến lược (chưa tạo ảnh).** Dùng `scripts/parse_srt.py` để phân tích SRT thành các dòng phụ đề và đưa ra đề xuất phân cảnh theo 25–35 giây/cảnh. Dựa vào đó xuất chiến lược minh họa: số thứ tự mỗi cảnh, ý chính, chủ thể hình ảnh, khoảng phụ đề tương ứng và `sceneDurationMs`. Mỗi cảnh chỉ thể hiện một ý chính. **Sau khi hoàn thành thì dừng lại, chờ người dùng xác nhận chiến lược.**
2. **Tạo bản vẽ nét.** Chỉ sau khi người dùng xác nhận chiến lược mới theo "Quy chuẩn hình ảnh thống nhất khi tạo ảnh" để tạo lần lượt từng cảnh ảnh nét vẽ tỉ lệ 16:9, nền giấy cũ màu vàng kem ấm, nền `#F5EBD7`, giữ đủ khoảng trắng giữa các chủ thể để dễ tách vùng tự động; không được tạo chữ, ảnh phức tạp kiểu ảnh chụp, đối tượng chồng lấp hay các yếu tố trái với quy chuẩn. **Sau khi hoàn thành thì dừng lại, hiển thị bản vẽ nét và chờ người dùng xác nhận.**
3. **Đọc phụ đề trước rồi mới xem ảnh, sau đó đánh dấu chú thích và mở bàn xem trước.** Chỉ sau khi người dùng xác nhận bản vẽ nét mới đọc phụ đề tương ứng với ảnh đó, rồi thực sự xem ảnh, và lấy kích thước pixel gốc của ảnh; không được chỉ dựa vào phụ đề để đoán hình ảnh, cũng không được chỉ sắp xếp máy móc theo vị trí trong ảnh. Trước tiên rút ra các sự kiện tường thuật từ phụ đề, sau đó ánh xạ các chủ thể nhìn thấy trong ảnh vào từng sự kiện, sắp xếp thứ tự vẽ theo trình tự ngữ nghĩa "bối cảnh nền → nhân vật/vật thể chính → hành động xung đột hoặc thay đổi → phản ứng/kết quả". Sau đó tạo file `<tên-ảnh>.annotation.json`. Ngay sau khi tạo xong, dùng trình duyệt mặc định mở `assets/preview.html`, và thông qua chức năng "Mở thư mục" của bàn xem trước để nạp toàn bộ cặp `<tên>.png` + `<tên>.annotation.json` trong **thư mục chứa file chú thích đó**; không được chỉ đưa đường dẫn file hoặc yêu cầu người dùng tự thao tác. **Sau khi bàn xem trước đã nạp xong thư mục thì dừng lại, chờ người dùng xác nhận nội dung chú thích và bản xem trước.**
4. **Tạo ảnh kiểm tra vùng.** Chỉ sau khi người dùng xác nhận chú thích và nội dung xem trước mới dùng `render_annotation_preview.py` để xuất ảnh kiểm tra có đánh số/hướng vẽ, đối chiếu xem việc phân vùng có khớp với trình tự tường thuật không, các vùng có nằm trong khung ảnh không, chủ thể chồng lấp có được bảo vệ bằng `protectedRegions` không. **Sau khi hoàn thành thì dừng lại, chờ người dùng xác nhận ảnh xem trước.**
5. **Chỉnh sửa và lưu trên bàn xem trước.** Chỉ sau khi người dùng xác nhận ảnh xem trước mới chỉnh sửa trên bàn xem trước đã mở sẵn và đã nạp đúng thư mục: mặc định (khi chưa phát) hiển thị đầy đủ ảnh và khung vùng; khung vẽ là **đại diện dạng hình chữ nhật**: kéo bốn cạnh/bốn góc của vùng để đổi `region`, chỉnh tên/hướng/**thời gian bắt đầu (ms)/kết thúc (ms)** (thời lượng = kết thúc − bắt đầu, chỉ đọc) và **phụ đề** ở khung bên phải, kéo danh sách khối để **đổi thứ tự** (tự động sắp xếp lại `sequence`), chọn một khối sẽ tự động làm nổi bật phụ đề tương ứng; kéo thanh thời gian hoặc bấm phát để xem việc hiển thị dần (vùng chưa bắt đầu sẽ không hiển thị); `direction` chỉ ảnh hưởng đến bản đại diện này. Sau khi chỉnh xong, bấm "Lưu cảnh này/Lưu tất cả" để ghi lại vào file `.annotation.json` gốc (bao gồm `subtitle` của từng vùng, và canh `sceneDurationMs` theo thời điểm kết thúc của vùng cuối cùng + 0,5 giây). **Sau khi lưu thì dừng lại, chờ người dùng xác nhận chú thích và thời gian cuối cùng.**
6. **Render thành phẩm bằng dòng lệnh.** Chỉ sau khi người dùng xác nhận chú thích và thời gian cuối cùng mới dùng `render_stream_whiteboard.py` để xuất MP4 chất lượng đầy đủ cho từng cảnh, kiểm tra lấy mẫu ở ba thời điểm: mở đầu, giữa một khối bất kỳ có chồng lấp, và kết thúc. **Sau khi hoàn thành thì dừng lại, chờ người dùng xác nhận thành phẩm.**
7. **Ghép nhiều cảnh (chỉ áp dụng khi có nhiều cảnh).** Chỉ sau khi người dùng xác nhận tất cả các thành phẩm của từng cảnh riêng lẻ mới dùng `merge_scenes.py` để ghép lại theo đúng thứ tự thành một video. **Sau khi hoàn thành thì dừng lại, chờ người dùng xác nhận video tổng hợp cuối cùng.**

## Quy ước thư mục

Tạo trong dự án của người dùng:

```text
assets/whiteboard/<tên-dự-án>/
  scene-01-<tên>.png
  scene-01-<tên>.annotation.json     # trùng tên với png
  scene-01-<tên>-whiteboard.mp4      # thành phẩm
  scene-01-<tên>-preview.mp4         # đoạn phim thực tế (do bàn xem trước tạo, chất lượng thấp)
```

Ảnh và file cấu hình phải trùng tên: `foo.png` tương ứng với `foo.annotation.json`. Bàn xem trước sẽ tự động nạp cấu hình dựa vào đó.

## Sắp xếp theo ngữ nghĩa và đánh dấu chú thích ở mức pixel (bắt buộc thực hiện)

1. **Căn cứ để đọc:** Trước khi đánh dấu chú thích phải có đồng thời phụ đề và ảnh gốc đã được xem qua. Thiếu một trong hai thì phải yêu cầu bổ sung trước, không được tạo chú thích.
2. **Căn cứ về thứ tự:** `sequence`, `startMs` và `label` phải phản ánh đúng trình tự trước sau của các sự kiện trong phụ đề, chứ không chỉ theo thứ tự từ trái sang phải, từ trên xuống dưới hay mức độ nổi bật về thị giác.
3. **Căn cứ về tọa độ:** Mỗi khối xuất ra `x`, `y`, `width`, `height` là số nguyên pixel theo hệ tọa độ của ảnh gốc; gốc tọa độ ở góc trên bên trái, cấm dùng tọa độ theo phần trăm/tỷ lệ/ước lượng hoặc bỏ qua kích thước. `canvas.width`/`canvas.height` phải bằng đúng kích thước pixel của ảnh gốc.
4. **Các trường của khối:** Mỗi phần tử gồm `sequence`, `narrativeRole`, `subtitle`, `region`, `reveal`, `handPath`. `narrativeRole` dùng tiếng Trung để mô tả vai trò tường thuật của nó trong phụ đề; `subtitle` lưu nội dung phụ đề tương ứng với vùng đó (lấy từ SRT, phục vụ liên kết trên bàn xem trước và các mục đích sau này); `sequence` bắt đầu liên tục từ 1.
5. **Kiểm tra:** Trước khi tạo bản xem trước, kiểm tra từng vùng xem có nằm trong khung ảnh không, có phủ đúng chủ thể nhìn thấy tương ứng không, có khớp với sự kiện trong phụ đề không; chủ thể chồng lấp phải được bảo vệ bằng `protectedRegions` trước khi vẽ khối đó.

## Mô hình thời gian (dành riêng cho cách vẽ kiểu stream)

- **Tổng thời lượng mỗi cảnh** `sceneDurationMs` lấy từ khoảng thời gian phụ đề của cảnh đó (`scenes[].sceneDurationMs` trong `parse_srt.py`).
- **Các vùng được vẽ tuần tự:** Cách vẽ kiểu stream giống như một cây bút đang di chuyển, các vùng trong cùng một cảnh nên **diễn ra tuần tự theo thời gian** (`startMs` không chồng lấp): vùng tiếp theo bắt đầu từ `startMs + durationMs` của vùng trước đó (cộng thêm khoảng nghỉ tùy chọn 100–300ms). Nếu `startMs` bị chồng lấp, bộ render vẫn xử lý theo thứ tự, nhưng về mặt hình ảnh sẽ không còn là tuần tự nữa.
- **Trong một vùng, phác nét (ink) → tô màu (color):** `durationMs` của mỗi vùng sẽ được chia theo tỉ lệ `ink:color = 2:1` thành đoạn phác nét và đoạn tô màu. `durationMs` được quyết định bởi **thời gian bắt đầu/kết thúc** trên bàn xem trước (kết thúc − bắt đầu), có thể canh theo thời lượng phụ đề tương ứng của vùng đó; cũng có thể dùng ước lượng ban đầu theo công thức 150 pixel/giây × khoảng cách vẽ.
- **Giữ khung hình cuối:** Sau khi vẽ xong tất cả các vùng, hệ thống tự động kéo dài thêm cho đủ `sceneDurationMs`, và đảm bảo giữ khung ảnh gốc hoàn chỉnh ít nhất 0,5 giây ở cuối.
- `reveal.direction` trong cách vẽ kiểu stream **không quyết định nét vẽ thực tế** (nét vẽ được tự động sinh ra theo khung xương/lưới), chỉ dùng để minh họa cho bản đại diện hình chữ nhật trên bàn xem trước; giữ lại trường này là để bàn xem trước có thể sử dụng được.

## Bất biến của mặt nạ (ở tầng dàn dựng, bắt buộc thực hiện)

- Tại thời điểm `t`, một khối chỉ được hiển thị các pixel sau thời điểm `reveal.startMs ≤ t` và không vượt quá tiến độ vẽ hiện tại; bất kỳ nét vẽ/vùng tô/hình ảnh nào của khối chưa bắt đầu đều không được xuất hiện.
- **Mặt nạ cho phép** của mỗi vùng = hình chữ nhật `region` trừ đi toàn bộ **`region` của các khối phía sau**, rồi trừ tiếp `reveal.protectedRegions` của chính khối đó. Việc hạ mực theo kiểu stream bị giới hạn trong mặt nạ cho phép, nên các vùng phía sau sẽ không bị lộ nét sớm.
- `protectedRegions` dùng cùng hệ tọa độ pixel nguyên như `region` của ảnh gốc, dùng cho các trường hợp hình chữ nhật quá lớn, chủ thể chồng lấp nhau hoặc nét vẽ nền có nguy cơ bị lộ ra ngoài.
- Bộ render đã hiện thực hóa trình tự "giới hạn việc hạ mực trong mặt nạ cho phép → các vùng phía sau và vùng bảo vệ tự nhiên không bị chạm tới"; bản đại diện hình chữ nhật trên bàn xem trước dùng phép trừ `destination-out` tương đương để minh họa cùng một cách dàn dựng này.

## Ví dụ cấu hình

```json
{
  "sceneId": "scene-01",
  "canvas": { "width": 1672, "height": 941 },
  "storyBasis": "Tóm tắt sự kiện phụ đề của cảnh này",
  "sceneDurationMs": 9000,
  "elements": [
    {
      "id": "rockery",
      "label": "Bối cảnh núi đá giả",
      "sequence": 1,
      "narrativeRole": "Bối cảnh nền của câu chuyện",
      "subtitle": "Trên núi khỉ, một chú khỉ con ngồi trên đỉnh núi đá giả, tay cầm quả chuối.",
      "type": "structure",
      "region": { "x": 20, "y": 120, "width": 540, "height": 780 },
      "reveal": { "direction": "top_to_bottom", "startMs": 300, "durationMs": 2600, "maskPaddingPx": 22, "protectedRegions": [] },
      "handPath": { "start": [290, 130], "end": [290, 890], "easing": "easeInOut" }
    }
  ]
}
```

> `direction` / `handPath` chỉ dùng cho bản đại diện hình chữ nhật trên bàn xem trước; nét vẽ của thành phẩm được stream tự động sinh ra, không cần tinh chỉnh.

## Sử dụng script

Tất cả các script render đều chạy bằng trình thông dịch `.venv` riêng của skill (cô lập phụ thuộc).

1. **Chuẩn bị môi trường** (lần đầu hoặc khi thiếu phụ thuộc):
   ```bash
   python scripts/prepare_env.py --check   # dò kiểm tra; nếu thành công, dòng cuối in ra ENV_PY=<đường-dẫn>, lưu lại để dùng sau
   python scripts/prepare_env.py           # nếu thiếu sẽ tạo .venv và cài opencv-python/numpy/av
   ```
2. **Phân tích phụ đề + đề xuất phân cảnh**:
   ```bash
   python scripts/parse_srt.py <phu-de.srt> --target-sec 30 --min-sec 25 --max-sec 35
   ```
3. **Ảnh xem trước có đánh số vùng**:
   ```bash
   python scripts/render_annotation_preview.py <ảnh> <chú-thích> <đầu-ra-ảnh-xem-trước>
   ```
4. **Bàn xem trước (không cần server)**: Mở trực tiếp `assets/preview.html` bằng Chrome / Edge, bấm "Mở thư mục" chọn thư mục → nạp toàn bộ ảnh + chú thích trùng tên → kéo thả để chỉnh sửa → bấm "Lưu" để ghi lại vào file gốc. Việc ghi lại cần File System Access API (Chrome/Edge); trình duyệt khác thì tải file về rồi tự tay ghi đè. Việc render vẫn thực hiện qua dòng lệnh (bước 5 bên dưới).
5. **Render thành phẩm từng cảnh**:
   ```bash
   <ENV_PY> scripts/render_stream_whiteboard.py <ảnh> <chú-thích> <đầu-ra.mp4> assets/drawing-hand.png \
       [--ink-path grid|skeleton] [--color-fill contour-wipe|brush] [--total-ms <mili-giây>]
   ```
   Nếu bỏ qua `--total-ms` thì dùng `sceneDurationMs` trong file chú thích. Dòng cuối in ra `OUTPUT=<đường-dẫn>`.
6. **Ghép nhiều cảnh**:
   ```bash
   <ENV_PY> scripts/merge_scenes.py --inputs canh1.mp4 canh2.mp4 canh3.mp4 --output final.mp4
   ```

## Kiểm tra chất lượng

Xác nhận trước/sau khi render:

- Khung hình đầu tiên là nền giấy cũ màu vàng kem sạch sẽ, không có nét vẽ nào lộ ra sớm.
- Đã đọc phụ đề tương ứng và đã thực sự xem ảnh gốc; `canvas` khớp với kích thước pixel của ảnh gốc, tất cả `region` là tọa độ pixel nguyên và nằm trong khung ảnh.
- `sequence`, `startMs` khớp với thứ tự sự kiện trong phụ đề; số thứ tự/nhãn/vùng trong ảnh xem trước đều lấy từ cùng một file chú thích JSON.
- Kiểm tra ở ba thời điểm: mở đầu, giữa một khối bất kỳ có chồng lấp, và sau khi tất cả các khối hoàn thành: các khối chưa vẽ đều không hiển thị, vùng bảo vệ chồng lấp không bị lộ, khung hình cuối cùng hiển thị đầy đủ ảnh gốc.
- Ngòi bút bám sát nét vẽ đang tiến hành; minh họa có nét vẽ rõ ràng có thể dùng `--ink-path skeleton` để nét vẽ khớp hơn.
- Sau khi tất cả các khối hoàn thành, giữ khung ảnh gốc hoàn chỉnh ít nhất 0,5 giây.
- Sau khi ghép nhiều cảnh, thứ tự và thời lượng phải khớp với phân cảnh của phụ đề.

Nếu cần chỉnh sửa hiệu ứng, hãy chỉnh chú thích (vùng/thứ tự/thời gian) trên bàn xem trước (`assets/preview.html`) và lưu lại trước, sau đó mới render bằng dòng lệnh, không nên tạo lại thành phẩm một cách tùy tiện nhiều lần.
