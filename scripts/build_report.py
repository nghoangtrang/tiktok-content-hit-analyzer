"""Dựng báo cáo HTML từ dữ liệu đã chuẩn bị.

  python build_report.py --data report_data.json --top top_gmvmax.json --hooks hooks.json \
                         --strips strips --out report.html [--template ../assets/report_template.html]

- report_data.json: nội dung báo cáo (khung 25 ô, idea, nhận định). Xem assets/report_data.example.json.
- top_gmvmax.json: đầu ra của aggregate_gmvmax.py.
- hooks.json: {item_id: {vh, ht, frame, fmt, act}} ghi chú hook từng video.
- strips/: ảnh dải frame <item_id>.jpg (contact_sheet.py hoặc cắt từ ảnh chụp trình duyệt).
Các trường dạng danh sách trong report_data.json được phép chứa HTML (ví dụ <b>...</b>).
"""
import argparse, base64, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LAYOUT = [['C1', 'S1', 'C2', 'S2', 'C3'], ['S3', 'U1', 'U2', 'U3', 'S4'],
                  ['C4', 'U4', 'PRD', 'U5', 'S5'], ['S6', 'U6', 'U7', 'U8', 'C5'],
                  ['C6', 'S7', 'C7', 'S8', 'C8']]
DEFAULT_TH = {'v2': [25, 12], 'v6': [12, 4], 'ctr': [4, 1.5], 'cvr': [5, 2]}
E = html.escape

def fm(x):
    return f"{x/1e6:,.1f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def pc(x):
    return f"{x:.1f}".replace('.', ',') + '%'

