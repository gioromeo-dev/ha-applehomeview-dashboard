// Screensaver faces, shared by the editor preview and the dashboard (WallPanel card).
// Inputs (defined by the caller): d (Date), CFG (object), states (hass states map), hass (or null), CLOCK (fn)
const EN = CFG.lang === 'en';
const LOC = EN ? 'en-US' : 'it-IT';
const T = (it, en) => (EN ? en : it);
const W = (CFG.aspect || 1.4) * 100;
const pad = (n) => String(n).padStart(2, '0');
const esc = (t) => String(t == null ? '' : t).replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif";
const faces = (CFG.faces && CFG.faces.length) ? CFG.faces : ['clock'];
const slot = Math.max(10, CFG.interval || 60) * 1000;
const now = d.getTime();
const face = faces[Math.floor(now / slot) % faces.length];
const hhmm = d.toLocaleTimeString(LOC, {hour: '2-digit', minute: '2-digit'});
const dateLong = (() => { const s = d.toLocaleDateString(LOC, {weekday: 'long', day: 'numeric', month: 'long'}); return s.charAt(0).toUpperCase() + s.slice(1); })();
const minuteKey = Math.floor(now / 60000);
const prev = window.__hvFace || {};
const fresh = !CFG.preview && prev.face !== face;
const st = (id) => (states && id && states[id]) || null;

// ---- night mode -------------------------------------------------------------
const toMin = (s) => { const m = /^(\d{1,2}):(\d{2})$/.exec(s || ''); return m ? (+m[1]) * 60 + (+m[2]) : null; };
let night = false;
if (CFG.night && CFG.night.on) {
  const a = toMin(CFG.night.start), b = toMin(CFG.night.end), cur = d.getHours() * 60 + d.getMinutes();
  if (a != null && b != null) night = a <= b ? (cur >= a && cur < b) : (cur >= a || cur < b);
}
const dim = night ? Math.max(0.1, Math.min(1, CFG.night.dim || 0.35)) : 1;
const wrap = (inner, bg, key) => `<div style="position:relative;width:100%;height:100%;overflow:hidden;border-radius:inherit;font-family:${FONT};background:${bg || '#000'};filter:${night ? `brightness(${dim}) sepia(0.35)` : 'none'}">
  <style>@keyframes hvfadein{from{opacity:0}to{opacity:1}}@keyframes hvdrift1{0%{transform:translate(-10%,-6%) scale(1)}50%{transform:translate(12%,8%) scale(1.25)}100%{transform:translate(-10%,-6%) scale(1)}}
  @keyframes hvdrift2{0%{transform:translate(8%,10%) scale(1.1)}50%{transform:translate(-14%,-6%) scale(0.9)}100%{transform:translate(8%,10%) scale(1.1)}}
  @keyframes hvdrift3{0%{transform:translate(0,12%) scale(0.95)}50%{transform:translate(10%,-12%) scale(1.2)}100%{transform:translate(0,12%) scale(0.95)}}</style>
  <div style="position:absolute;inset:0;animation:${fresh ? 'hvfadein 1.2s ease' : 'none'}">${inner}</div></div>`;

// ---- faces ------------------------------------------------------------------
let html = '', key = face, photoIdx = null;
if (face === 'clock') {
  key += '|' + minuteKey;
  html = wrap(CLOCK(d, CFG.clockStyle || 'bold', CFG.accent, CFG.fg, W, true), CFG.accent, key);
}

