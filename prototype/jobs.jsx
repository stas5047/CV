// Jobs list page
const { useState } = React;

const ALL_JOBS = [
  { id: 'j001', filename: 'patrol_footage_01.mp4',   status: 'completed', mediaType: 'video', model: 'YOLO26s-v1.2',     created: '2026-05-14T09:23:00Z', duration: 47,  detections: 312, avgConf: 0.87 },
  { id: 'j002', filename: 'aerial_snapshot_43.jpg',  status: 'completed', mediaType: 'image', model: 'YOLO26s-v1.2',     created: '2026-05-14T08:11:00Z', duration: 3,   detections: 1,   avgConf: 0.91 },
  { id: 'j003', filename: 'sector_scan_video.mp4',   status: 'processing',mediaType: 'video', model: 'YOLO26s-v1.2',     created: '2026-05-14T10:05:00Z', duration: null, detections: null,avgConf: null },
  { id: 'j004', filename: 'test_image_001.png',      status: 'failed',    mediaType: 'image', model: 'YOLO26s-v1.2',     created: '2026-05-13T16:40:00Z', duration: 2,   detections: null,avgConf: null },
  { id: 'j005', filename: 'night_patrol_27.mp4',     status: 'queued',    mediaType: 'video', model: 'YOLO26s-v1.2',     created: '2026-05-14T10:08:00Z', duration: null, detections: null,avgConf: null },
  { id: 'j006', filename: 'daylight_scan_08.jpg',    status: 'completed', mediaType: 'image', model: 'YOLO26n-v1.0',     created: '2026-05-13T14:22:00Z', duration: 4,   detections: 3,   avgConf: 0.79 },
  { id: 'j007', filename: 'flight_record_002.mp4',   status: 'completed', mediaType: 'video', model: 'YOLO26s-v1.2',     created: '2026-05-13T11:55:00Z', duration: 128, detections: 891, avgConf: 0.84 },
  { id: 'j008', filename: 'thermal_feed_01.mp4',     status: 'cancelled', mediaType: 'video', model: 'YOLO26s-v1.2',     created: '2026-05-12T18:30:00Z', duration: null, detections: null,avgConf: null },
  { id: 'j009', filename: 'surveillance_clip_05.mp4',status: 'completed', mediaType: 'video', model: 'YOLO11s-fallback', created: '2026-05-12T09:18:00Z', duration: 73,  detections: 204, avgConf: 0.76 },
  { id: 'j010', filename: 'frame_capture_112.webp',  status: 'completed', mediaType: 'image', model: 'YOLO26s-v1.2',     created: '2026-05-11T15:04:00Z', duration: 2,   detections: 0,   avgConf: null },
];

