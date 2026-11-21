export default () => <claude.Visualize data-claude-component='tuong-duong-theo-delta' sources={{rows:{kind:'data', data:[{slug:'c1', label:'C1 Tổn thất cộng dồn 7 năm', d:0.012866, t:-0.011961, lo:-0.042565, hi:0.018643, t2:-0.014275, lo2:-0.039907, hi2:0.011357, k2:'gộp hai mẫu', v:'? không kết luận'},{slug:'c2', label:'C2 Dự phòng muộn − sớm', d:0.011996, t:-0.002264, lo:-0.011995, hi:0.007468, t2:-0.003643, lo2:-0.011504, hi2:0.004218, k2:'gộp hai mẫu', v:'0 sát biên'},{slug:'c3', label:'C3 Quá hạn sớm, nợ đất NN', d:0.007197, t:-0.000829, lo:-0.005631, hi:0.003973, t2:0.000926, lo2:-0.003459, hi2:0.005312, k2:'gộp hai mẫu', v:'0 gợi ý'},{slug:'p2', label:'Nợ xấu sau đợt nóng hai năm', d:0.057328, t:0.031536, lo:-0.010799, hi:0.073871, t2:null, lo2:null, hi2:null, k2:'', v:'? không kết luận'},{slug:'p1', label:'Lãi suất vay sản xuất NN', d:0.06831, t:0.014208, lo:-0.013555, hi:0.041972, t2:null, lo2:null, hi2:null, k2:'', v:'0 tương đương'},{slug:'c5', label:'C5 Dư nợ NN đến t+2', d:0.30757, t:-0.143981, lo:-0.392668, hi:0.104706, t2:-0.152967, lo2:-0.33142, hi2:0.025486, k2:'gộp hai mẫu', v:'? không kết luận'},{slug:'c4', label:'C4 Thanh khoản năm nóng', d:0.213356, t:0.175251, lo:0.099179, hi:0.251323, t2:0.012964, lo2:-0.084016, hi2:0.109944, k2:'mẫu ngoài 1995–2006', v:'+ không lặp lại'}]}}}>{({rows, datum}) => {
 const xl = 262, xr = 612, vmin = -3.5, vmax = 1.6, y0 = 100, rh = 40;
 const X = v => xl + (v - vmin) / (vmax - vmin) * (xr - xl);
 const fmt = v => (v < 0 ? '−' : '') + Math.abs(v).toFixed(4).replace('.', ',');
 const blue = 'var(--cds-chart-categorical-1)', grey = 'var(--cds-chart-muted)';
 const yb = y0 + rows.length * rh;
 return <svg viewBox='0 0 760 432' role='img' aria-label='Lãi suất, dự phòng, quá hạn sớm nằm trong ±Δ; tổn thất cộng dồn thì chưa' fontSize='11'>
  <text data-claude-text-id='title' x='16' y='24' fontSize='15' fontWeight='600' fill='var(--cds-text-primary)'>Lãi suất, dự phòng, quá hạn sớm nằm trong ±Δ; tổn thất cộng dồn thì chưa</text>
  <text data-claude-text-id='sub-1' x='16' y='44' fill='var(--cds-text-secondary)'>Ước lượng và khoảng tin cậy 90%, chia cho ngưỡng Δ của từng thống kê; kết luận tương đương khi cả khoảng nằm trong ±Δ.</text>
  <text data-claude-text-id='sub-2' x='16' y='60' fill='var(--cds-text-secondary)'>Chấm xanh: mẫu chính 2007–2024. Chấm rỗng: gộp với mẫu 1995–2006 (riêng C4: mẫu ngoài 1995–2006).</text>
  <rect x={X(-1)} y={y0 - 16} width={X(1) - X(-1)} height={yb - y0 + 4} fill='var(--cds-chart-muted)' fillOpacity='0.16' />
  <text data-claude-text-id='band' x={X(0)} y={y0 - 22} textAnchor='middle' fill='var(--cds-text-secondary)'>vùng tương đương ±Δ</text>
  <g data-claude-anchor='x-axis'>
   <line x1={X(0)} x2={X(0)} y1={y0 - 16} y2={yb - 12} stroke='var(--cds-chart-axis)' />
   <line x1={X(-1)} x2={X(-1)} y1={y0 - 16} y2={yb - 12} stroke='var(--cds-chart-reference)' strokeDasharray='3 3' />
   <line x1={X(1)} x2={X(1)} y1={y0 - 16} y2={yb - 12} stroke='var(--cds-chart-reference)' strokeDasharray='3 3' />
   <text data-claude-text-id='tick-m3' x={X(-3)} y={yb + 6} textAnchor='middle' fill='var(--cds-text-secondary)'>−3Δ</text>
   <text data-claude-text-id='tick-m2' x={X(-2)} y={yb + 6} textAnchor='middle' fill='var(--cds-text-secondary)'>−2Δ</text>
   <text data-claude-text-id='tick-m1' x={X(-1)} y={yb + 6} textAnchor='middle' fill='var(--cds-text-secondary)'>−Δ</text>
   <text data-claude-text-id='tick-0' x={X(0)} y={yb + 6} textAnchor='middle' fill='var(--cds-text-secondary)'>0</text>
   <text data-claude-text-id='tick-p1' x={X(1)} y={yb + 6} textAnchor='middle' fill='var(--cds-text-secondary)'>+Δ</text>
   <text data-claude-text-id='axis-note' x='16' y={yb + 30} fill='var(--cds-text-secondary)'>Với C1–C3, nợ xấu và lãi suất, phía dương là bất lợi cho ngân hàng hoặc người vay.</text>
  </g>
  {rows.map((r, i) => { const yy = y0 + i * rh; return <g key={r.slug} data-claude-anchor={`row-${r.slug}`}>
   <text x='16' y={yy + 4} fill='var(--cds-text-primary)'>{r.label}</text>
   <line x1={X(r.lo / r.d)} x2={X(r.hi / r.d)} y1={yy} y2={yy} stroke={blue} strokeWidth='2' {...datum(r, 'hi')}><title>{`${r.label}, mẫu chính: khoảng tin cậy 90% [${fmt(r.lo)}; ${fmt(r.hi)}], Δ = ${fmt(r.d)}`}</title></line>
   <circle cx={X(r.t / r.d)} cy={yy} r='4' fill={blue} {...datum(r, 't')}><title>{`${r.label}, mẫu chính: ước lượng ${fmt(r.t)}`}</title></circle>
   {r.t2 === null ? null : <line x1={X(r.lo2 / r.d)} x2={X(r.hi2 / r.d)} y1={yy + 12} y2={yy + 12} stroke={grey} strokeWidth='2' {...datum(r, 'hi2')}><title>{`${r.label}, ${r.k2}: khoảng tin cậy 90% [${fmt(r.lo2)}; ${fmt(r.hi2)}]`}</title></line>}
   {r.t2 === null ? null : <circle cx={X(r.t2 / r.d)} cy={yy + 12} r='3.5' fill='none' stroke={grey} strokeWidth='1.5' {...datum(r, 't2')}><title>{`${r.label}, ${r.k2}: ước lượng ${fmt(r.t2)}`}</title></circle>}
   <text x='626' y={yy + 4} fill='var(--cds-text-secondary)'>{r.v}</text>
  </g>; })}
 </svg>;
}}</claude.Visualize>;
