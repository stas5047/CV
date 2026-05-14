// Upload & processing page
const { useState, useRef, useCallback, useEffect } = React;

const UploadPage = ({ navigate }) => {
  const [file, setFile]       = useState(null);
  const [drag, setDrag]       = useState(false);
  const [model, setModel]     = useState('YOLO26s-v1.2');
  const [conf, setConf]       = useState(0.25);
  const [iou, setIou]         = useState(0.45);
  const [tracker, setTracker] = useState('ByteTrack');
  const [job, setJob]         = useState(null);   // null | 'submitting' | jobObj
  const [submitting, setSub]  = useState(false);
  const inputRef = useRef(null);

  const isVideo = file && /\.(mp4|avi|mov|mkv)$/i.test(file.name);
  const fmtSize = bytes => bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} КБ` : `${(bytes / 1048576).toFixed(1)} МБ`;

  const accept = f => {
    if (!f) return;
    const ok = /\.(jpg|jpeg|png|webp|mp4|avi|mov|mkv)$/i.test(f.name);
    const lim = /\.(mp4|avi|mov|mkv)$/i.test(f.name) ? 500 * 1048576 : 20 * 1048576;
    if (!ok)        { alert('Непідтримуваний формат файлу'); return; }
    if (f.size > lim){ alert('Файл перевищує допустимий розмір'); return; }
    setFile(f); setJob(null);
  };

  const onDrop = useCallback(e => {
    e.preventDefault(); setDrag(false);
    accept(e.dataTransfer.files[0]);
  }, []);

  const startJob = () => {
    if (!file) return;
    setSub(true);
    const newJobId = 'j-upload-' + Date.now();
    setTimeout(() => {
      setSub(false);
      const newJob = { id: newJobId, status: 'queued', progress: 0 };
      setJob(newJob);
      // Store new job info for detail page
      window.__uploadedJobs = window.__uploadedJobs || {};
      window.__uploadedJobs[newJobId] = {
        id: newJobId, filename: file.name,
        mediaType: /\.(mp4|avi|mov|mkv)$/i.test(file.name) ? 'video' : 'image',
        model, conf, iou, tracker,
        created: new Date().toISOString(),
        status: 'queued', progress: 0,
      };
      let p = 0;
      const iv = setInterval(() => {
        p += Math.random() * 9 + 2;
        const done = p >= 100;
        if (done) { p = 100; clearInterval(iv); }
        const newStatus = done ? 'completed' : 'processing';
        setJob(j => ({ ...j, status: newStatus, progress: Math.floor(p) }));
        window.__uploadedJobs[newJobId].status   = newStatus;
        window.__uploadedJobs[newJobId].progress = Math.floor(p);
        if (done) {
          window.__uploadedJobs[newJobId].detections = Math.floor(Math.random() * 50) + 1;
          window.__uploadedJobs[newJobId].avgConf    = 0.75 + Math.random() * 0.2;
          window.__uploadedJobs[newJobId].duration   = Math.floor(Math.random() * 30) + 2;
        }
      }, 550);
    }, 700);
  };

  const Slider = ({ label, value, min, max, step, onChange }) => (
    <div className="form-field">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <label className="form-label">{label}</label>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent-text)', background: 'var(--accent-dim)', padding: '1px 8px', borderRadius: 4 }}>
          {value.toFixed(2)}
        </span>
      </div>
      <input type="range" className="range-slider" min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}/>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
        <span style={{ fontSize: 10, color: 'var(--text-3)' }}>{min}</span>
        <span style={{ fontSize: 10, color: 'var(--text-3)' }}>{max}</span>
      </div>
    </div>
  );

  return (
    <>
      <window.PageHeader title="Завантаження" subtitle="Завантажте медіафайл та запустіть обробку"/>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 20, alignItems: 'start' }} className="resp-grid-col-side">

        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

          {!file ? (
            <div className={`drop-zone ${drag ? 'drag-over' : ''}`}
              onDragOver={e => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={onDrop}
              onClick={() => inputRef.current?.click()}>
              <div style={{ width: 52, height: 52, borderRadius: 14, background: 'var(--accent-dim)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <window.IcoUpload size={24} style={{ color: 'var(--accent)' }}/>
              </div>
              <div>
                <div style={{ fontWeight: 500, color: 'var(--text-1)', marginBottom: 5 }}>Перетягніть файл або натисніть для вибору</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)', lineHeight: 1.6 }}>
                  Зображення: JPG, PNG, WEBP — до 20 МБ<br/>
                  Відео: MP4, AVI, MOV, MKV — до 500 МБ
                </div>
              </div>
              <input ref={inputRef} type="file" accept=".jpg,.jpeg,.png,.webp,.mp4,.avi,.mov,.mkv"
                style={{ display: 'none' }} onChange={e => accept(e.target.files[0])}/>
            </div>
          ) : (
            <div className="card" style={{ padding: '14px 18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 42, height: 42, borderRadius: 10, background: 'var(--surface-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {isVideo ? <window.IcoVideo size={20} style={{ color: 'var(--accent)' }}/> : <window.IcoImage size={20} style={{ color: 'var(--accent)' }}/>}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>{isVideo ? 'Відео' : 'Зображення'} · {fmtSize(file.size)}</div>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => { setFile(null); setJob(null); }}>
                  <window.IcoClose size={13}/>
                </button>
              </div>
              <div className="preview-placeholder" style={{ marginTop: 14, height: 200 }}>
                {isVideo ? <window.IcoVideo size={34}/> : <window.IcoImage size={34}/>}
                <span>Попередній перегляд недоступний</span>
              </div>
            </div>
          )}

          {/* Job status card */}
          {job && (
            <div className="card" style={{ padding: '14px 18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-2)' }}>Завдання {job.id}</span>
                <window.StatusBadge status={job.status}/>
              </div>
              {job.status !== 'completed' && (
                <>
                  <window.ProgressBar value={job.progress}/>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 7 }}>
                    <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{job.status === 'queued' ? 'Очікує в черзі…' : 'Обробляється…'}</span>
                    <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-text)' }}>{job.progress}%</span>
                  </div>
                </>
              )}
              {job.status === 'completed' && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <window.IcoCheckCircle size={14} style={{ color: 'var(--success)', flexShrink: 0 }}/>
                  <span style={{ fontSize: 13, color: 'var(--success-text)' }}>Обробку завершено успішно</span>
                  <button className="btn btn-secondary btn-sm" style={{ marginLeft: 'auto' }} onClick={() => navigate(`/jobs/${job.id}`)}>
                    Результати <window.IcoChevronRight size={12}/>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: parameters */}
        <div className="card" style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div style={{ fontFamily: 'var(--font-heading)', fontSize: 13, fontWeight: 600, paddingBottom: 14, borderBottom: '1px solid var(--border)' }}>
            Параметри обробки
          </div>

          <div className="form-field">
            <label className="form-label">Модель</label>
            <select className="form-select" value={model} onChange={e => setModel(e.target.value)}>
              <option value="YOLO26s-v1.2">YOLO26s-v1.2 (активна)</option>
              <option value="YOLO26n-v1.0">YOLO26n-v1.0</option>
              <option value="YOLO11s-fallback">YOLO11s (резервна)</option>
            </select>
          </div>

          <Slider label="Поріг впевненості" value={conf} min={0.05} max={0.95} step={0.05} onChange={setConf}/>
          <Slider label="Поріг IoU"         value={iou}  min={0.10} max={0.90} step={0.05} onChange={setIou}/>

          {isVideo && (
            <div className="form-field">
              <label className="form-label">Трекер</label>
              <select className="form-select" value={tracker} onChange={e => setTracker(e.target.value)}>
                <option value="ByteTrack">ByteTrack (типово)</option>
                <option value="BoT-SORT">BoT-SORT</option>
              </select>
            </div>
          )}

          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 14 }}>
            <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '9px' }}
              disabled={!file || submitting || job?.status === 'processing' || job?.status === 'queued'}
              onClick={startJob}>
              {submitting
                ? <><window.Spinner size={14}/> Створення завдання…</>
                : <><window.IcoZap size={14}/> Запустити обробку</>}
            </button>
            {!file && <p style={{ fontSize: 11, color: 'var(--text-3)', textAlign: 'center', marginTop: 8 }}>Спочатку завантажте файл</p>}
          </div>
        </div>
      </div>
    </>
  );
};

Object.assign(window, { UploadPage });