else if (face === 'photos') {
  window.__hvPh = window.__hvPh || {urls: [], next: 0};
  const P = window.__hvPh;
  if (CFG.photoDir && hass && !P.busy && Date.now() >= P.next) {
    P.busy = true;
    Promise.resolve().then(() => hass.callWS({type: 'media_source/browse_media', media_content_id: CFG.photoDir}))
      .then((r) => Promise.all(((r && r.children) || []).filter((c) => c.media_class === 'image').slice(0, 60)
        .map((c) => hass.callWS({type: 'media_source/resolve_media', media_content_id: c.media_content_id}).then((x) => x.url).catch(() => null))))
      .then((urls) => { P.urls = urls.filter(Boolean); P.next = Date.now() + 3600000; })
      .catch(() => { P.next = Date.now() + 120000; })
      .finally(() => { P.busy = false; });
  }
  const list = (P.urls && P.urls.length) ? P.urls : (CFG.photos || []);
  const per = Math.max(10, CFG.photoInterval || 20) * 1000;
  const i = list.length ? Math.floor(now / per) % list.length : -1;
  photoIdx = i;
  key += '|' + i + '|' + minuteKey;
  const img = i >= 0 ? `<div style="position:absolute;inset:0;background:url('${esc(list[i])}') center/cover no-repeat;animation:${!CFG.preview && prev.photo !== i ? 'hvfadein 1.5s ease' : 'none'}"></div>` : '';
  html = wrap(`${img}<div style="position:absolute;inset:0;background:linear-gradient(to top, rgba(0,0,0,.55), rgba(0,0,0,0) 45%)"></div>
    <div style="position:absolute;left:5%;bottom:6%;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.4)">
      <div style="font-size:15vmin;font-weight:200;line-height:1;letter-spacing:-0.03em">${hhmm}</div>
      <div style="font-size:3.4vmin;font-weight:600;margin-top:1.2vmin">${esc(dateLong)}</div>
      ${i < 0 ? `<div style="font-size:2.6vmin;opacity:.8;margin-top:1vmin">${T('Nessuna foto: aggiungile nella cartella Photo Slideshow o carica degli sfondi', 'No photos: add some to the Photo Slideshow folder or upload wallpapers')}</div>` : ''}
    </div>`, '#111', key);
}

else if (face === 'flow') {
  const m = st(CFG.motion);
  const active = !!(m && m.state === 'on');
  const h = d.getHours();
  // palette drifts through the day: dawn, day, dusk, night
  const pal = h < 6 ? ['#1B2A6B', '#4B2A8A', '#0E5E7A'] : h < 11 ? ['#FF9F6E', '#FF6FA8', '#7FB8FF'] : h < 17 ? ['#3FA9F5', '#7B6CFF', '#2FD3B6'] : h < 21 ? ['#FF7A45', '#C2418F', '#5B4BDB'] : ['#2B3A9E', '#7A2FA0', '#14707F'];
  const sp = active ? 0.45 : 1, op = active ? 0.95 : 0.7;
  const t = (now / 1000);
  const blob = (c, size, x, y, anim, dur) => `<div style="position:absolute;left:${x}%;top:${y}%;width:${size}vmax;height:${size}vmax;margin:-${size / 2}vmax 0 0 -${size / 2}vmax;border-radius:50%;background:radial-gradient(circle, ${c} 0%, ${c}00 68%);opacity:${op};filter:blur(4vmin);animation:${anim} ${dur * sp}s ease-in-out infinite;animation-delay:-${(t % (dur * sp)).toFixed(1)}s"></div>`;
  key += '|' + active + '|' + minuteKey + '|' + pal[0];
  html = wrap(`${blob(pal[0], 75, 30, 35, 'hvdrift1', 26)}${blob(pal[1], 70, 72, 60, 'hvdrift2', 31)}${blob(pal[2], 60, 50, 80, 'hvdrift3', 23)}
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff">
      <div style="font-size:22vmin;font-weight:100;letter-spacing:-0.04em;line-height:1">${hhmm}</div>
      <div style="font-size:3.6vmin;font-weight:500;opacity:.85;margin-top:2vmin">${esc(dateLong)}</div>
    </div>`, '#06070C', key);
}

else if (face === 'meridian') {
  const ang = ((d.getHours() % 12) + d.getMinutes() / 60) * 30;
  const cx = W / 2, cy = 50, R = 38;
  let nums = '';
  for (let n = 1; n <= 12; n++) {
    const a = n * 30, diff = Math.abs(((a - ang + 540) % 360) - 180);
    const o = 0.08 + 0.92 * Math.pow(Math.max(0, Math.cos(diff * Math.PI / 180)), 4);
    const x = cx + R * Math.sin(a * Math.PI / 180), y = cy - R * Math.cos(a * Math.PI / 180);
    nums += `<text x="${x.toFixed(2)}" y="${y.toFixed(2)}" text-anchor="middle" dominant-baseline="central" font-size="${(9 + 5 * o).toFixed(1)}" font-weight="${o > 0.6 ? 500 : 300}" fill="${CFG.fg}" fill-opacity="${o.toFixed(2)}">${n}</text>`;
  }
  const hx = cx + (R - 12) * Math.sin(ang * Math.PI / 180), hy = cy - (R - 12) * Math.cos(ang * Math.PI / 180);
  key += '|' + minuteKey;
  html = wrap(`<svg viewBox="0 0 ${W.toFixed(1)} 100" style="width:100%;height:100%;display:block;font-family:${FONT}">
      <defs><radialGradient id="hvm" cx="50%" cy="45%" r="70%"><stop offset="0%" stop-color="#fff" stop-opacity="0.16"/><stop offset="100%" stop-color="#000" stop-opacity="0.25"/></radialGradient></defs>
      <rect width="${W}" height="100" fill="url(#hvm)"/>
      <line x1="${cx}" y1="${cy}" x2="${hx.toFixed(2)}" y2="${hy.toFixed(2)}" stroke="${CFG.fg}" stroke-opacity="0.35" stroke-width="0.6" stroke-linecap="round"/>
      <circle cx="${cx}" cy="${cy}" r="1.1" fill="${CFG.fg}" fill-opacity="0.6"/>${nums}
      <text x="${cx}" y="${cy + 9}" text-anchor="middle" font-size="3.4" font-weight="600" fill="${CFG.fg}" fill-opacity="0.55">${esc(hhmm)}</text>
    </svg>`, CFG.accent, key);
}

