# SOP chi tiết

Các ID tài khoản lấy từ `config.local.json` (tạo từ `config.example.json`):
`advertiser_id`, `store_id`, `store_authorized_bc_id`, `inhouse_identity_id`, `inhouse_username`.

## Mục lục
1. Số liệu GMV Max
2. Tài liệu nội bộ
3. PDP
4. Lời thoại video
5. Khung 25 ô (xem grid-25.md)
6. Contact sheet
7. Phân tích hook (xem hook-analysis.md)
8. Dựng báo cáo
9. Lỗi thường gặp

---

## 1. Số liệu GMV Max (MCP TikTok Business)

Gọi qua `tool_execute` với `tool_name = "gmv_max_report_get"`.

**1a. Danh sách campaign**
```json
{"advertiser_id": "<adv>", "store_ids": ["<store>"], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD",
 "dimensions": ["campaign_id"], "metrics": ["campaign_name","gross_revenue","cost","orders"],
 "filtering": {"gmv_max_promotion_types": ["PRODUCT"], "campaign_statuses": ["STATUS_ALL"]},
 "page_size": 200, "sort_field": "gross_revenue"}
```
Chọn các campaign có doanh thu và có chứa SPU (campaign riêng của sản phẩm và campaign All Products).

**1b. Số liệu theo video**
```json
{"advertiser_id": "<adv>", "store_ids": ["<store>"], "start_date": "...", "end_date": "...",
 "dimensions": ["campaign_id","item_group_id","item_id"],
 "metrics": ["gross_revenue","cost","orders","roi","product_impressions","product_clicks",
             "ad_click_rate","ad_conversion_rate","ad_video_view_rate_2s","ad_video_view_rate_6s",
             "ad_video_view_rate_p25","ad_video_view_rate_p50","ad_video_view_rate_p75","ad_video_view_rate_p100"],
 "filtering": {"campaign_ids": ["..."], "item_group_ids": ["<SPU>"]},
 "page_size": 1000, "sort_field": "gross_revenue"}
```
- `title`, `tt_account_name` không dùng được ở cấp này (API trả lỗi 40002).
- Kết quả lớn bị lưu thành file: chạy `python scripts/aggregate_gmvmax.py --report <file> --excel <export.xlsx> --inhouse <username> --out top_gmvmax.json`.
- `item_id = -1` là product card, script tự bỏ.
- Script in ra các video có GMV cao nhưng không có trong Excel: kiểm tra chủ kênh của chúng trước khi chốt top 20.

## 2. Tài liệu nội bộ

- File content hit cũ trên Google Docs (nếu có): `read_file_content` với fileId trong link.
- Phương pháp 25 ô: dùng `references/grid-25.md`, không cần mở tài liệu gốc.

## 3. PDP TikTok Shop

- Mở link PDP bằng Chrome. Gặp CAPTCHA thì dừng, nhờ người dùng tự kéo mảnh ghép.
- Bấm "Xem thêm" ở mô tả, cuộn qua các ảnh mô tả. Ghi lại: giá từng phân loại, phân loại mặc định, rating, số đã bán, thông số, ảnh so sánh, ảnh công dụng, chứng nhận.

## 4. Lời thoại video

Trên trang `https://www.tiktok.com/@<user>/video/<id>`, đọc JSON `#__UNIVERSAL_DATA_FOR_REHYDRATION__` →
`__DEFAULT_SCOPE__['webapp.video-detail'].itemInfo.itemStruct.video.subtitleInfos` → fetch URL phụ đề (ưu tiên `vie-VN`), bỏ dòng thời gian.
- Chạy `browser_batch` theo lô 5–9 video (navigate + javascript), lưu vào `localStorage`. Đổ ra bằng cách chèn toàn bộ text vào 1 thẻ `<article>` rồi `get_page_text` (javascript_tool cắt kết quả khoảng 1.000 ký tự).
- Không fetch trực tiếp `/api/item/detail` (bị chặn vì truy cập trái phép).
- Video không voice: dựa vào caption, nhạc nền và frame.

