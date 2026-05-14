// Experiments & metrics page — uses Recharts if available
const { useState } = React;

/* ─── Mock data ─── */
const MODEL_COMP = [
  { metric: 'mAP@50',    n: 84.3, s: 89.1 },
  { metric: 'mAP@50-95', n: 68.1, s: 73.4 },
  { metric: 'Precision', n: 86.7, s: 91.2 },
  { metric: 'Recall',    n: 82.1, s: 87.6 },
];

const CONF_THRESH = [
  { conf: 0.25, precision: 78.1, recall: 93.2, f1: 85.0 },
  { conf: 0.35, precision: 83.5, recall: 90.1, f1: 86.7 },
  { conf: 0.45, precision: 87.2, recall: 86.3, f1: 86.8 },
  { conf: 0.50, precision: 89.1, recall: 82.4, f1: 85.6 },
  { conf: 0.60, precision: 91.8, recall: 76.9, f1: 83.7 },
  { conf: 0.70, precision: 93.4, recall: 70.1, f1: 80.1 },
  { conf: 0.80, precision: 95.1, recall: 61.8, f1: 74.9 },
];

const TRACKER_DATA = [
  { metric: 'MOTA ↑',          bytetrack: '72.4', botsort: '71.8', bt_wins: true  },
  { metric: 'ID Switches ↓',   bytetrack: '23',   botsort: '31',   bt_wins: true  },
  { metric: 'Avg FPS ↑',       bytetrack: '34.2', botsort: '28.1', bt_wins: true  },
  { metric: 'Fragmentations ↓',bytetrack: '41',   botsort: '47',   bt_wins: true  },
  { metric: 'Track Recall ↑',  bytetrack: '84.1', botsort: '82.7', bt_wins: true  },
];

/* ─── Simple SVG bar chart (no Recharts dependency) ─── */
const BarChartSVG = ({ data }) => {
  const W = 500, H = 180, PAD_L = 10, PAD_B = 24, BAR_GAP = 6;
  const gW = (W - PAD_L) / data.length;
  const bW = (gW - BAR_GAP * 3) / 2;
  const maxV = 100;
  const scaleY = v => H - PAD_B - (v / maxV) * (H - PAD_B - 8);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: H, overflow: 'visible' }}>
      <defs>
        <linearGradient id="barN" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#4a607a"/><stop offset="100%" stopColor="#3a4e63"/></linearGradient>
        <linearGradient id="barS" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="var(--accent)"/><stop offset="100%" stopColor="var(--accent-hover)"/></linearGradient>
      </defs>
      {[60,70,80,90,100].map(g => (
        <g key={g}>
          <line x1={PAD_L} y1={scaleY(g)} x2={W} y2={scaleY(g)} stroke="var(--border)" strokeWidth="0.5"/>
          <text x={PAD_L - 2} y={scaleY(g) + 3} fontSize="9" fill="var(--text-3)" textAnchor="end">{g}</text>
        </g>
      ))}
      {data.map((d, i) => {
        const x = PAD_L + i * gW + BAR_GAP;
        const yN = scaleY(d.n); const yS = scaleY(d.s);
        const hN = H - PAD_B - yN; const hS = H - PAD_B - yS;
        return (
          <g key={d.metric}>
            <rect x={x} y={yN} width={bW} height={hN} fill="url(#barN)" rx="2"/>
            <rect x={x + bW + BAR_GAP} y={yS} width={bW} height={hS} fill="url(#barS)" rx="2"/>
            <text x={x + bW + BAR_GAP / 2} y={H - 6} fontSize="9" fill="var(--text-3)" textAnchor="middle">{d.metric}</text>
          </g>
        );
      })}
    </svg>
  );
};

/* ─── Simple SVG line chart ─── */
const LineChartSVG = ({ data }) => {
  const W = 500, H = 160, PL = 24, PB = 24, PT = 8, PR = 12;
  const iW = W - PL - PR, iH = H - PT - PB;
  const xs = data.map((_, i) => PL + (i / (data.length - 1)) * iW);
  const ys = (key) => data.map(d => PT + (1 - (d[key] - 55) / 45) * iH);
  const line = (key) => xs.map((x, i) => `${x},${ys(key)[i]}`).join(' ');

  const series = [
    { key: 'precision', color: 'var(--accent)',   label: 'Precision' },
    { key: 'recall',    color: 'var(--success)',   label: 'Recall'    },
    { key: 'f1',        color: 'var(--warning)',   label: 'F1',       dash: '5 5' },
  ];

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: H, overflow: 'visible' }}>
      {[60,70,80,90,100].map(g => {
        const y = PT + (1 - (g - 55) / 45) * iH;
        return <line key={g} x1={PL} y1={y} x2={W - PR} y2={y} stroke="var(--border)" strokeWidth="0.5"/>;
      })}
      {series.map(s => (
        <polyline key={s.key} fill="none" stroke={s.color} strokeWidth="1.8"
          strokeDasharray={s.dash || ''} points={line(s.key)}/>
      ))}
      {data.map((d, i) => (
        <circle key={i} cx={xs[i]} cy={ys('precision')[i]} r="2.5" fill="var(--accent)"/>
      ))}
      {data.map((d, i) => (
        <text key={i} x={xs[i]} y={H - 6} fontSize="9" fill="var(--text-3)" textAnchor="middle">{d.conf.toFixed(2)}</text>
      ))}
    </svg>
  );
};

