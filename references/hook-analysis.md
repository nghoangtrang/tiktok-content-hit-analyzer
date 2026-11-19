# Phân tích hook hình ảnh và khung hình

## Ghi cho mỗi video (lưu vào hooks.json)

| Trường | Nội dung |
|---|---|
| `vh` | Hook hình ảnh 0–3s: trong khung có gì, chuyển động gì |
| `ht` | Loại hook (xem 7 loại bên dưới + các loại hình ảnh: cảm giác chạm, size gap, hành động, giá/ưu đãi) |
| `frame` | Bố cục: góc máy, sản phẩm chiếm bao nhiêu khung, banner/chữ ở đâu, cảnh cắt ở giây nào |
| `fmt` | Loại video + âm thanh (voice / nhạc / ASMR) |
| `act` | Việc nên làm: giữ gì, sửa gì, đưa cảnh nào lên sớm hơn |

Video chưa xem được frame: ghi `"(Chưa có contact sheet) ..."` và chỉ dựa vào lời thoại.

## Skill dùng và điều lấy từ mỗi skill

| Skill | Áp dụng |
|---|---|
| `tiktok-creative-playbook` | 7 loại hook: sự thật bị giấu, câu hỏi tò mò, cảnh báo nỗi đau, câu chuyện cá nhân, con số gây sốc, đồng cảm nhu cầu, chủ đề tranh luận. Loại video Commerce: Product Demonstration (ROI tốt nhất), Scenario Based (CTR tốt nhất), Display (tương tác tốt nhất). Body cần 4–6 sellpoint. Âm thanh: voice-over / BGM / ASMR |
| `tt-ads-creative-strategy-diagnosis` | Cây GMV/ROAS. Hook-rate cao, CVR thấp → giữ hook, viết lại giữa và cuối. Người xem rơi trước giây 3 → sản phẩm hoặc nỗi đau phải có ở giây đầu. Đỉnh click sau giây 5 → kéo lên 0–3s. Đỉnh chuyển đổi sau giây 10 → đưa bằng chứng/ưu đãi lên giây 3–8. Có đơn mà GMV thấp → nhấn combo, mua nhiều |
| `tt4b-creative-engine` | Hook-rate = xem 2 giây / hiển thị. Thứ tự xếp winner: ROI → CPA → CVR → CTR → hook-rate (chi tiêu chỉ là bối cảnh). Sổ claim: an toàn (khớp PDP), cần kiểm (người bán tự nói, chưa có bằng chứng), chặn (mâu thuẫn PDP hoặc claim y tế) + câu thay thế |
| `lifestyle-durable-goods-growth-diagnosis` | H1 không gian thật, H2 quá trình, H3 chi tiết đúng mẫu, H4 món lẻ hay phối bộ, H5 cách mở đầu (bừa bộn hoặc kết quả trước đều hợp lệ), H6 bước tiếp theo/CTA |
| `creative-asset-lifecycle-optimizer` | Chỉ nói "hook yếu" khi đã xem nội dung. Gắn nhãn quan sát / giả thuyết / cần xác minh. Không kết luận nhân quả khi không có đối chứng |

Tra ngưỡng nhanh: file tổng hợp 59 skill (sheet "Ngưỡng & con số", "Chọn skill theo câu hỏi") nếu có.

## Gom quy luật

Chia video theo nhóm hook/format, tính số liệu nhóm (số video, tổng GMV, ROI nhóm = tổng GMV / tổng cost, hook-rate và CVR trung bình). Các câu hỏi nên trả lời:
- Video GMV cao nhất mở đầu thế nào? Sản phẩm có trong khung ở giây 0 không?
- Nhóm hook-rate cao có CVR cao không? Nếu không → giữ hook, sửa thân.
- Inhouse và KOC khác nhau ở bố cục nào (banner, góc máy, bối cảnh)?
- Video có đơn = 0 thiếu gì ở cuối (CTA, giá)?
- Frame by frame của video top: click đỉnh ở giây nào, người xem rơi ở giây nào?

## Khung kịch bản cho brief (mẫu, chỉnh theo sản phẩm)

| Thời điểm | Nội dung |
|---|---|
| 0–1s · Hình | Người dùng sản phẩm, sản phẩm chiếm 50–60% khung, title tên sản phẩm. Không banner sale ở trên |
| 1–3s · Lời | 1 câu so sánh hoặc nỗi đau |
| 3–8s · Bằng chứng | Size gap, macro chất liệu, demo độ bền/độ phồng |
| 8–12s · Ưu đãi | Combo, giá, quà, ở 1/3 dưới khung |
| Cuối · CTA | "Bấm giỏ hàng góc trái", không kết bằng logo trơn |

## Mốc màu trên thẻ video

Xanh / đỏ là so sánh nội bộ trong tập video, không phải chuẩn ngành. Mặc định trong `build_report.py`: hook 2s ≥25% / ≤12%, xem 6s ≥12% / ≤4%, CTR ≥4% / ≤1,5%, CVR ≥5% / ≤2%. Đổi trong `report_data.json` (`thresholds`) nếu tập video khác hẳn.