## 6. Contact sheet

**Cách A, API (ưu tiên)**
1. `gmv_max_video_get`: `store_id`, `store_authorized_bc_id`, `spu_id_list=[SPU]`, `need_auth_code_video=true`, `identity_list=[identity Inhouse]`, `page_size=50`, lật trang.
2. Video còn thiếu: gọi lại với `keyword=<item_id>` (khớp chính xác), `page_size=1`. Video Inhouse cần identity TT_USER của kênh.
3. Ghi `{item_id: preview_url}` vào `video_urls.json` → `python scripts/contact_sheet.py --urls video_urls.json --top top_gmvmax.json --out strips/`.
   Script tải mp4, cắt frame ở 0, 1, 2, 3, 5, 8 giây, giữa và cuối, lưu 1 dải/video và các sheet 4 video để xem nhanh.

**Cách B, KOC hết ủy quyền (Chrome, GMV Max)**
1. Mở `https://ads.tiktok.com/i18n/gmv-max/manage-analyze?aadvid=<adv>&oec_seller_id=<store>&bc_id=<bc>&reporting_type=video`.
2. Mỗi video: tải lại trang, chờ 10 giây, focus ô tìm kiếm bằng JS (`input[placeholder*=search]`), gõ đúng 1 Post ID, Enter, bấm dòng "Post ID contains any of", bấm thumbnail để mở drawer, bấm play.
3. Chạy `scripts/browser_contact_sheet.js` bằng javascript_tool, rồi chụp màn hình phần canvas trên cùng.
4. Tab "Frame by frame" trong drawer: biểu đồ click và giữ chân theo giây. Chụp cho các video top.
- Không gõ nhiều ID một lúc và không bỏ lọc rồi gõ tiếp: trang dễ treo.
- Link mp4 có chữ ký không lấy ra ngoài trình duyệt được, nên dựng sheet ngay trong trang.

**Cách C**: gửi người dùng danh sách ID còn thiếu. Họ lấy link mp4 từ Seller Center (Phân tích LIVE & video → Tài khoản liên kết → bấm video). Lưu ý Seller Center chỉ cho chọn khoảng 90 ngày gần nhất.

## 8. Dựng báo cáo

1. Chuẩn bị: `top_gmvmax.json` (bước 1), `hooks.json` (bước 7), thư mục `strips/` (bước 6), `report_data.json` (theo `assets/report_data.example.json`).
2. `python scripts/build_report.py --data report_data.json --top top_gmvmax.json --hooks hooks.json --strips strips --out report.html`
3. Kiểm tra: không còn `{{...}}`, đủ số thẻ video, GMV khớp GMV Max.
4. Đăng bằng Artifact. Cập nhật thì đăng lại cùng file path để giữ link.

## 9. Lỗi thường gặp

| Tình huống | Cách xử lý |
|---|---|
| CAPTCHA TikTok | Nhờ người dùng tự giải |
| Landing page 404 / "chưa xuất bản" | Báo ngay, đây là lỗi nghiêm trọng |
| Trang video TikTok lỗi, player nhúng không phát | Chuyển sang cách A hoặc B ở bước 6 |
| `gmv_max_video_get` trả rỗng với KOC | Creator chưa hoặc hết ủy quyền: cách B hoặc C |
| GMV Max treo khi gõ tìm kiếm | Tải lại trang, focus bằng JS, mỗi lần 1 ID |
| Seller Center lọc creator không ra | Bộ lọc chỉ hiện creator có dữ liệu trong khoảng ngày đã chọn |
| Chrome không phản hồi | Báo người dùng, làm tiếp phần không cần trình duyệt |
| `browser_batch` mất kết nối | Kiểm tra trạng thái trước khi chạy lại, chia lô nhỏ hơn |