/* ─── Empty experiment section ─── */
const NoData = () => (
  <div style={{ padding: '40px 24px', textAlign: 'center', color: 'var(--text-3)' }}>
    <window.IcoFlask size={28} style={{ opacity: 0.25, marginBottom: 10 }}/>
    <div style={{ fontSize: 13 }}>Дані експерименту ще не завантажено</div>
  </div>
);

/* ─── Tabs content ─── */
const ModelComparison = ({ showEmpty }) => {
  if (showEmpty) return <NoData/>;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }} className="resp-grid-2">
      {/* Metric cards */}
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, fontFamily: 'var(--font-heading)', marginBottom: 14 }}>Ключові метрики</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {MODEL_COMP.map(m => (
            <div key={m.metric} className="card" style={{ padding: '12px 16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.055em' }}>{m.metric}</span>
                <div style={{ display: 'flex', gap: 14, fontSize: 11 }}>
                  <span style={{ color: 'var(--text-3)' }}>YOLO26n: <span style={{ fontFamily: 'var(--font-mono)', color: '#7a95b0' }}>{m.n}%</span></span>
                  <span style={{ color: 'var(--accent-text)' }}>YOLO26s: <span style={{ fontFamily: 'var(--font-mono)' }}>{m.s}%</span></span>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <div style={{ height: 3, background: 'var(--surface-3)', borderRadius: 2 }}>
                  <div style={{ width: `${m.n}%`, height: '100%', background: '#4a607a', borderRadius: 2 }}/>
                </div>
                <div style={{ height: 3, background: 'var(--surface-3)', borderRadius: 2 }}>
                  <div style={{ width: `${m.s}%`, height: '100%', background: 'var(--accent)', borderRadius: 2 }}/>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bar chart */}
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, fontFamily: 'var(--font-heading)', marginBottom: 14 }}>Порівняльна діаграма</div>
        <div className="card" style={{ padding: '16px 14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 10, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>Recharts · BarChart · вісь Y: %</span>
            <div style={{ display: 'flex', gap: 12 }}>
              {[['#4a607a', 'YOLO26n'], ['var(--accent)', 'YOLO26s']].map(([c, l]) => (
                <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11 }}>
                  <div style={{ width: 9, height: 9, borderRadius: 2, background: c, flexShrink: 0 }}/><span style={{ color: 'var(--text-2)' }}>{l}</span>
                </div>
              ))}
            </div>
          </div>
          <BarChartSVG data={MODEL_COMP}/>
        </div>
      </div>
    </div>
  );
};

const ThresholdAnalysis = ({ showEmpty }) => {
  if (showEmpty) return <NoData/>;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 20 }} className="resp-grid-col-side">
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, fontFamily: 'var(--font-heading)', marginBottom: 14 }}>Precision / Recall / F1 по порогу</div>
        <div className="card" style={{ padding: '16px 14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 10, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>Recharts · LineChart · вісь X: поріг</span>
            <div style={{ display: 'flex', gap: 10 }}>
              {[['var(--accent)', 'Precision'], ['var(--success)', 'Recall'], ['var(--warning)', 'F1']].map(([c, l]) => (
                <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11 }}>
                  <div style={{ width: 14, height: 2, background: c, borderRadius: 1 }}/><span style={{ color: 'var(--text-2)' }}>{l}</span>
                </div>
              ))}
            </div>
          </div>
          <LineChartSVG data={CONF_THRESH}/>
        </div>
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, fontFamily: 'var(--font-heading)', marginBottom: 14 }}>Значення</div>
        <div className="card">
          <table className="data-table">
            <thead><tr><th>Поріг</th><th>Prec.</th><th>Rec.</th><th>F1</th></tr></thead>
            <tbody>
              {CONF_THRESH.map(r => (
                <tr key={r.conf} style={r.conf === 0.45 ? { background: 'var(--accent-dim)' } : {}}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{r.conf.toFixed(2)}{r.conf === 0.45 ? ' ★' : ''}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{r.precision}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{r.recall}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{r.f1}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: 7, fontSize: 11, color: 'var(--text-3)' }}>★ Типове значення (0.45)</div>
      </div>
    </div>
  );
};