else if (face === 'weather') {
  const w = st(CFG.weather);
  const sun = st('sun.sun');
  const isNight = sun ? sun.state === 'below_horizon' : (d.getHours() < 7 || d.getHours() >= 20);
  const c = w ? w.state : 'unknown';
  const NAMES = EN ? {'clear-night': 'Clear', cloudy: 'Cloudy', exceptional: 'Warning', fog: 'Fog', hail: 'Hail', lightning: 'Thunderstorm', 'lightning-rainy': 'Thunderstorm', partlycloudy: 'Partly cloudy', pouring: 'Pouring', rainy: 'Rain', snowy: 'Snow', 'snowy-rainy': 'Sleet', sunny: 'Sunny', windy: 'Windy', 'windy-variant': 'Windy'}
    : {'clear-night': 'Sereno', cloudy: 'Nuvoloso', exceptional: 'Allerta', fog: 'Nebbia', hail: 'Grandine', lightning: 'Temporale', 'lightning-rainy': 'Temporale', partlycloudy: 'Poco nuvoloso', pouring: 'Pioggia forte', rainy: 'Pioggia', snowy: 'Neve', 'snowy-rainy': 'Nevischio', sunny: 'Soleggiato', windy: 'Ventoso', 'windy-variant': 'Ventoso'};
  const ICON = {'clear-night': 'weather-night', cloudy: 'weather-cloudy', exceptional: 'alert-circle-outline', fog: 'weather-fog', hail: 'weather-hail', lightning: 'weather-lightning', 'lightning-rainy': 'weather-lightning-rainy', partlycloudy: isNight ? 'weather-night-partly-cloudy' : 'weather-partly-cloudy', pouring: 'weather-pouring', rainy: 'weather-rainy', snowy: 'weather-snowy', 'snowy-rainy': 'weather-snowy-rainy', sunny: 'weather-sunny', windy: 'weather-windy', 'windy-variant': 'weather-windy-variant'};
  const bg = isNight ? 'linear-gradient(160deg,#0B1030,#1D2457 60%,#2C2A5E)'
    : /rain|pour|lightning|hail/.test(c) ? 'linear-gradient(160deg,#41526B,#5E7491 60%,#8296AE)'
    : /cloud|fog/.test(c) ? 'linear-gradient(160deg,#6E8099,#93A6BE 60%,#B9C7D6)'
    : /snow/.test(c) ? 'linear-gradient(160deg,#9FB4CC,#C9D7E6 60%,#EEF3F8)'
    : 'linear-gradient(160deg,#2F80ED,#56A8F5 55%,#8FCBFF)';
  const temp = w && w.attributes && w.attributes.temperature != null ? Math.round(w.attributes.temperature) + '°' : '–°';
  const F = window.__hwNws || {};
  const td = F.td || [];
  const day = td.find((p) => p.is_daytime) || null, nt = td.find((p) => !p.is_daytime) || null;
  const hi = day && day.temperature != null ? Math.round(day.temperature) + '°' : '–', lo = nt && nt.temperature != null ? Math.round(nt.temperature) + '°' : '–';
  const next = td.filter((p) => p.is_daytime).slice(1, 5).map((p) => {
    const dd = new Date(p.datetime);
    return `<div style="text-align:center;min-width:12vmin"><div style="font-size:2.8vmin;opacity:.8">${esc(dd.toLocaleDateString(LOC, {weekday: 'short'}))}</div>
      <ha-icon icon="mdi:${ICON[p.condition] || 'weather-partly-cloudy'}" style="--mdc-icon-size:6vmin;margin:1vmin 0"></ha-icon>
      <div style="font-size:3vmin;font-weight:600">${p.temperature != null ? Math.round(p.temperature) + '°' : '–'}</div></div>`;
  }).join('');
  key += '|' + c + '|' + temp + '|' + hi + lo + '|' + td.length + '|' + minuteKey;
  html = wrap(`<div style="position:absolute;inset:0;padding:6% 7%;box-sizing:border-box;color:#fff;display:flex;flex-direction:column">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><div style="font-size:4vmin;font-weight:600">${esc(CFG.place || T('Casa', 'Home'))}</div>
          <div style="font-size:24vmin;font-weight:200;line-height:1;letter-spacing:-0.04em;margin-top:1vmin">${temp}</div>
          <div style="font-size:4.4vmin;font-weight:500">${esc(NAMES[c] || c)}</div>
          <div style="font-size:3.4vmin;opacity:.85;margin-top:.6vmin">${T('Max', 'H')} ${hi} · ${T('Min', 'L')} ${lo}</div></div>
        <div style="text-align:right"><ha-icon icon="mdi:${ICON[c] || 'weather-partly-cloudy'}" style="--mdc-icon-size:22vmin"></ha-icon>
          <div style="font-size:5vmin;font-weight:300;margin-top:1vmin">${hhmm}</div></div>
      </div>
      <div style="margin-top:auto;display:flex;gap:4vmin;justify-content:flex-start">${next}</div>
    </div>`, bg, key);
}

