---
name: tiktok-content-hit-analyzer
description: Phân tích content của 1 sản phẩm TikTok Shop rồi xuất báo cáo HTML gồm khung 25 ô vuông (PRD, 8 USP, 8 khách hàng, 8 hoàn cảnh), danh sách idea map với top 20 video Inhouse và top 20 video KOC theo GMV của GMV Max, cùng phân tích hook hình ảnh và khung hình có contact sheet từng video. Dùng skill này khi người dùng muốn tìm content hit, xây idea content, làm khung 25 ô, xếp video hiệu quả vào idea, tìm idea chưa có creative, phân tích hook / 3 giây đầu / khung hình / contact sheet của video TikTok, hoặc viết brief cho KOC dựa trên video bán tốt, kể cả khi họ chỉ đưa link sản phẩm TikTok Shop và file export creative mà không nói tên skill.
---

# TikTok Content Hit Analyzer

Skill này biến số liệu GMV Max + video thật của một sản phẩm thành một báo cáo mà team content dùng được ngay: biết idea nào đang bán, idea nào còn trống, và 3 giây đầu của video thắng trông như thế nào.

## Output

Một trang HTML (đăng bằng Artifact nếu có) gồm 4 phần:
1. **Khung 25 ô**: PRD ở giữa, vòng trong 8 USP, vòng ngoài xen kẽ 8 khách hàng (C) và 8 hoàn cảnh (S). Bấm vào idea thì sáng các ô tạo nên idea.
2. **Idea**: mỗi idea = C + S + 1–2 U + PRD, kèm video đang có, tổng GMV và trạng thái (đã có / mỏng / chưa có, cần sản xuất). Thêm 2 khối "Nhân bản 20%" và "Ý tưởng mới 80%".
3. **Top 20 Inhouse + top 20 KOC** theo GMV GMV Max, kèm đơn, ROI, CTR, CVR, idea được xếp.
4. **Hook hình ảnh và khung hình**: quy luật chung, khung kịch bản cho brief, sổ claim, và thẻ từng video (contact sheet + chỉ số + ghi chú).

## Đầu vào cần hỏi người dùng (nếu thiếu)

- SPU ID, link PDP TikTok Shop, khoảng thời gian.
- Tên kênh Inhouse (các kênh còn lại là KOC).
- File phân tích content hit cũ (nếu có). Phương pháp 25 ô đã nằm đầy đủ trong `references/grid-25.md`, không cần xin tài liệu gốc.
- File Excel export creative từ GMV Max (để gắn username, vì API không trả tên tài khoản ở cấp video).
- Danh sách creator không có quyền dùng hình ảnh: các video này không làm contact sheet và không đưa vào phần 4.
- Cấu hình tài khoản TikTok Ads: xem `config.example.json`, người dùng điền vào `config.local.json` (không commit).

## Quy trình (tóm tắt)

Đọc `references/sop.md` để biết chi tiết từng bước, lệnh API và cách xử lý lỗi.

1. **Số liệu GMV Max** qua MCP TikTok Business (`gmv_max_report_get` cấp item_id) → chạy `scripts/aggregate_gmvmax.py` để cộng theo video, gắn username, xếp top 20 mỗi bên.
2. **Tài liệu nội bộ** (nếu có): file content hit cũ trên Google Drive, để biết team đã nhận định gì.
3. **PDP**: đọc bằng Chrome; nguồn USP và nguồn kiểm claim. Gặp CAPTCHA thì nhờ người dùng tự giải.
4. **Lời thoại**: phụ đề tự động trên trang video TikTok.
5. **Khung 25 ô và idea**: đọc `references/grid-25.md` (framework đầy đủ: tư duy 80/20, cấu trúc, cách điền ô, ghép và lọc idea, 2 ví dụ).
6. **Contact sheet**: lấy mp4 qua `gmv_max_video_get` → `scripts/contact_sheet.py`. Nếu KOC hết ủy quyền thì dùng `scripts/browser_contact_sheet.js` trong trình phát GMV Max, hoặc xin người dùng link mp4.
7. **Phân tích hook và khung hình**: theo `references/hook-analysis.md`, dùng 5 skill TikTok Ads cài riêng (bản cài nằm trong thư mục `required-skills/`). Nếu chưa có skill nào thì nhắc người dùng cài, trong lúc đó vẫn phân tích theo tóm tắt quy tắc trong `hook-analysis.md`.
8. **Dựng báo cáo**: điền `report_data.json` theo `assets/report_data.example.json` → chạy `scripts/build_report.py` → đăng Artifact.

## Nguyên tắc

- **Không bịa số liệu.** Mọi con số lấy từ GMV Max, file export hoặc PDP. Mốc xanh/đỏ trên chỉ số là so sánh nội bộ trong tập video, không gọi là chuẩn ngành.
- **Chỉ nhận xét hình ảnh khi đã xem frame.** Video chưa có contact sheet thì ghi rõ "chưa xem được hình", tách quan sát với giả thuyết.
- **Dừng lại hỏi** khi gặp CAPTCHA, trang lỗi, thiếu quyền. Không tự vượt qua cơ chế bảo vệ.
- **Báo danh sách video còn thiếu contact sheet** trước khi chuyển sang cách lấy video khác, vì người dùng thường lấy link nhanh hơn.
- **Tôn trọng quyền hình ảnh**: không nhúng frame của creator nằm trong danh sách loại trừ.
- Viết tiếng Việt, câu ngắn, cho team content đọc. Cuối cùng gửi link báo cáo và 5–7 phát hiện chính.