def num(x):
    return f"{x:.1f}".replace('.', ',')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--top', required=True)
    ap.add_argument('--hooks', required=True)
    ap.add_argument('--strips', default='strips')
    ap.add_argument('--out', required=True)
    ap.add_argument('--template', default=os.path.join(HERE, '..', 'assets', 'report_template.html'))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    D = json.load(open(a.data, encoding='utf-8'))
    T = json.load(open(a.top, encoding='utf-8'))
    H = json.load(open(a.hooks, encoding='utf-8'))
    tpl = open(a.template, encoding='utf-8').read()
    TH = {**DEFAULT_TH, **D.get('thresholds', {})}
    skip = set(D.get('skip_ids', []))

    V = {}
    for src in ('ih', 'koc'):
        for k, o in enumerate(T[src], 1):
            o.setdefault('rank', k)
            o['src'] = src
            V[o['id']] = o
    idea_of = {}
    for k, lst in D.get('idea_videos', {}).items():
        for i in lst:
            idea_of[i] = int(k)
    for i in D.get('other', {}).get('videos', []):
        idea_of[i] = 0

    # --- Phần 1: khung 25 ô
    cells = D['cells']
    grid = ''
    for r in D.get('layout', DEFAULT_LAYOUT):
        for c in r:
            t, s = cells[c]
            cls = 'p' if c == 'PRD' else c[0].lower()
            grid += f'<div class="cell {cls}" data-c="{c}" title="{E(s)}"><span class="code">{c}</span><span class="name">{E(t)}</span></div>'

    def legend(prefix):
        return ''.join(f'<li><span class="chip {prefix.lower()}">{k}</span><div><b>{E(t)}</b><span>{E(s)}</span></div></li>'
                       for k, (t, s) in cells.items() if k.startswith(prefix) and k != 'PRD')

    # --- Phần 2: idea
    def vlink(i):
        v = V[i]
        tag = 'IH' if v['src'] == 'ih' else 'KOC'
        return (f'<a class="vid {tag.lower()}" href="https://www.tiktok.com/@{v["user"]}/video/{i}" target="_blank" rel="noopener">'
                f'<span class="vt">{tag} #{v["rank"]}</span> {E(v["user"])} <b>{fm(v["gmv"])}tr</b></a>')

    rows = []
    for idea in D['ideas']:
        n, cs = idea['id'], idea['cells']
        vids = [i for i in D.get('idea_videos', {}).get(str(n), []) if i in V]
        g = sum(V[i]['gmv'] for i in vids)
        nih = sum(1 for i in vids if V[i]['src'] == 'ih')
        nk = len(vids) - nih
        if idea.get('gap') or not vids:
            st = '<span class="pill gap">Chưa có, cần sản xuất</span>'
        elif nk == 0:
            st = '<span class="pill thin">Chỉ có Inhouse, chưa có KOC</span>'
        elif nih == 0:
            st = '<span class="pill thin">Chỉ có KOC, chưa có Inhouse</span>'
        elif len(vids) <= 2:
            st = '<span class="pill thin">Mỏng, cần thêm</span>'
        else:
            st = '<span class="pill ok">Đã có, nhân bản biến thể</span>'
        chips = ''.join(f'<span class="chip {c[0].lower()}">{c}</span>' for c in cs)
        vh = ''.join(vlink(i) for i in sorted(vids, key=lambda i: -V[i]['gmv'])) or '<span class="none">Chưa có creative trong top</span>'
        rows.append(f'<tr data-cells="{" ".join(cs + ["PRD"])}" tabindex="0"><td class="num">{n}</td>'
                    f'<td><div class="chips">{chips}<span class="chip p">PRD</span></div></td>'
                    f'<td class="ti"><strong>{E(idea["title"])}</strong><p>{E(idea["hook"])}</p></td>'
                    f'<td class="vids">{vh}</td><td class="num gmv">{fm(g) if g else "–"}</td><td>{st}</td></tr>')
    other = D.get('other')
    if other and other.get('videos'):
        ov = [i for i in other['videos'] if i in V]
        rows.append(f'<tr data-cells="PRD" tabindex="0"><td class="num">–</td><td><div class="chips"><span class="chip p">PRD</span></div></td>'
                    f'<td class="ti"><strong>{E(other["title"])}</strong><p>{E(other["desc"])}</p></td>'
                    f'<td class="vids">{"".join(vlink(i) for i in ov)}</td><td class="num gmv">{fm(sum(V[i]["gmv"] for i in ov))}</td>'
                    f'<td><span class="pill thin">Tham khảo</span></td></tr>')

    pb = D.get('playbook', {})
    playbook = ('<div class="two"><div class="card"><h3>Nhân bản (20%): biến thể của idea đã thắng</h3><ul class="plain">'
                + ''.join(f'<li>{x}</li>' for x in pb.get('replicate', []))
                + '</ul></div><div class="card"><h3>Ý tưởng mới (80%): ưu tiên sản xuất</h3><ul class="plain">'
                + ''.join(f'<li>{x}</li>' for x in pb.get('new', [])) + '</ul></div></div>')

    # --- Phần 3: bảng top
    def vtable(src):
        out = []
        for o in T[src]:
            n = idea_of.get(o['id'])
            lab = f'Idea {n}' if n else ('Ngoài khung' if n == 0 else '–')
            roi = o['gmv'] / o['cost'] if o.get('cost') else 0
            out.append(f'<tr><td class="num">{o["rank"]}</td><td><a href="https://www.tiktok.com/@{o["user"]}/video/{o["id"]}" target="_blank" rel="noopener">{E(o["user"])}</a>'
                       f'<span class="cap">{E(o.get("cap", ""))}</span></td><td class="num">{fm(o["gmv"])}</td><td class="num">{int(o["orders"])}</td>'
                       f'<td class="num">{roi:.2f}</td><td class="num">{pc(o["ctr"])}</td><td class="num">{pc(o["cvr"])}</td><td><span class="ideatag">{lab}</span></td></tr>')
        return '\n'.join(out)

    # --- Phần 4: thẻ video
    def chip(lbl, key, val):
        hi, lo = TH[key]
        cls = ' class="hi"' if val >= hi else (' class="lo"' if val <= lo else '')
        return f'<span{cls}>{lbl} {pc(val)}</span>'

    def card(o):
        i = o['id']
        h = H.get(i, {})
        roi = o['gmv'] / o['cost'] if o.get('cost') else 0
        p = os.path.join(a.strips, i + '.jpg')
        if os.path.exists(p):
            b64 = base64.b64encode(open(p, 'rb').read()).decode()
            strip = (f'<div class="strip"><img loading="lazy" alt="Contact sheet video {i}: các mốc 0, 1, 2, 3, 5, 8 giây, giữa và cuối video" '
                     f'src="data:image/jpeg;base64,{b64}"></div>')
        else:
            strip = '<div class="strip"><span class="none">Chưa có contact sheet cho video này.</span></div>'
        met = (f'<span>GMV {fm(o["gmv"])} tr</span>' + chip('Hook 2s', 'v2', o['v2']) + chip('Xem 6s', 'v6', o['v6'])
               + chip('CTR', 'ctr', o['ctr']) + chip('CVR', 'cvr', o['cvr']) + f'<span>ROI {num(roi)}</span>')
        kv = ''.join(f'<dt>{lbl}</dt><dd>{E(h.get(k, "–"))}</dd>' for lbl, k in
                     [('Hook hình ảnh 0–3s', 'vh'), ('Loại hook', 'ht'), ('Khung hình', 'frame'), ('Format · âm thanh', 'fmt'), ('Hành động', 'act')])
        return (f'<article class="vcard" data-src="{o["src"]}"><div class="vhead"><b>{"Inhouse" if o["src"] == "ih" else "KOC"} #{o["rank"]}</b>'
                f'<a class="who" href="https://www.tiktok.com/@{o["user"]}/video/{i}" target="_blank" rel="noopener">@{E(o["user"])} · {i}</a></div>'
                f'<div class="met">{met}</div>{strip}<dl class="kv">{kv}</dl></article>')

    shown = [o for o in T['ih'] + T['koc'] if o['id'] not in skip]
    cards = '\n'.join(card(o) for o in shown)
    sb = ''.join(f'<div><span class="t">{E(s["t"])}</span>{s["body"]}<span>{s.get("ref", "")}</span></div>' for s in D.get('storyboard', []))
    claims = ''.join(f'<tr><td><span class="pill {c["level"]}">{E(c["label"])}</span></td><td>{E(c["text"])}</td><td>{E(c["reason"])}</td><td>{E(c["alt"])}</td></tr>'
                     for c in D.get('claims', []))
    th_note = (f'hook 2s ≥{num(TH["v2"][0])}% / ≤{num(TH["v2"][1])}%, CTR ≥{num(TH["ctr"][0])}% / ≤{num(TH["ctr"][1])}%, '
               f'CVR ≥{num(TH["cvr"][0])}% / ≤{num(TH["cvr"][1])}%')

    rep = {
        'PAGE_TITLE': E(D['page_title']), 'EYEBROW': E(D['eyebrow']), 'TITLE': E(D['title']), 'LEDE': D['lede'],
        'TAKEAWAYS': ''.join(f'<div><b>{E(t["big"])}</b><span>{t["text"]}</span></div>' for t in D.get('takeaways', [])),
        'GRID': grid, 'LEG_U': legend('U'), 'LEG_C': legend('C'), 'LEG_S': legend('S'),
        'IDEA_LEDE': D.get('idea_lede', ''), 'ROWS': '\n'.join(rows), 'PLAYBOOK_CARDS': playbook,
        'INHOUSE_NAME': E(D.get('inhouse_name', 'Inhouse')), 'TAB_IH': vtable('ih'), 'TAB_KOC': vtable('koc'),
        'TOP_NOTE': D.get('top_note', ''), 'HOOK_LEDE': D.get('hook_lede', ''),
        'OBSERVATIONS': ''.join(f'<li>{x}</li>' for x in D.get('observations', [])),
        'RULES': ''.join(f'<li>{x}</li>' for x in D.get('rules', [])),
        'STORYBOARD': sb, 'CLAIMS': claims,
        'N_ALL': str(len(shown)), 'N_IH': str(sum(o['src'] == 'ih' for o in shown)), 'N_KOC': str(sum(o['src'] == 'koc' for o in shown)),
        'THRESH_NOTE': th_note, 'SKIP_NOTE': D.get('skip_note', ''), 'CARDS': cards, 'SOURCE_NOTE': D.get('source_note', ''),
    }
    out = tpl
    for k, v in rep.items():
        out = out.replace('{{' + k + '}}', v)
    left = [s for s in set(__import__('re').findall(r'\{\{[A-Z_]+\}\}', out))]
    if left:
        sys.exit(f'Còn placeholder chưa điền: {left}')
    open(a.out, 'w', encoding='utf-8').write(out)
    print(f'ok {a.out} · {len(out)//1024} KB · {len(shown)} thẻ video')

if __name__ == '__main__':
    main()
