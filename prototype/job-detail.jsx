// Job detail page
const { useState, useEffect } = React;

const MOCK_JOB_DATA = {
  j001: { id: 'j001', filename: 'patrol_footage_01.mp4',  status: 'completed', progress: 100, mediaType: 'video', model: 'YOLO26s-v1.2', created: '2026-05-14T09:23:00Z', duration: 47,  detections: 312, avgConf: 0.872, avgFps: 32.4, conf: 0.25, iou: 0.45, tracker: 'ByteTrack', error: null },
  j002: { id: 'j002', filename: 'aerial_snapshot_43.jpg', status: 'completed', progress: 100, mediaType: 'image', model: 'YOLO26s-v1.2', created: '2026-05-14T08:11:00Z', duration: 3,   detections: 1,   avgConf: 0.912, avgFps: null, conf: 0.25, iou: 0.45, tracker: null,       error: null },
  j003: { id: 'j003', filename: 'sector_scan_video.mp4',  status: 'processing',progress: 63,  mediaType: 'video', model: 'YOLO26s-v1.2', created: '2026-05-14T10:05:00Z', duration: null, detections: null,avgConf: null,  avgFps: null, conf: 0.25, iou: 0.45, tracker: 'ByteTrack', error: null },
  j004: { id: 'j004', filename: 'test_image_001.png',     status: 'failed',    progress: 0,   mediaType: 'image', model: 'YOLO26s-v1.2', created: '2026-05-13T16:40:00Z', duration: 2,   detections: null,avgConf: null,  avgFps: null, conf: 0.25, iou: 0.45, tracker: null,       error: 'Помилка читання файлу: пошкоджений JPEG-заголовок. Перевірте цілісність файлу.' },
  j005: { id: 'j005', filename: 'night_patrol_27.mp4',    status: 'queued',    progress: 0,   mediaType: 'video', model: 'YOLO26s-v1.2', created: '2026-05-14T10:08:00Z', duration: null, detections: null,avgConf: null,  avgFps: null, conf: 0.25, iou: 0.45, tracker: 'ByteTrack', error: null },
  j010: { id: 'j010', filename: 'frame_capture_112.webp', status: 'completed', progress: 100, mediaType: 'image', model: 'YOLO26s-v1.2', created: '2026-05-11T15:04:00Z', duration: 2,   detections: 0,   avgConf: null,  avgFps: null, conf: 0.25, iou: 0.45, tracker: null,       error: null },
};

const MOCK_DETECTIONS = [
  { frame: 1,   ts: '00:00:00.033', cls: 'drone', conf: 0.94, bbox: '[124, 87, 312, 198]',  trackId: 'T-001' },
  { frame: 4,   ts: '00:00:00.133', cls: 'drone', conf: 0.91, bbox: '[127, 90, 315, 201]',  trackId: 'T-001' },
  { frame: 8,   ts: '00:00:00.267', cls: 'drone', conf: 0.88, bbox: '[131, 95, 319, 206]',  trackId: 'T-001' },
  { frame: 12,  ts: '00:00:00.400', cls: 'drone', conf: 0.86, bbox: '[134, 98, 323, 210]',  trackId: 'T-001' },
  { frame: 15,  ts: '00:00:00.500', cls: 'drone', conf: 0.93, bbox: '[138, 102, 328, 215]', trackId: 'T-001' },
  { frame: 22,  ts: '00:00:00.733', cls: 'drone', conf: 0.79, bbox: '[185, 143, 371, 258]', trackId: 'T-002' },
  { frame: 28,  ts: '00:00:00.933', cls: 'drone', conf: 0.82, bbox: '[192, 150, 378, 266]', trackId: 'T-002' },
  { frame: 35,  ts: '00:00:01.167', cls: 'drone', conf: 0.85, bbox: '[198, 155, 385, 272]', trackId: 'T-002' },
];

const MOCK_TRACKS = [
  { id: 'T-001', firstFrame: 1,  lastFrame: 231, duration: '00:07:42', count: 228, avgConf: 0.884 },
  { id: 'T-002', firstFrame: 22, lastFrame: 127, duration: '00:03:31', count: 104, avgConf: 0.812 },
];

