// Dựng contact sheet ngay trong trang (drawer video của GMV Max, hoặc tab đang mở file mp4).
// Chạy bằng javascript_tool sau khi đã bấm play để video được tải.
// Kết quả: 1 canvas phủ lên đầu trang (id "__cs"), chụp màn hình rồi cắt phần trên cùng.
// Gỡ canvas trước khi sang video khác: document.getElementById('__cs')?.remove()
const v = [...document.querySelectorAll('video')].pop();
v.muted = true;
v.pause();
await new Promise(r => { if (v.readyState >= 2) r(); else v.onloadeddata = r; });
const d = v.duration;
const T = [0, 1, 2, 3, 5, 8, d * 0.5, Math.max(d - 1.5, 0)];
const W = 180, H = 320;
const c = document.createElement('canvas');
c.id = '__cs';
c.width = W * T.length;
c.height = H + 24;
const x = c.getContext('2d');
x.fillStyle = '#fff';
x.fillRect(0, 0, c.width, c.height);
for (let i = 0; i < T.length; i++) {
  await new Promise(r => { v.onseeked = r; v.currentTime = T[i]; });
  await new Promise(r => setTimeout(r, 150));
  x.drawImage(v, i * W, 24, W, H);
  x.fillStyle = '#000';
  x.fillRect(i * W, 24, 44, 18);
  x.fillStyle = '#fff';
  x.font = '13px sans-serif';
  x.fillText(T[i].toFixed(0) + 's', i * W + 4, 38);
}
x.fillStyle = '#000';
x.font = '15px sans-serif';
x.fillText('dur ' + d.toFixed(0) + 's', 4, 17);
c.style.cssText = 'position:fixed;left:0;top:0;width:100vw;z-index:2147483647;background:#fff';
document.body.appendChild(c);
'ok ' + d;
