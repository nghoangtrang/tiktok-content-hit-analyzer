"""Tải video và cắt contact sheet.

  --urls   JSON {item_id: preview_url} (từ gmv_max_video_get) hoặc {item_id: {"url": ...}}
  --top    top_gmvmax.json (từ aggregate_gmvmax.py), để biết thứ tự và tên kênh
  --videos thư mục lưu mp4 (mặc định videos/)
  --out    thư mục lưu dải frame mỗi video (mặc định strips/)
  --skip   các item_id không làm (creator không có quyền hình ảnh), cách nhau dấu phẩy

Mỗi video ra 1 dải 8 frame: 0, 1, 2, 3, 5, 8 giây, giữa video, cuối video - 1,5 giây.
Thêm các file sheet_XX.jpg (4 video/sheet) để xem nhanh.
Cần: Python 3, opencv-python, numpy, curl.
"""
import argparse, json, os, subprocess
import cv2
import numpy as np

TS = [0, 1, 2, 3, 5, 8]
W, H = 150, 267

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--urls', required=True)
    ap.add_argument('--top', required=True)
    ap.add_argument('--videos', default='videos')
    ap.add_argument('--out', default='strips')
    ap.add_argument('--skip', default='')
    a = ap.parse_args()
    os.makedirs(a.videos, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    skip = {s.strip() for s in a.skip.split(',') if s.strip()}

    urls = json.load(open(a.urls, encoding='utf-8'))
    urls = {k: (v['url'] if isinstance(v, dict) else v) for k, v in urls.items()}
    T = json.load(open(a.top, encoding='utf-8'))
    order = [('IH', o) for o in T['ih']] + [('KOC', o) for o in T['koc']]

    rows, missing = [], []
    for src, o in order:
        i = o['id']
        if i in skip:
            continue
        p = os.path.join(a.videos, i + '.mp4')
        if not (os.path.exists(p) and os.path.getsize(p) > 10000):
            if i not in urls:
                missing.append(f"{src}#{o['rank']} {o['user']} {i}")
                continue
            subprocess.run(['curl', '-s', '-L', '-A', 'Mozilla/5.0', '-o', p, urls[i]], timeout=180)
        cap = cv2.VideoCapture(p)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        tiles = []
        for t in TS + [dur * 0.5, max(dur - 1.5, 0)]:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, fr = cap.read()
            fr = cv2.resize(fr, (W, H)) if ok else np.zeros((H, W, 3), np.uint8)
            cv2.rectangle(fr, (0, 0), (40, 16), (0, 0, 0), -1)
            cv2.putText(fr, f'{t:.0f}s', (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            tiles.append(fr)
        strip = np.hstack(tiles)
        cv2.imwrite(os.path.join(a.out, i + '.jpg'), strip, [cv2.IMWRITE_JPEG_QUALITY, 72])
        head = np.full((22, strip.shape[1], 3), 255, np.uint8)
        cv2.putText(head, f"{src}#{o['rank']} {o['user']} {i} {dur:.0f}s", (4, 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        rows.append(np.vstack([head, strip]))
        print(f"ok {src}#{o['rank']} {i} {dur:.0f}s", flush=True)

    for b in range(0, len(rows), 4):
        cv2.imwrite(os.path.join(a.out, f'sheet_{b // 4:02d}.jpg'), np.vstack(rows[b:b + 4]),
                    [cv2.IMWRITE_JPEG_QUALITY, 80])
    if missing:
        print('\nChưa có link video (cần cách B hoặc C):')
        print('\n'.join('  ' + m for m in missing))

if __name__ == '__main__':
    main()
