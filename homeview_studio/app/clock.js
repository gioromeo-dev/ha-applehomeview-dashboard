// Clock face renderer shared by the editor preview and the dashboard.
// Inputs (defined by the caller): d (Date), STYLE, ACC (accent), FG (foreground), W (viewBox width; height is 100), BG (fill background with ACC)
const H = 100, cx = W / 2, cy = 50, R = Math.min(W, H) / 2;
const hh = d.getHours(), mm = d.getMinutes();
const sec = hh % 12 * 3600 + mm * 60 + d.getSeconds() + d.getMilliseconds() / 1000;
const pad = (n) => String(n).padStart(2, '0');
const FONT = "ui-rounded, 'SF Pro Rounded', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif";
const spin = (p) => `transform-origin:${cx}px ${cy}px;animation:hvspin ${p}s linear infinite;animation-delay:-${(sec % p).toFixed(2)}s`;
const hand = (len, w, col, p, tail) => `<g style="${spin(p)}"><line x1="${cx}" y1="${cy + (tail || 0)}" x2="${cx}" y2="${cy - len}" stroke="${col}" stroke-width="${w}" stroke-linecap="round"/></g>`;
const pt = (deg, r) => { const a = deg * Math.PI / 180; return [cx + r * Math.sin(a), cy - r * Math.cos(a)]; };
const txt = (t, x, y, size, weight, fill, extra) => `<text x="${x.toFixed(2)}" y="${y.toFixed(2)}" text-anchor="middle" dominant-baseline="central" font-size="${size}" font-weight="${weight}" fill="${fill}" ${extra || ''}>${t}</text>`;
const dateStr = d.toLocaleDateString('it-IT', {weekday: 'long', day: 'numeric', month: 'long'});
const short = d.toLocaleDateString('it-IT', {weekday: 'short'}).toUpperCase().replace('.', '') + ' ' + d.getDate();
const SEC = '#FF9F0A';
let s = '';
if (STYLE === 'classic') {
  for (let i = 0; i < 60; i++) {
    const big = i % 5 === 0, [x1, y1] = pt(i * 6, R * (big ? 0.86 : 0.9)), [x2, y2] = pt(i * 6, R * 0.95);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${FG}" stroke-opacity="${big ? 0.9 : 0.4}" stroke-width="${R * (big ? 0.028 : 0.014)}" stroke-linecap="round"/>`;
  }
  for (let h = 1; h <= 12; h++) { const [x, y] = pt(h * 30, R * 0.71); s += txt(h, x, y, R * 0.22, 500, FG); }
  s += hand(R * 0.44, R * 0.072, FG, 43200) + hand(R * 0.74, R * 0.052, FG, 3600) + hand(R * 0.84, R * 0.024, SEC, 60, R * 0.16);
  s += `<circle cx="${cx}" cy="${cy}" r="${R * 0.052}" fill="${FG}"/><circle cx="${cx}" cy="${cy}" r="${R * 0.024}" fill="${SEC}"/>`;
} else if (STYLE === 'minimal') {
  for (let i = 0; i < 12; i++) {
    const [x1, y1] = pt(i * 30, R * (i % 3 ? 0.88 : 0.8)), [x2, y2] = pt(i * 30, R * 0.95);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${FG}" stroke-opacity="${i % 3 ? 0.5 : 1}" stroke-width="${R * 0.03}" stroke-linecap="round"/>`;
  }
  s += hand(R * 0.5, R * 0.06, FG, 43200) + hand(R * 0.8, R * 0.04, FG, 3600) + hand(R * 0.86, R * 0.016, ACC === FG ? SEC : ACC, 60, R * 0.12);
  s += `<circle cx="${cx}" cy="${cy}" r="${R * 0.04}" fill="${FG}"/>`;
} else if (STYLE === 'bold') {
  const wide = W >= H * 1.2, fs = wide ? R * 1.12 : R * 0.5;
  const dx = wide ? Math.min(R * 0.72, R * 0.6 + (W - H) * 0.15) : R * 0.7, y12 = wide ? R * 0.5 : R * 0.68, y6 = wide ? R * 0.54 : R * 0.7;
  s += txt('12', cx, cy - y12, fs, 300, FG, 'letter-spacing="-1"') + txt('3', cx + dx, cy + R * 0.02, fs, 300, FG)
     + txt('6', cx + 1, cy + y6, fs, 300, FG) + txt('9', cx - dx, cy + R * 0.02, fs, 300, FG);
  s += `<g style="filter:drop-shadow(0 0.4px 0.8px rgba(0,0,0,0.35))">${hand(R * 0.5, R * 0.064, '#FFFFFF', 43200, R * 0.12)}${hand(R * 0.78, R * 0.064, '#FFFFFF', 3600, R * 0.12)}</g>`;
  s += hand(R * 0.94, R * 0.01, '#FFFFFF', 60, R * 0.16) + `<circle cx="${cx}" cy="${cy}" r="${R * 0.042}" fill="#FFFFFF"/>`;
  s += `<text x="${W * 0.05}" y="${H * 0.94}" fill="${FG}" font-size="${R * 0.092}" font-weight="700" letter-spacing="0.2">${short}</text>`;
} else if (STYLE === 'digital') {
  s += txt(`${pad(hh)}:${pad(mm)}`, cx, cy - R * 0.06, R * 0.62, 600, FG, 'letter-spacing="-1" font-variant-numeric="tabular-nums"');
  s += txt(dateStr.charAt(0).toUpperCase() + dateStr.slice(1), cx, cy + R * 0.48, R * 0.13, 500, FG, 'fill-opacity="0.75"');
} else if (STYLE === 'stacked') {
  s += txt(pad(hh), cx, cy - R * 0.43, R * 0.92, 700, FG, 'letter-spacing="-2"');
  s += txt(pad(mm), cx, cy + R * 0.47, R * 0.92, 700, ACC === FG ? SEC : ACC, 'letter-spacing="-2"');
} else if (STYLE === 'solar') {
  const r = R * 0.86, frac = (hh * 60 + mm) / 1440, a = frac * 360 + 180;
  s += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${FG}" stroke-opacity="0.18" stroke-width="${R * 0.05}"/>`;
  const [ex, ey] = pt(a, r), large = frac > 0.5 ? 1 : 0, [sx, sy] = pt(180, r);
  s += `<path d="M ${sx} ${sy} A ${r} ${r} 0 ${large} 1 ${ex} ${ey}" fill="none" stroke="${ACC === FG ? SEC : ACC}" stroke-width="${R * 0.05}" stroke-linecap="round"/>`;
  s += `<circle cx="${ex}" cy="${ey}" r="${R * 0.09}" fill="#FFD60A" style="filter:drop-shadow(0 0 ${R * 0.06}px #FFD60A)"/>`;
  for (const [h, lbl] of [[0, '0'], [6, '6'], [12, '12'], [18, '18']]) { const [x, y] = pt(h * 15 + 180, r * 0.8); s += txt(lbl, x, y, R * 0.1, 600, FG, 'fill-opacity="0.55"'); }
  s += txt(`${pad(hh)}:${pad(mm)}`, cx, cy, R * 0.36, 600, FG, 'font-variant-numeric="tabular-nums"');
}
return `<svg viewBox="0 0 ${W.toFixed(2)} ${H}" preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%;display:block;font-family:${FONT}">
  <style>@keyframes hvspin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}</style>
  ${BG ? `<rect x="0" y="0" width="${W}" height="${H}" fill="${ACC}"/>` : ''}${s}</svg>`;