else if (face === 'calendar') {
  const F = window.__hwCal2 || {};
  const pd = (s) => { if (typeof s === 'string' && s.length === 10) { const [y, mo, dd] = s.split('-').map(Number); return new Date(y, mo - 1, dd); } return new Date(s); };
  const sod = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate());
  const today = sod(d);
  const ev = (F.ev || []).map((e) => Object.assign({}, e, {_s: pd(e.start), _e: pd(e.end)})).filter((e) => e._e > d).sort((a, b) => a._s - b._s).slice(0, 5);
  const dayLbl = (x) => { const diff = Math.round((sod(x) - today) / 86400000); if (diff <= 0) return T('Oggi', 'Today'); if (diff === 1) return T('Domani', 'Tomorrow'); return x.toLocaleDateString(LOC, {weekday: 'long', day: 'numeric', month: 'short'}); };
  const rows = ev.map((e) => {
    const allDay = typeof e.start === 'string' && e.start.length === 10;
    const col = (CFG.cals && CFG.cals[e._cal]) || '#FF9F0A';
    const time = allDay ? T('Tutto il giorno', 'All day') : e._s.toLocaleTimeString(LOC, {hour: '2-digit', minute: '2-digit'});
    return `<div style="display:flex;gap:2.4vmin;align-items:stretch;margin-bottom:2.6vmin">
      <div style="width:.9vmin;border-radius:1vmin;background:${col}"></div>
      <div style="min-width:0"><div style="font-size:4.2vmin;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(e.summary)}</div>
        <div style="font-size:3vmin;opacity:.75">${esc(dayLbl(e._s))} · ${esc(time)}</div></div></div>`;
  }).join('');
  key += '|' + ev.map((e) => e.start + e.summary).join(',') + '|' + minuteKey;
  html = wrap(`<div style="position:absolute;inset:0;padding:6% 7%;box-sizing:border-box;color:#fff;display:grid;grid-template-columns:1fr 1.4fr;gap:6%">
      <div><div style="font-size:4vmin;font-weight:600;color:#FF453A;text-transform:uppercase;letter-spacing:.08em">${esc(d.toLocaleDateString(LOC, {weekday: 'long'}))}</div>
        <div style="font-size:30vmin;font-weight:200;line-height:1;letter-spacing:-0.05em">${d.getDate()}</div>
        <div style="font-size:4vmin;opacity:.8">${esc(d.toLocaleDateString(LOC, {month: 'long', year: 'numeric'}))}</div>
        <div style="font-size:7vmin;font-weight:200;margin-top:4vmin">${hhmm}</div></div>
      <div style="align-self:center;min-width:0"><div style="font-size:3vmin;font-weight:700;text-transform:uppercase;letter-spacing:.1em;opacity:.6;margin-bottom:3vmin">${T('Prossimi', 'Up next')}</div>
        ${rows || `<div style="font-size:4vmin;opacity:.7">${T('Nessun impegno in arrivo', 'Nothing coming up')}</div>`}</div>
    </div>`, 'linear-gradient(160deg,#141418,#24242B)', key);
}

// identical string for the same key -> the DOM is left alone, so animations don't restart
if (prev.key === key && !CFG.preview) return prev.html;
if (!CFG.preview) window.__hvFace = {key, html, face, photo: photoIdx};
return html;
