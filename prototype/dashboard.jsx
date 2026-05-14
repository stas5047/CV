// Dashboard page
const { useState, useEffect } = React;

const DASH_STATS = { processedFiles: 1847, totalDetections: 23419, avgConfidence: 0.872, avgFps: 34.2 };
const ACTIVE_MODEL = { name: 'YOLO26s-v1.2', family: 'YOLO26', variant: 's', mAP50: 0.891, precision: 0.912, recall: 0.876 };

const RECENT_JOBS = [
  { id: 'j001', filename: 'patrol_footage_01.mp4', status: 'completed', mediaType: 'video', model: 'YOLO26s-v1.2', created: '2026-05-14T09:23:00Z', duration: 47,  detections: 312  },
  { id: 'j002', filename: 'aerial_snapshot_43.jpg', status: 'completed', mediaType: 'image', model: 'YOLO26s-v1.2', created: '2026-05-14T08:11:00Z', duration: 3,   detections: 1    },
  { id: 'j003', filename: 'sector_scan_video.mp4', status: 'processing', mediaType: 'video', model: 'YOLO26s-v1.2', created: '2026-05-14T10:05:00Z', duration: null, detections: null },
  { id: 'j004', filename: 'test_image_001.png',    status: 'failed',     mediaType: 'image', model: 'YOLO26s-v1.2', created: '2026-05-13T16:40:00Z', duration: 2,   detections: null },
  { id: 'j005', filename: 'night_patrol_27.mp4',   status: 'queued',     mediaType: 'video', model: 'YOLO26s-v1.2', created: '2026-05-14T10:08:00Z', duration: null, detections: null },
];

const ACTIVITY = [
  { day: '08.05', d: 1840 }, { day: '09.05', d: 923  }, { day: '10.05', d: 2340 },
  { day: '11.05', d: 712  }, { day: '12.05', d: 3120 }, { day: '13.05', d: 2890 },
  { day: '14.05', d: 1540 },
];

const ActivityChart = ({ data }) => {
  const max = Math.max(...data.map(d => d.d));
  const W = 420, H = 100, PAD = 10;
  const pts = data.map((d, i) => {
    const x = PAD + (i / (data.length - 1)) * (W - PAD * 2);
    const y = H - PAD - ((d.d / max) * (H - PAD * 2));
    return [x, y];
  });
  const polyline = pts.map(([x, y]) => `${x},${y}`).join(' ');
  const area = `M${pts[0][0]},${H} ` + pts.map(([x, y]) => `L${x},${y}`).join(' ') + ` L${pts[pts.length - 1][0]},${H} Z`;
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 100, display: 'block', overflow: 'visible' }}>
        <defs>
          <linearGradient id="dashGrad" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.25"/>
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0"/>
          </linearGradient>
        </defs>
        {[0.25, 0.5, 0.75].map(f => (
          <line key={f} x1={PAD} y1={H - PAD - f * (H - PAD * 2)} x2={W - PAD} y2={H - PAD - f * (H - PAD * 2)} stroke="var(--border)" strokeWidth="0.5"/>
        ))}
        <path d={area} fill="url(#dashGrad)"/>
        <polyline points={polyline} fill="none" stroke="var(--accent)" strokeWidth="1.5"/>
        {pts.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="2.5" fill="var(--accent)"/>
        ))}
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
        {data.map(d => (
          <span key={d.day} style={{ fontSize: 10, color: 'var(--text-3)', flex: 1, textAlign: 'center' }}>{d.day}</span>
        ))}
      </div>
    </div>
  );
};