const JobsPage = ({ navigate, showEmpty }) => {
  const [statusF, setStatusF] = useState('all');
  const [typeF,   setTypeF]   = useState('all');
  const [search,  setSearch]  = useState('');

  const jobs = showEmpty ? [] : ALL_JOBS;

  const filtered = jobs.filter(j => {
    if (statusF !== 'all' && j.status !== statusF) return false;
    if (typeF   !== 'all' && j.mediaType !== typeF)  return false;
    if (search && !j.filename.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageStart  = (page - 1) * PAGE_SIZE;
  const paginated  = filtered.slice(pageStart, pageStart + PAGE_SIZE);

  // Reset to page 1 when filters change
  React.useEffect(() => { setPage(1); }, [statusF, typeF, search]);

  const fmt  = iso => new Date(iso).toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' });
  const dur  = s => s == null ? '—' : s < 60 ? `${s}с` : `${Math.floor(s / 60)}хв ${s % 60}с`;
  const conf = v => v == null ? '—' : `${(v * 100).toFixed(1)}%`;

  const [page, setPage] = useState(1);
  const PAGE_SIZE = 5;

  const statusOpts = [
    { id: 'all', label: 'Усі' }, { id: 'queued', label: 'У черзі' }, { id: 'processing', label: 'Обробляється' },
    { id: 'completed', label: 'Завершено' }, { id: 'failed', label: 'Збій' }, { id: 'cancelled', label: 'Скасовано' },
  ];

  return (
    <>
      <window.PageHeader
        title="Черга завдань"
        subtitle="Журнал усіх завдань обробки медіафайлів"
        actions={<button className="btn btn-primary" onClick={() => navigate('/upload')}><window.IcoPlus size={13}/> Нове завдання</button>}
      />

      {/* Filter bar */}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 14, flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', width: 230 }}>
          <window.IcoSearch size={13} style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)', pointerEvents: 'none' }}/>
          <input className="form-input" placeholder="Пошук за назвою…" value={search} onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: 28, paddingTop: 6, paddingBottom: 6, fontSize: 13 }}/>
        </div>

        <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
          {statusOpts.map(o => (
            <button key={o.id} className={`filter-chip ${statusF === o.id ? 'active' : ''}`} onClick={() => setStatusF(o.id)}>{o.label}</button>
          ))}
        </div>

        <select className="form-select" value={typeF} onChange={e => setTypeF(e.target.value)}
          style={{ width: 'auto', paddingTop: 5, paddingBottom: 5, fontSize: 13 }}>
          <option value="all">Всі типи</option>
          <option value="image">Зображення</option>
          <option value="video">Відео</option>
        </select>
      </div>

      <div className="card table-scroll">
        {filtered.length === 0 ? (
          <window.EmptyState
            icon={<window.IcoInbox size={28}/>}
            title={jobs.length === 0 ? 'Завдань ще немає' : 'Нічого не знайдено'}
            subtitle={jobs.length === 0 ? 'Завантажте перший файл для обробки' : 'Спробуйте змінити фільтри або пошуковий запит'}
            action={jobs.length === 0 ? <button className="btn btn-primary btn-sm" onClick={() => navigate('/upload')}><window.IcoUpload size={12}/> Завантажити</button> : null}
          />
        ) : (
          <table className="data-table">
            <thead>
              <tr><th>Статус</th><th>Файл</th><th className="resp-hide-col">Тип</th><th className="resp-hide-col">Модель</th><th>Дата</th><th>Виявлень</th><th className="resp-hide-col">Впевн.</th><th className="resp-hide-col">Тривалість</th><th></th></tr>
            </thead>
            <tbody>
              {paginated.map(j => (
                <tr key={j.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/jobs/${j.id}`)}>
                  <td><window.StatusBadge status={j.status}/></td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                      <span style={{ color: 'var(--text-3)', flexShrink: 0 }}>{j.mediaType === 'video' ? <window.IcoVideo size={12}/> : <window.IcoImage size={12}/>}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.filename}</span>
                    </div>
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text-3)' }}>{j.mediaType === 'video' ? 'Відео' : 'Зобр.'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)' }}>{j.model}</td>
                  <td style={{ fontSize: 12, color: 'var(--text-3)', whiteSpace: 'nowrap' }}>{fmt(j.created)}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: j.detections != null ? 'var(--text-1)' : 'var(--text-3)' }}>
                    {j.detections != null ? j.detections.toLocaleString('uk-UA') : '—'}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: j.avgConf != null ? 'var(--text-1)' : 'var(--text-3)' }}>
                    {conf(j.avgConf)}
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text-3)' }}>{dur(j.duration)}</td>
                  <td>
                    <button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); navigate(`/jobs/${j.id}`); }}>
                      <window.IcoEye size={12}/>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {filtered.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12, fontSize: 12, color: 'var(--text-3)' }}>
          <span>
            {filtered.length === 0 ? 'Немає результатів' :
              `Показано ${pageStart + 1}–${Math.min(pageStart + PAGE_SIZE, filtered.length)} із ${filtered.length} завдань`}
          </span>
          <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
            <button className="btn btn-ghost btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Назад</button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
              <button key={p} onClick={() => setPage(p)} style={{
                padding: '3px 9px', borderRadius: 4, fontSize: 12, border: 'none', cursor: 'pointer',
                background: page === p ? 'var(--accent-dim)' : 'transparent',
                color: page === p ? 'var(--accent-text)' : 'var(--text-3)',
                fontWeight: page === p ? 600 : 400,
              }}>{p}</button>
            ))}
            <button className="btn btn-ghost btn-sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Далі →</button>
          </div>
        </div>
      )}
    </>
  );
};

Object.assign(window, { JobsPage, ALL_JOBS });