const JobDetailPage = ({ jobId, navigate, showEmpty }) => {
  const [loading, setLoading] = useState(true);
  const [job, setJob] = useState(null);

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => {
      // Check for dynamically uploaded jobs first
      const uploaded = window.__uploadedJobs?.[jobId];
      if (uploaded) {
        setJob({
          id: uploaded.id, filename: uploaded.filename, status: uploaded.status,
          progress: uploaded.progress || 0, mediaType: uploaded.mediaType,
          model: uploaded.model || 'YOLO26s-v1.2', created: uploaded.created,
          duration: uploaded.duration || null, detections: uploaded.detections ?? null,
          avgConf: uploaded.avgConf || null, avgFps: uploaded.status === 'completed' ? (28 + Math.random() * 10).toFixed(1) : null,
          conf: uploaded.conf || 0.25, iou: uploaded.iou || 0.45,
          tracker: uploaded.tracker || null, error: null,
        });
      } else {
        setJob(MOCK_JOB_DATA[jobId] || MOCK_JOB_DATA['j001']);
      }
      setLoading(false);
    }, 550);
    return () => clearTimeout(t);
  }, [jobId]);

  const fmt = iso => new Date(iso).toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' });
  const dur = s => s == null ? '—' : s < 60 ? `${s}с` : `${Math.floor(s / 60)}хв ${s % 60}с`;

  const dets   = (showEmpty || !job || job.detections === 0) ? [] : MOCK_DETECTIONS;
  const tracks = (showEmpty || !job || job.mediaType !== 'video') ? [] : MOCK_TRACKS;

  if (loading) return (
    <>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 24 }}>
        <window.Skel w={60} h={26} br={6}/><window.Skel w={200} h={18}/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 16 }}>
        <window.Skel w="100%" h={280} br={8}/>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[...Array(4)].map((_, i) => <window.Skel key={i} w="100%" h={60} br={8}/>)}
        </div>
      </div>
    </>
  );

  if (!job) return <div style={{ padding: 40, color: 'var(--text-3)' }}>Завдання не знайдено.</div>;

  return (
    <>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/jobs')}>
          <window.IcoArrowLeft size={13}/> Черга
        </button>
        <span style={{ color: 'var(--text-3)' }}>/</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)', maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{job.filename}</span>
        <window.StatusBadge status={job.status}/>
      </div>

      {/* Active progress */}
      {(job.status === 'queued' || job.status === 'processing') && (
        <div className="card" style={{ padding: '13px 18px', marginBottom: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 9 }}>
            <span style={{ fontSize: 13, color: 'var(--text-2)' }}>
              {job.status === 'queued' ? 'Очікує в черзі…' : 'Завдання обробляється…'}
            </span>
            {job.progress > 0 && <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent-text)' }}>{job.progress}%</span>}
          </div>
          <window.ProgressBar value={job.progress || 0} color={job.status === 'queued' ? 'var(--muted-text)' : 'var(--accent)'}/>
          <div style={{ marginTop: 7, fontSize: 11, color: 'var(--text-3)' }}>Оновлено: {fmt(job.created)}</div>
        </div>
      )}

      {/* Error */}
      {job.status === 'failed' && job.error && (
        <div className="error-banner" style={{ marginBottom: 14 }}>
          <window.IcoAlertCircle size={15} style={{ flexShrink: 0, marginTop: 1 }}/>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 2 }}>Помилка обробки</div>
            <div style={{ fontSize: 12, opacity: 0.85 }}>{job.error}</div>
          </div>
        </div>
      )}

      {/* Top row: media placeholder + summary */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 16, marginBottom: 16 }} className="resp-grid-col-side">
        {/* Placeholder */}
        <div className="preview-placeholder" style={{ minHeight: 260 }}>
          {job.mediaType === 'video' ? <window.IcoVideo size={38}/> : <window.IcoImage size={38}/>}
          <span style={{ fontWeight: 500 }}>
            {job.status === 'completed' ? 'Анотований результат' : 'Попередній перегляд недоступний'}
          </span>
          {job.status === 'completed' && job.mediaType === 'video' && (
            <span style={{ fontSize: 12 }}>Відтворення у браузері може бути недоступним — завантажте файл нижче</span>
          )}
        </div>

        {/* Summary column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            { label: 'Виявлень',       val: job.detections != null ? job.detections.toLocaleString('uk-UA') : '—', icon: <window.IcoActivity size={14}/> },
            { label: 'Сер. впевн.',    val: job.avgConf    ? `${(job.avgConf * 100).toFixed(1)}%`   : '—', icon: <window.IcoPercent size={14}/> },
            { label: 'Середній FPS',   val: job.avgFps     ? job.avgFps.toFixed(1)                   : '—', icon: <window.IcoZap size={14}/> },
            { label: 'Тривалість',     val: dur(job.duration),                                               icon: <window.IcoClock size={14}/> },
          ].map(item => (
            <div key={item.label} className="card" style={{ padding: '11px 15px', display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: 'var(--text-3)', flexShrink: 0 }}>{item.icon}</span>
              <div>
                <div style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>{item.label}</div>
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: 20, fontWeight: 700, marginTop: 1, lineHeight: 1 }}>{item.val}</div>
              </div>
            </div>
          ))}

          {/* Job params */}
          <div className="card" style={{ padding: '11px 15px' }}>
            <div style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700, marginBottom: 9 }}>Параметри</div>
            {[
              ['Модель',     job.model],
              ['Впевненість', job.conf.toFixed(2)],
              ['IoU',        job.iou.toFixed(2)],
              ...(job.tracker ? [['Трекер', job.tracker]] : []),
              ['Дата',       fmt(job.created)],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 5 }}>
                <span style={{ color: 'var(--text-3)' }}>{k}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Downloads */}
      {job.status === 'completed' && (
        <div className="card" style={{ padding: '12px 18px', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 13, color: 'var(--text-2)', fontWeight: 500, marginRight: 4 }}>Завантажити:</span>
            {[
              { label: job.mediaType === 'video' ? 'Анотоване відео' : 'Анотоване зображення', icon: <window.IcoDownload size={13}/> },
              { label: 'CSV-звіт',  icon: <window.IcoFileText size={13}/> },
              { label: 'JSON-дані', icon: <window.IcoFileText size={13}/> },
            ].map(d => (
              <button key={d.label} className="btn btn-secondary btn-sm">{d.icon} {d.label}</button>
            ))}
          </div>
        </div>
      )}

      {/* Detections table */}
      {job.status === 'completed' && (
        <div style={{ marginBottom: 16 }}>
          <window.SectionHeader title="Виявлення"/>
          <div className="card">
            {job.detections === 0 ? (
              <window.EmptyState icon={<window.IcoActivity size={24}/>} title="Виявлень не знайдено" subtitle="Модель не виявила жодного об'єкта у цьому файлі"/>
            ) : dets.length === 0 ? (
              <window.EmptyState icon={<window.IcoActivity size={24}/>} title="Дані відсутні"/>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead><tr><th>Кадр</th><th>Час</th><th>Клас</th><th>Впевненість</th><th>Bounding box</th><th>Track ID</th></tr></thead>
                  <tbody>
                    {dets.map((d, i) => (
                      <tr key={i}>
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{d.frame}</td>
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{d.ts}</td>
                        <td><span style={{ fontSize: 11, background: 'var(--accent-dim)', color: 'var(--accent-text)', padding: '2px 8px', borderRadius: 4 }}>{d.cls}</span></td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                            <div style={{ width: 44, height: 3, background: 'var(--surface-3)', borderRadius: 2, flexShrink: 0 }}>
                              <div style={{ width: `${d.conf * 100}%`, height: '100%', background: d.conf > 0.85 ? 'var(--success)' : 'var(--warning)', borderRadius: 2 }}/>
                            </div>
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)' }}>{(d.conf * 100).toFixed(0)}%</span>
                          </div>
                        </td>
                        <td><span className="bbox-value">{d.bbox}</span></td>
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{d.trackId ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {job.detections > dets.length && (
                  <div style={{ padding: '9px 14px', fontSize: 12, color: 'var(--text-3)', borderTop: '1px solid var(--border-subtle)' }}>
                    Показано {dets.length} із {job.detections.toLocaleString('uk-UA')} виявлень
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tracks */}
      {job.status === 'completed' && job.mediaType === 'video' && (
        <div style={{ marginBottom: 16 }}>
          <window.SectionHeader title="Треки об'єктів"/>
          <div className="card">
            {tracks.length === 0 ? (
              <window.EmptyState icon={<window.IcoActivity size={24}/>} title="Треки відсутні" subtitle="Для цього відео жодного треку не побудовано"/>
            ) : (
              <table className="data-table">
                <thead><tr><th>Track ID</th><th>Перший кадр</th><th>Останній кадр</th><th>Тривалість</th><th>Виявлень</th><th>Сер. впевненість</th></tr></thead>
                <tbody>
                  {tracks.map(t => (
                    <tr key={t.id}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600 }}>{t.id}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{t.firstFrame}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{t.lastFrame}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{t.duration}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{t.count}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{(t.avgConf * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </>
  );
};

Object.assign(window, { JobDetailPage });