const DashboardPage = ({ navigate, user, showEmpty }) => {
  const [loading, setLoading] = useState(true);
  useEffect(() => { const t = setTimeout(() => setLoading(false), 600); return () => clearTimeout(t); }, []);

  const fmt = iso => new Date(iso).toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' });
  const dur = s => s == null ? '—' : s < 60 ? `${s}с` : `${Math.floor(s / 60)}хв ${s % 60}с`;

  if (loading) return (
    <>
      <window.PageHeader title="Огляд" subtitle="Завантаження…"/>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card" style={{ padding: '18px 20px' }}>
            <window.Skel w="55%" h={10} mb={14}/><window.Skel w="45%" h={26} mb={8}/><window.Skel w="70%" h={10}/>
          </div>
        ))}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 16, marginBottom: 24 }}>
        <div className="card" style={{ padding: 20 }}><window.Skel w="100%" h={160}/></div>
        <div className="card" style={{ padding: 20 }}><window.Skel w="40%" h={14} mb={16}/><window.Skel w="100%" h={130}/></div>
      </div>
    </>
  );

  const stats = showEmpty ? null : DASH_STATS;
  const jobs = showEmpty ? [] : RECENT_JOBS;

  return (
    <>
      <window.PageHeader
        title="Огляд"
        subtitle={user?.role === 'admin' ? 'Глобальна статистика системи' : 'Ваша статистика обробки'}
        actions={<button className="btn btn-primary" onClick={() => navigate('/upload')}><window.IcoUpload size={13}/> Завантажити</button>}
      />

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 20 }} className="resp-grid-4">
        <window.MetricCard label="Оброблено файлів" value={stats ? stats.processedFiles.toLocaleString('uk-UA') : '—'} sub="за весь час" icon={<window.IcoFolder size={15}/>}/>
        <window.MetricCard label="Виявлень дронів" value={stats ? stats.totalDetections.toLocaleString('uk-UA') : '—'} sub="сумарно" icon={<window.IcoActivity size={15}/>}/>
        <window.MetricCard label="Сер. впевненість" value={stats ? `${(stats.avgConfidence * 100).toFixed(1)}%` : '—'} sub="завершені завдання" icon={<window.IcoPercent size={15}/>}/>
        <window.MetricCard label="Середній FPS" value={stats ? stats.avgFps.toFixed(1) : '—'} sub="відеозавдання" icon={<window.IcoZap size={15}/>}/>
      </div>

      {/* Active model + chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '272px 1fr', gap: 16, marginBottom: 20 }} className="resp-grid-col-side">
        {/* Active model */}
        <div className="card" style={{ padding: '18px 20px' }}>
          <div className="metric-label" style={{ marginBottom: 12 }}>Активна модель</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <div style={{ width: 38, height: 38, borderRadius: 9, background: 'var(--accent-dim)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <window.IcoCpu size={17} style={{ color: 'var(--accent)' }}/>
            </div>
            <div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600 }}>{ACTIVE_MODEL.name}</div>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 1 }}>Fine-tuned · {ACTIVE_MODEL.family} · {ACTIVE_MODEL.variant}</div>
            </div>
          </div>
          {[['mAP@50', ACTIVE_MODEL.mAP50], ['Precision', ACTIVE_MODEL.precision], ['Recall', ACTIVE_MODEL.recall]].map(([l, v]) => (
            <div key={l} style={{ marginBottom: 9 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 4 }}>
                <span style={{ color: 'var(--text-3)' }}>{l}</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-2)' }}>{(v * 100).toFixed(1)}%</span>
              </div>
              <window.MiniBar value={v} color="var(--accent)" height={2}/>
            </div>
          ))}
        </div>

        {/* Activity chart */}
        <div className="card" style={{ padding: '18px 20px' }}>
          <window.SectionHeader title="Виявлення за тиждень"/>
          {stats ? <ActivityChart data={ACTIVITY}/> : (
            <window.EmptyState icon={<window.IcoBarChart size={26}/>} title="Немає даних" subtitle="Дані з'являться після першого обробленого завдання"/>
          )}
        </div>
      </div>

      {/* Recent jobs */}
      <div className="card">
        <div style={{ padding: '14px 20px 0' }}>
          <window.SectionHeader title="Останні завдання" action={
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/jobs')}>
              Усі завдання <window.IcoChevronRight size={12}/>
            </button>
          }/>
        </div>
        {jobs.length === 0 ? (
          <window.EmptyState icon={<window.IcoInbox size={26}/>} title="Завдань ще немає" subtitle="Завантажте перший файл, щоб розпочати обробку"
            action={<button className="btn btn-primary btn-sm" onClick={() => navigate('/upload')}><window.IcoUpload size={12}/> Завантажити</button>}/>
        ) : (
          <table className="data-table">
            <thead><tr><th>Статус</th><th>Файл</th><th>Тип</th><th>Модель</th><th>Дата</th><th>Виявлень</th><th>Час</th><th></th></tr></thead>
            <tbody>
              {jobs.map(j => (
                <tr key={j.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/jobs/${j.id}`)}>
                  <td><window.StatusBadge status={j.status}/></td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                      <span style={{ color: 'var(--text-3)', flexShrink: 0 }}>{j.mediaType === 'video' ? <window.IcoVideo size={12}/> : <window.IcoImage size={12}/>}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)', maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.filename}</span>
                    </div>
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text-3)' }}>{j.mediaType === 'video' ? 'Відео' : 'Зобр.'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)' }}>{j.model}</td>
                  <td style={{ fontSize: 12, color: 'var(--text-3)', whiteSpace: 'nowrap' }}>{fmt(j.created)}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: j.detections != null ? 'var(--text-1)' : 'var(--text-3)' }}>
                    {j.detections != null ? j.detections.toLocaleString('uk-UA') : '—'}
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text-3)' }}>{dur(j.duration)}</td>
                  <td><button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); navigate(`/jobs/${j.id}`); }}><window.IcoEye size={12}/></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
};

Object.assign(window, { DashboardPage, RECENT_JOBS });
