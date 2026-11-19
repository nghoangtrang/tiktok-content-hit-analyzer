# Skill TikTok Ads cần cài riêng

5 file zip trong thư mục này là **skill độc lập** của bộ TikTok Ads, không phải một phần của framework `tiktok-content-hit-analyzer`. Framework chỉ gọi tên chúng ở bước phân tích hook (xem `../references/hook-analysis.md`). Mỗi skill phải được cài riêng.

| File | Skill | Dùng trong framework để |
|---|---|---|
| `tiktok-creative-playbook.zip` | tiktok-creative-playbook | 7 loại hook, loại video (Demo / Scenario / Display), 4–6 sellpoint, âm thanh |
| `tt-ads-creative-strategy-diagnosis.zip` | tt-ads-creative-strategy-diagnosis | Hook-rate cao CVR thấp thì giữ hook sửa thân; người xem rơi trước giây 3; đỉnh click sau giây 5 |
| `tt4b-creative-engine.zip` | tt4b-creative-engine | Hook-rate = xem 2 giây / hiển thị; thứ tự xếp video thắng; sổ claim |
| `lifestyle-durable-goods-growth-diagnosis.zip` | lifestyle-durable-goods-growth-diagnosis | Checklist ngành nội thất/nệm: không gian, chi tiết, mở đầu, CTA |
| `creative-asset-lifecycle-optimizer.zip` | creative-asset-lifecycle-optimizer | Tách quan sát / giả thuyết, không kết luận nhân quả khi không có đối chứng |

## Cách cài

**Claude Code**: giải nén từng file vào thư mục skill, mỗi skill một thư mục riêng:
```bash
unzip tiktok-creative-playbook.zip -d ~/.claude/skills/
```
Lặp lại cho 4 file còn lại. Sau khi giải nén sẽ có `~/.claude/skills/tiktok-creative-playbook/SKILL.md`, …

**Claude app (claude.ai / desktop)**: vào Settings → Capabilities → Skills → Upload skill, chọn lần lượt từng file zip.

## Lưu ý

- Các skill này đọc dữ liệu tài khoản qua MCP TikTok Business API. Chỉ đọc, không tự thay đổi quảng cáo.
- Đây là skill do bên thứ ba phát hành. Trước khi để repo ở chế độ public, kiểm tra điều khoản phân phối lại của các skill này. Nếu không chắc, giữ repo private hoặc bỏ thư mục này và chỉ ghi tên skill để người dùng tự tải.
