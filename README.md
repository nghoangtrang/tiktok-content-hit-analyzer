# TikTok Content Hit Analyzer

Skill cho Claude (Claude Code / Claude app) để phân tích content của 1 sản phẩm TikTok Shop và xuất báo cáo HTML gồm:

1. **Khung 25 ô vuông**: PRD, 8 USP, 8 khách hàng, 8 hoàn cảnh.
2. **Idea content** ghép từ khung, map với top video, đánh dấu idea chưa có creative.
3. **Top 20 Inhouse + top 20 KOC** theo GMV của GMV Max.
4. **Phân tích hook hình ảnh và khung hình** với contact sheet từng video, sổ claim và khung kịch bản cho brief.

## Cấu trúc

```
tiktok-content-hit-analyzer/
├── SKILL.md                     # Hướng dẫn chính Claude đọc khi skill được gọi
├── config.example.json          # Mẫu cấu hình tài khoản TikTok Ads (copy thành config.local.json)
├── requirements.txt
├── references/
│   ├── sop.md                   # Quy trình chi tiết, tham số API, xử lý lỗi
│   ├── grid-25.md               # Framework 25 ô đầy đủ (không cần tài liệu gốc)
│   └── hook-analysis.md         # Cách phân tích hook/khung hình và các skill TikTok Ads dùng kèm
├── scripts/
│   ├── aggregate_gmvmax.py      # Cộng GMV Max theo video, xếp top N Inhouse/KOC
│   ├── contact_sheet.py         # Tải mp4, cắt frame 0/1/2/3/5/8s, giữa, cuối
│   ├── browser_contact_sheet.js # Dựng contact sheet trong trình phát GMV Max (video KOC hết ủy quyền)
│   └── build_report.py          # Ghép dữ liệu vào template thành báo cáo HTML
├── assets/
│   ├── report_template.html     # Template báo cáo
│   ├── report_data.example.json # Mẫu nội dung báo cáo
│   └── hooks.example.json       # Mẫu ghi chú hook từng video
└── required-skills/             # 5 skill TikTok Ads cài riêng (không gộp vào framework)
    ├── README.md
    └── *.zip
```

## Cài đặt

1. Copy thư mục này vào thư mục skill của Claude:
   - Claude Code: `~/.claude/skills/tiktok-content-hit-analyzer/` (hoặc `.claude/skills/` trong dự án)
2. `pip install -r requirements.txt` và có sẵn `curl`.
3. `cp config.example.json config.local.json` rồi điền ID tài khoản. File này đã nằm trong `.gitignore`.

## Yêu cầu kết nối

- **MCP TikTok Business API** (đọc GMV Max report, danh sách video GMV Max).
- **Claude in Chrome** (đọc PDP TikTok Shop, lời thoại video, trình phát GMV Max).
- **Google Drive connector** nếu có file content hit cũ trên Google Docs.

Phương pháp 25 ô đã được đóng gói đầy đủ trong `references/grid-25.md`, không cần tài liệu gốc.

## Skill TikTok Ads cần cài riêng

Phần 4 (phân tích hook) dùng 5 skill TikTok Ads. Đây là skill độc lập, **không** nằm trong `SKILL.md` của framework này, nên người dùng phải cài riêng từng cái. Bản cài sẵn để trong thư mục `required-skills/` (xem `required-skills/README.md`):

| Skill | Dùng để |
|---|---|
| `tiktok-creative-playbook` | 7 loại hook, loại video, sellpoint, âm thanh |
| `tt-ads-creative-strategy-diagnosis` | Chẩn đoán theo hook-rate, CTR, CVR và theo từng giây |
| `tt4b-creative-engine` | Hook-rate, xếp video thắng, sổ claim |
| `lifestyle-durable-goods-growth-diagnosis` | Checklist creative ngành nội thất/nệm |
| `creative-asset-lifecycle-optimizer` | Tách quan sát và giả thuyết khi kết luận |

Thiếu skill nào thì framework vẫn chạy được, vì quy tắc chính đã tóm tắt trong `references/hook-analysis.md`. Có đủ skill thì Claude áp quy tắc đầy đủ và chính xác hơn.

## Cách dùng

Gọi bằng lời bình thường, ví dụ:

> Phân tích content cho sản phẩm SPU 1731…, link PDP …, từ 01/08 đến 17/11. Kênh Inhouse là … . Bỏ qua hình ảnh của creator A, B vì chưa có quyền. Làm khung 25 ô, xếp top 20 video mỗi bên vào idea và phân tích hook hình ảnh.

Chạy tay từng script:

```bash
python scripts/aggregate_gmvmax.py --report gmvmax_raw.json --excel export.xlsx --inhouse <kenh_inhouse> --out top_gmvmax.json
python scripts/contact_sheet.py --urls video_urls.json --top top_gmvmax.json --out strips --skip <id1>,<id2>
python scripts/build_report.py --data report_data.json --top top_gmvmax.json --hooks hooks.json --strips strips --out report.html
```

## Lưu ý bảo mật

- Không commit `config.local.json`, file export, video, ảnh frame hay báo cáo đã dựng: các file này chứa ID tài khoản, số liệu doanh thu và hình ảnh của creator. `.gitignore` đã chặn sẵn.
- Nếu repo để public, kiểm tra lại không có ID tài khoản hay số liệu nội bộ trong lịch sử commit.
- Chỉ dùng hình ảnh video của creator đã cấp quyền.
