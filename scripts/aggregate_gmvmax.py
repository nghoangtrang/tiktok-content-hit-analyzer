"""Cộng số liệu GMV Max theo video và xếp top N Inhouse / KOC.

Đầu vào:
  --report  file JSON trả về từ gmv_max_report_get (dimensions campaign_id, item_group_id, item_id).
            Có thể truyền nhiều file (nhiều trang).
  --excel   file Excel export creative từ GMV Max (cột "ID video", "Tên người dùng", "Tiêu đề video", "Doanh thu gộp").
  --inhouse username kênh Inhouse (có thể truyền nhiều, cách nhau dấu phẩy).
  --top     số video mỗi bên (mặc định 20).
  --out     file JSON đầu ra.

Đầu ra: {"ih": [...], "koc": [...]} mỗi phần tử có id, user, gmv, cost, orders, imp, clk,
ctr, cvr, v2, v6, p25, p50, p100 (tỷ lệ %, lấy theo campaign có nhiều hiển thị nhất), cap.
"""
import argparse, json, sys, collections

def load_report(paths):
    rows = []
    for p in paths:
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, dict) and 'data' in d:
            d = d['data']['list']
        rows += d
    return rows

def load_excel(path):
    if not path:
        return {}
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    h = rows[0]
    return {str(r[0]): dict(zip(h, r)) for r in rows[1:] if r and r[0]}

def f(x):
    try:
        return float(x or 0)
    except ValueError:
        return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', nargs='+', required=True)
    ap.add_argument('--excel')
    ap.add_argument('--inhouse', required=True)
    ap.add_argument('--top', type=int, default=20)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    inhouse = {u.strip() for u in a.inhouse.split(',')}
    rows = load_report(a.report)
    X = load_excel(a.excel)

    agg = collections.defaultdict(collections.Counter)
    best = {}
    for r in rows:
        i = r['dimensions']['item_id']
        m = r['metrics']
        if i == '-1':  # product card, không phải video
            continue
        for k in ['gross_revenue', 'cost', 'orders', 'product_impressions', 'product_clicks']:
            agg[i][k] += f(m.get(k))
        imp = f(m.get('product_impressions'))
        if i not in best or imp > best[i][0]:
            best[i] = (imp, m)

    out, unknown = [], []
    for i, s in agg.items():
        x = X.get(i)
        m = best[i][1]
        o = dict(id=i, user=(x or {}).get('Tên người dùng') or '?',
                 gmv=s['gross_revenue'], cost=s['cost'], orders=s['orders'],
                 imp=s['product_impressions'], clk=s['product_clicks'],
                 ctr=f(m.get('ad_click_rate')), cvr=f(m.get('ad_conversion_rate')),
                 v2=f(m.get('ad_video_view_rate_2s')), v6=f(m.get('ad_video_view_rate_6s')),
                 p25=f(m.get('ad_video_view_rate_p25')), p50=f(m.get('ad_video_view_rate_p50')),
                 p100=f(m.get('ad_video_view_rate_p100')),
                 cap=((x or {}).get('Tiêu đề video') or '').split('#')[0].strip()[:110])
        (unknown if o['user'] == '?' else out).append(o)

    ih = sorted([o for o in out if o['user'] in inhouse], key=lambda o: -o['gmv'])[:a.top]
    koc = sorted([o for o in out if o['user'] not in inhouse], key=lambda o: -o['gmv'])[:a.top]
    for k, o in enumerate(ih, 1): o['rank'] = k; o['src'] = 'ih'
    for k, o in enumerate(koc, 1): o['rank'] = k; o['src'] = 'koc'
    json.dump(dict(ih=ih, koc=koc), open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print(f'{len(agg)} video, Inhouse top {len(ih)}, KOC top {len(koc)}')
    cut = min([o['gmv'] for o in ih][-1:] + [o['gmv'] for o in koc][-1:] or [0])
    risky = sorted([o for o in unknown if o['gmv'] >= cut], key=lambda o: -o['gmv'])
    if risky:
        print('Video chưa rõ chủ kênh nhưng GMV đủ lọt top, cần kiểm tra:')
        for o in risky:
            print(f"  {o['id']}  {o['gmv']/1e6:.1f} tr")

if __name__ == '__main__':
    main()
