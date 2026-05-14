// Models registry page
const { useState } = React;

const MODELS = [
  { id: 'm001', name: 'YOLO26s-v1.2', family: 'YOLO26', variant: 's', active: true,  dataset: 'AeroDrone-v3 (fine-tuned)', mAP50: 0.891, mAP5095: 0.734, precision: 0.912, recall: 0.876, size: 22.4, registered: '2026-04-15' },
  { id: 'm002', name: 'YOLO26n-v1.0', family: 'YOLO26', variant: 'n', active: false, dataset: 'AeroDrone-v2',               mAP50: 0.843, mAP5095: 0.681, precision: 0.867, recall: 0.821, size: 5.8,  registered: '2026-03-10' },
  { id: 'm003', name: 'YOLO11s-fallback', family: 'YOLO11', variant: 's', active: false, dataset: 'AeroDrone-v2 (fallback)', mAP50: 0.798, mAP5095: 0.623, precision: 0.819, recall: 0.779, size: 19.1, registered: '2026-02-28' },
];

const ModelsPage = ({ user, showEmpty }) => {
  const [showForm, setShowForm] = useState(false);
  const [activating, setActivating] = useState(null);
  const [models, setModels] = useState(MODELS);
  const isAdmin = user?.role === 'admin';
  const list = showEmpty ? [] : models;

  const activate = (id) => {
    setActivating(id);
    setTimeout(() => {
      setModels(prev => prev.map(m => ({ ...m, active: m.id === id })));
      setActivating(null);
    }, 700);
  };

  return (
    <>
      <window.PageHeader
        title="Реєстр моделей"
        subtitle="Зареєстровані версії моделей виявлення"
        actions={isAdmin ? (
          <button className="btn btn-primary" onClick={() => setShowForm(v => !v)}>
            <window.IcoPlus size={13}/> Зареєструвати модель
          </button>
        ) : null}
      />

      {/* Register form (admin only) */}
      {isAdmin && showForm && (
        <div className="card" style={{ padding: '16px 20px', marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 600 }}>Нова модель</span>
            <button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}><window.IcoClose size={13}/></button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 16 }}>
            {[
              { l: 'Назва',    p: 'YOLO26s-v1.3',  t: 'text'   },
              { l: 'Датасет',  p: 'AeroDrone-v3',   t: 'text'   },
              { l: 'Розмір МБ',p: '22.4',           t: 'number' },
            ].map(f => (
              <div key={f.l} className="form-field">
                <label className="form-label">{f.l}</label>
                <input type={f.t} className="form-input" placeholder={f.p}/>
              </div>
            ))}
            <div className="form-field">
              <label className="form-label">Сімейство</label>
              <select className="form-select"><option>YOLO26</option><option>YOLO11</option></select>
            </div>
            <div className="form-field">
              <label className="form-label">Варіант</label>
              <select className="form-select"><option>n</option><option>s</option><option>m</option><option>l</option></select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-primary btn-sm"><window.IcoCheck size={12}/> Зареєструвати</button>
            <button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}>Скасувати</button>
          </div>
        </div>
      )}

      {list.length === 0 ? (
        <div className="card">
          <window.EmptyState icon={<window.IcoCpu size={26}/>} title="Моделей не зареєстровано" subtitle="Зареєструйте першу модель для початку роботи"/>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {list.map(m => (
            <div key={m.id} className="card" style={{ padding: '18px 20px', borderLeft: `2px solid ${m.active ? 'var(--accent)' : 'transparent'}` }}>
              {/* Header row */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: m.active ? 'var(--accent-dim)' : 'var(--surface-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <window.IcoCpu size={17} style={{ color: m.active ? 'var(--accent)' : 'var(--text-3)' }}/>
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 600 }}>{m.name}</span>
                      {m.active && (
                        <span style={{ fontSize: 10, fontWeight: 700, background: 'var(--success-dim)', color: 'var(--success-text)', padding: '1px 8px', borderRadius: 99, letterSpacing: '0.03em' }}>АКТИВНА</span>
                      )}
                      <span style={{ fontSize: 11, background: 'var(--surface-3)', color: 'var(--text-3)', padding: '1px 8px', borderRadius: 4 }}>
                        {m.family} · {m.variant}
                      </span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 3 }}>{m.dataset}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
                  <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{m.size} МБ · {m.registered}</span>
                  {isAdmin && !m.active && (
                    <button className="btn btn-secondary btn-sm" onClick={() => activate(m.id)} disabled={!!activating}>
                      {activating === m.id ? <window.Spinner size={12}/> : <><window.IcoCheck size={12}/> Активувати</>}
                    </button>
                  )}
                </div>
              </div>

              {/* Metrics bars */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }} className="resp-grid-4">
                {[
                  { label: 'mAP@50',    val: m.mAP50,    color: 'var(--accent)'   },
                  { label: 'mAP@50-95', val: m.mAP5095,  color: 'var(--accent)'   },
                  { label: 'Precision', val: m.precision, color: 'var(--success)'  },
                  { label: 'Recall',    val: m.recall,    color: 'var(--warning)'  },
                ].map(met => (
                  <div key={met.label}>
                    <div style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.055em', fontWeight: 700, marginBottom: 5 }}>{met.label}</div>
                    <window.MiniBar value={met.val} color={met.color} height={3}/>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
};

Object.assign(window, { ModelsPage });
