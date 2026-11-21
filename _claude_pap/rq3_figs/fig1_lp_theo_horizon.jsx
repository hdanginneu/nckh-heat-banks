export default () => <claude.Visualize data-claude-component='lp-theo-horizon' sources={{rows:{kind:'data', data:[{o:'nco', h:0, b:0.005604, lo:-0.002041, hi:0.013248, p:0.247, m:false, n:97525},{o:'nco', h:1, b:0.005642, lo:-0.008282, hi:0.019567, p:0.519, m:false, n:93601},{o:'nco', h:2, b:-0.003579, lo:-0.021943, hi:0.014785, p:0.751, m:false, n:86143},{o:'nco', h:3, b:-0.017153, lo:-0.040661, hi:0.006356, p:0.243, m:false, n:78981},{o:'nco', h:4, b:-0.015916, lo:-0.041956, hi:0.010124, p:0.328, m:false, n:72114},{o:'nco', h:5, b:-0.019635, lo:-0.04845, hi:0.00918, p:0.282, m:false, n:65501},{o:'nco', h:6, b:-0.011961, lo:-0.042565, hi:0.018643, p:0.541, m:true, n:59172},{o:'allow', h:0, b:-0.008407, lo:-0.014312, hi:-0.002503, p:0.029, m:true, n:89284},{o:'allow', h:1, b:-0.019008, lo:-0.029014, hi:-0.009001, p:0.003, m:true, n:81466},{o:'allow', h:2, b:-0.020051, lo:-0.032828, hi:-0.007274, p:0.012, m:false, n:74014},{o:'allow', h:3, b:-0.023839, lo:-0.038032, hi:-0.009646, p:0.004, m:true, n:66887},{o:'allow', h:4, b:-0.02188, lo:-0.036154, hi:-0.007605, p:0.013, m:true, n:60049},{o:'allow', h:5, b:-0.013288, lo:-0.028679, hi:0.002103, p:0.165, m:true, n:53467},{o:'allow', h:6, b:-0.012763, lo:-0.029244, hi:0.003718, p:0.198, m:true, n:47163},{o:'pdna', h:0, b:-0.000871, lo:-0.005229, hi:0.003488, p:0.743, m:true, n:97525},{o:'pdna', h:1, b:-0.001597, lo:-0.007985, hi:0.004791, p:0.686, m:true, n:93601},{o:'pdna', h:2, b:0.00178, lo:-0.006556, hi:0.010116, p:0.726, m:false, n:86143},{o:'pdna', h:3, b:0.002157, lo:-0.006852, hi:0.011166, p:0.696, m:false, n:78981},{o:'pdna', h:4, b:-0.00325, lo:-0.012986, hi:0.006486, p:0.599, m:false, n:72114},{o:'pdna', h:5, b:-0.005325, lo:-0.015406, hi:0.004755, p:0.382, m:false, n:65501},{o:'pdna', h:6, b:-0.00378, lo:-0.015017, hi:0.007458, p:0.586, m:false, n:59172},{o:'liq', h:0, b:0.175251, lo:0.099179, hi:0.251323, p:0.002, m:true, n:97526},{o:'liq', h:1, b:0.060097, lo:-0.051084, hi:0.171278, p:0.428, m:false, n:93601},{o:'liq', h:2, b:0.126136, lo:0.002567, hi:0.249706, p:0.163, m:false, n:86143},{o:'liq', h:3, b:0.0314, lo:-0.087567, hi:0.150368, p:0.724, m:false, n:78981},{o:'liq', h:4, b:-0.054708, lo:-0.169919, hi:0.060503, p:0.513, m:false, n:72114},{o:'liq', h:5, b:0.020652, lo:-0.097968, hi:0.139273, p:0.81, m:false, n:65501},{o:'liq', h:6, b:-0.007516, lo:-0.1338, hi:0.118769, p:0.928, m:false, n:59172},{o:'agl', h:0, b:-0.259657, lo:-0.367095, hi:-0.152219, p:0.001, m:false, n:97525},{o:'agl', h:1, b:-0.125322, lo:-0.315198, hi:0.064553, p:0.28, m:false, n:93601},{o:'agl', h:2, b:-0.143981, lo:-0.392668, hi:0.104706, p:0.351, m:true, n:86143},{o:'agl', h:3, b:-0.006049, lo:-0.318535, hi:0.306438, p:0.979, m:false, n:78981},{o:'agl', h:4, b:0.154767, lo:-0.219818, hi:0.529352, p:0.497, m:false, n:72114},{o:'agl', h:5, b:0.159967, lo:-0.23309, hi:0.553024, p:0.508, m:false, n:65501},{o:'agl', h:6, b:0.142093, lo:-0.265057, hi:0.549243, p:0.569, m:false, n:59172}]}, panels:{kind:'data', data:[{slug:'nco', label:'Tổn thất ròng cộng dồn', unit:'điểm % dư nợ t−1', c:0, w:0, dec:3},{slug:'allow', label:'Thay đổi dự phòng', unit:'điểm % dư nợ t−1', c:1, w:0, dec:3},{slug:'pdna', label:'Quá hạn sớm, nợ đất nông nghiệp', unit:'điểm % dư nợ t−1', c:2, w:0, dec:3},{slug:'liq', label:'Tỷ lệ thanh khoản', unit:'điểm % tổng tài sản', c:0, w:1, dec:2},{slug:'agl', label:'Dư nợ nông nghiệp', unit:'điểm % dư nợ t−1', c:1, w:1, dec:2}]}}}>{({rows, panels, datum}) => {
 const pw = 230, gap = 20, x0 = 16, y0 = 92, ph = 186, ax = 46, plotH = 110;
 const fmt = (v, d) => (v < 0 ? '−' : '') + Math.abs(v).toFixed(d).replace('.', ',');
 const blue = 'var(--cds-chart-categorical-1)', grey = 'var(--cds-chart-muted)';
 return <svg viewBox='0 0 760 458' role='img' aria-label='Không có mẫu hình ghi nhận trễ: tổn thất và dự phòng không tăng về sau' fontSize='11'>
  <text data-claude-text-id='title' x='16' y='24' fontSize='15' fontWeight='600' fill='var(--cds-text-primary)'>Không có mẫu hình ghi nhận trễ: tổn thất và dự phòng không tăng về sau</text>
  <text data-claude-text-id='sub-1' x='16' y='44' fill='var(--cds-text-secondary)'>β₂ theo h, số năm sau năm nóng; nhiệt +1 SD, FarmShare +10 điểm %. Vạch dọc: khoảng tin cậy 90% từ hoán vị năm thời tiết.</text>
  <text data-claude-text-id='sub-2' x='16' y='60' fill='var(--cds-text-secondary)'>Chấm xanh: các h tạo nên thống kê chính (C1: h = 6; C2: h = 0–1 và 3–6; C3: h = 0–1; C4: h = 0; C5: h = 2).</text>
  {panels.map(p => {
   const pr = rows.filter(r => r.o === p.slug);
   const lo = Math.min(0, ...pr.map(r => r.lo)), hi = Math.max(0, ...pr.map(r => r.hi)), pad = (hi - lo) * 0.06;
   const gx = x0 + p.c * (pw + gap), gy = y0 + p.w * ph, py = gy + 34;
   const y = v => py + (hi + pad - v) / (hi - lo + 2 * pad) * plotH;
   const band = (pw - ax) / 7, x = h => gx + ax + band * h + band / 2;
   return <g key={p.slug} data-claude-anchor={`panel-${p.slug}`}>
    <text x={gx} y={gy + 10} fontWeight='600' fill='var(--cds-text-primary)'>{p.label}</text>
    <text x={gx} y={gy + 24} fill='var(--cds-text-secondary)'>{p.unit}</text>
    <line x1={gx + ax} x2={gx + pw} y1={y(0)} y2={y(0)} stroke='var(--cds-chart-axis)' />
    <text x={gx + ax - 6} y={y(0) + 4} textAnchor='end' fill='var(--cds-text-secondary)'>0</text>
    {y(0) - y(hi) > 14 ? <text x={gx + ax - 6} y={y(hi) + 4} textAnchor='end' fill='var(--cds-text-secondary)'>{fmt(hi, p.dec)}</text> : null}
    {y(lo) - y(0) > 14 ? <text x={gx + ax - 6} y={y(lo) + 4} textAnchor='end' fill='var(--cds-text-secondary)'>{fmt(lo, p.dec)}</text> : null}
    {pr.map(r => <g key={`${p.slug}-${r.h}`}>
     <line x1={x(r.h)} x2={x(r.h)} y1={y(r.lo)} y2={y(r.hi)} stroke={r.m ? blue : grey} strokeWidth='2' {...datum(r, 'hi')}><title>{`${p.label}, h = ${r.h}: khoảng tin cậy 90% [${fmt(r.lo, 4)}; ${fmt(r.hi, 4)}]`}</title></line>
     <circle cx={x(r.h)} cy={y(r.b)} r='3.5' fill={r.m ? blue : grey} {...datum(r, 'b')}><title>{`${p.label}, h = ${r.h}: β₂ = ${fmt(r.b, 4)}; p hoán vị = ${fmt(r.p, 3)}; n = ${r.n}`}</title></circle>
     <text x={x(r.h)} y={py + plotH + 16} textAnchor='middle' fill='var(--cds-text-secondary)'>{r.h}</text>
    </g>)}
   </g>;
  })}
  <g data-claude-anchor='chu-thich'>
   <text data-claude-text-id='note-h' x='516' y='296' fill='var(--cds-text-secondary)'>Trục ngang: h = 0 là năm nóng.</text>
   <text data-claude-text-id='note-sample' x='516' y='314' fill='var(--cds-text-secondary)'>Mỗi h là một mẫu riêng (Bảng C1).</text>
   <text data-claude-text-id='note-sample-2' x='516' y='330' fill='var(--cds-text-secondary)'>C2 và C3 tính trên mẫu chung của mọi h,</text>
   <text data-claude-text-id='note-sample-3' x='516' y='346' fill='var(--cds-text-secondary)'>nên lệch ít so với các chấm này.</text>
   <text data-claude-text-id='note-scale' x='516' y='370' fill='var(--cds-text-secondary)'>Mỗi ô có thang dọc riêng.</text>
  </g>
 </svg>;
}}</claude.Visualize>;