const TrackerComparison = ({ showEmpty }) => {
  if (showEmpty) return <NoData/>;
  return (
    <>
      <div style={{ marginBottom: 12, padding: '9px 13px', background: 'var(--accent-dim)', borderRadius: 'var(--radius)', border: '1px solid rgba(59,130,246,0.15)', fontSize: 12, color: 'var(--accent-text)', display: 'flex', alignItems: 'center', gap: 8 }}>
        <window.IcoInfo size={13} style={{ flexShrink: 0 }}/>
        Порівняння поведінки трекерів — не є абсолютною оцінкою точності відстеження
      </div>
      <div className="card">
        <table className="data-table">
          <thead><tr><th>Метрика</th><th>ByteTrack (типово)</th><th>BoT-SORT</th><th>Перевага</th></tr></thead>
          <tbody>
            {TRACKER_DATA.map(r => (
              <tr key={r.metric}>
                <td style={{ fontWeight: 500 }}>{r.metric}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{r.bytetrack}</span>
                    {r.bt_wins && <span style={{ fontSize: 10, background: 'var(--success-dim)', color: 'var(--success-text)', padding: '0 5px', borderRadius: 3, fontWeight: 600 }}>краще</span>}
                  </div>
                </td>
                <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{r.botsort}</td>
                <td style={{ fontSize: 12, color: r.bt_wins ? 'var(--success-text)' : 'var(--text-3)' }}>ByteTrack</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
};

const FPAnalysis = ({ showEmpty }) => {
  if (showEmpty) return <NoData/>;
  const cards = [
    { label: 'Bird→Drone FP', val: '3.2%',  sub: 'Хибне виявлення птахів як дронів', color: 'var(--warning)', icon: <window.IcoAlertTriangle size={16}/> },
    { label: 'True Positive Rate', val: '96.8%', sub: 'Частка вірно виявлених дронів', color: 'var(--success)', icon: <window.IcoCheckCircle size={16}/> },
    { label: 'FP Reduction', val: '−41%', sub: 'відносно попередньої версії моделі', color: 'var(--accent)', icon: <window.IcoActivity size={16}/> },
  ];
  const breakdown = [
    { cat: 'Птахи',         pct: 3.2, count: 18 },
    { cat: 'Комахи',        pct: 0.7, count: 4  },
    { cat: 'Гілки / листя', pct: 0.5, count: 3  },
    { cat: 'Інше',          pct: 0.4, count: 2  },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {cards.map(c => (
          <div key={c.label} className="card" style={{ padding: '18px 20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <span style={{ color: c.color }}>{c.icon}</span>
              <span style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>{c.label}</span>
            </div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: 34, fontWeight: 700, color: c.color, marginBottom: 5, lineHeight: 1 }}>{c.val}</div>
            <div style={{ fontSize: 12, color: 'var(--text-3)', lineHeight: 1.4 }}>{c.sub}</div>
          </div>
        ))}
      </div>
      <div className="card" style={{ padding: '16px 20px' }}>
        <div style={{ fontSize: 13, fontWeight: 600, fontFamily: 'var(--font-heading)', marginBottom: 14 }}>Розбивка хибнопозитивних виявлень</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {breakdown.map(fp => (
            <div key={fp.cat}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                <span style={{ color: 'var(--text-2)' }}>{fp.cat}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-3)' }}>{fp.pct}%</span>
              </div>
              <div style={{ height: 4, background: 'var(--surface-3)', borderRadius: 2 }}>
                <div style={{ width: `${(fp.pct / 3.2) * 100}%`, height: '100%', background: 'var(--warning)', borderRadius: 2 }}/>
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-3)', marginTop: 4 }}>{fp.count} випадків</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/* ─── Main page ─── */
const ExperimentsPage = ({ showEmpty }) => {
  const [tab, setTab] = useState('models');
  const tabs = [
    { id: 'models',    label: 'Порівняння моделей'  },
    { id: 'threshold', label: 'Поріг впевненості'   },
    { id: 'trackers',  label: 'Трекери'              },
    { id: 'fp',        label: 'Хибнопозитивні'       },
  ];

  return (
    <>
      <window.PageHeader title="Досліди та метрики" subtitle="Результати експериментів та порівняльний аналіз моделей"/>
      <div style={{ marginBottom: 20 }}>
        <window.Tabs tabs={tabs} active={tab} onChange={setTab}/>
      </div>
      <div className="card" style={{ padding: '20px 22px' }}>
        {tab === 'models'    && <ModelComparison   showEmpty={showEmpty}/>}
        {tab === 'threshold' && <ThresholdAnalysis showEmpty={showEmpty}/>}
        {tab === 'trackers'  && <TrackerComparison showEmpty={showEmpty}/>}
        {tab === 'fp'        && <FPAnalysis        showEmpty={showEmpty}/>}
      </div>
    </>
  );
};

Object.assign(window, { ExperimentsPage });
