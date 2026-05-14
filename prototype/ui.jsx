// Shared UI primitives
const { useState, useEffect, createContext, useContext } = React;

/* ─── Status badge ─── */
const statusCfg = {
  queued:     { label: 'У черзі',      bg: 'var(--muted-dim)',   color: 'var(--muted-text)',   dot: 'var(--muted-text)',  pulse: false },
  processing: { label: 'Обробляється', bg: 'var(--accent-dim)',  color: 'var(--accent-text)',  dot: 'var(--accent)',      pulse: true  },
  completed:  { label: 'Завершено',    bg: 'var(--success-dim)', color: 'var(--success-text)', dot: 'var(--success)',     pulse: false },
  failed:     { label: 'Збій',         bg: 'var(--danger-dim)',  color: 'var(--danger-text)',  dot: 'var(--danger)',      pulse: false },
  cancelled:  { label: 'Скасовано',    bg: 'rgba(20,32,52,0.7)', color: 'var(--text-3)',       dot: 'var(--text-3)',      pulse: false },
};

const StatusBadge = ({ status, size = 'md' }) => {
  const cfg = statusCfg[status] || statusCfg.queued;
  return (
    <span className="badge" style={{
      background: cfg.bg, color: cfg.color,
      padding: size === 'sm' ? '2px 7px' : '3px 9px',
      fontSize: size === 'sm' ? '10px' : '11px',
    }}>
      <span style={{
        width: 5, height: 5, borderRadius: '50%', background: cfg.dot,
        flexShrink: 0, display: 'inline-block',
        animation: cfg.pulse ? 'pulse 1.3s ease-in-out infinite' : 'none',
      }}/>
      {cfg.label}
    </span>
  );
};

/* ─── Metric card ─── */
const MetricCard = ({ label, value, sub, icon, children }) => (
  <div className="card metric-card">
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
      <span className="metric-label">{label}</span>
      {icon && <span style={{ color: 'var(--text-3)', opacity: 0.55, flexShrink: 0 }}>{icon}</span>}
    </div>
    <div className="metric-value">{value ?? '—'}</div>
    {sub && <div className="metric-sub">{sub}</div>}
    {children}
  </div>
);

/* ─── Skeleton ─── */
const Skel = ({ w = '100%', h = 14, mb = 0, br = 4 }) => (
  <div className="skeleton" style={{ width: w, height: h, marginBottom: mb, borderRadius: br }}/>
);

/* ─── Empty state ─── */
const EmptyState = ({ icon, title, subtitle, action }) => (
  <div style={{
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', gap: 10, padding: '48px 24px',
    color: 'var(--text-3)', textAlign: 'center',
  }}>
    {icon && <span style={{ opacity: 0.3, marginBottom: 2 }}>{icon}</span>}
    <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-2)' }}>{title}</div>
    {subtitle && <div style={{ fontSize: 13, maxWidth: 300, lineHeight: 1.5 }}>{subtitle}</div>}
    {action && <div style={{ marginTop: 10 }}>{action}</div>}
  </div>
);

/* ─── Page header ─── */
const PageHeader = ({ title, subtitle, actions }) => (
  <div className="page-header">
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      {actions && <div style={{ display: 'flex', gap: 8, flexShrink: 0, alignItems: 'center' }}>{actions}</div>}
    </div>
  </div>
);

/* ─── Section header ─── */
const SectionHeader = ({ title, action }) => (
  <div className="section-header">
    <h2 className="section-title">{title}</h2>
    {action}
  </div>
);

/* ─── Spinner ─── */
const Spinner = ({ size = 16, color = 'var(--accent)' }) => (
  <div style={{
    width: size, height: size,
    border: `2px solid var(--border)`, borderTopColor: color,
    borderRadius: '50%', animation: 'spin 0.55s linear infinite', flexShrink: 0,
  }}/>
);

/* ─── Progress bar ─── */
const ProgressBar = ({ value, max = 100, color = 'var(--accent)' }) => {
  const pct = Math.min(100, Math.max(0, ((value ?? 0) / max) * 100));
  return (
    <div className="progress-bar">
      <div className="progress-bar-fill" style={{ width: `${pct}%`, background: color }}/>
    </div>
  );
};

/* ─── Tabs ─── */
const Tabs = ({ tabs, active, onChange }) => (
  <div style={{
    display: 'flex', gap: 2, background: 'var(--surface-2)',
    padding: 4, borderRadius: 'var(--radius-md)', width: 'fit-content',
  }}>
    {tabs.map(tab => (
      <button key={tab.id} onClick={() => onChange(tab.id)} style={{
        padding: '5px 14px', borderRadius: 'var(--radius)', fontSize: 13, fontWeight: 500,
        background: active === tab.id ? 'var(--surface-3)' : 'transparent',
        color: active === tab.id ? 'var(--text-1)' : 'var(--text-2)',
        border: 'none', cursor: 'pointer', transition: 'all 0.12s', lineHeight: 1.4,
      }}>
        {tab.label}
      </button>
    ))}
  </div>
);

/* ─── Nav tooltip ─── */
const NavTooltip = ({ children, label }) => (
  <div className="tooltip-wrap">
    {children}
    <span className="tooltip-label">{label}</span>
  </div>
);

/* ─── Toast ─── */
const ToastCtx = createContext(null);

const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const addToast = (message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), duration);
  };
  const remove = id => setToasts(prev => prev.filter(t => t.id !== id));

  const cfgs = {
    success: { bg: 'var(--success-dim)', bc: 'rgba(16,185,129,0.2)', color: 'var(--success-text)', Icon: window.IcoCheckCircle },
    error:   { bg: 'var(--danger-dim)',  bc: 'rgba(239,68,68,0.2)',   color: 'var(--danger-text)',  Icon: window.IcoXCircle    },
    info:    { bg: 'var(--accent-dim)',  bc: 'rgba(59,130,246,0.2)',   color: 'var(--accent-text)',  Icon: window.IcoInfo       },
    warning: { bg: 'var(--warning-dim)', bc: 'rgba(245,158,11,0.2)',  color: 'var(--warning-text)', Icon: window.IcoAlertTriangle },
  };

  return (
    <ToastCtx.Provider value={{ addToast }}>
      {children}
      <div className="toast-container">
        {toasts.map(t => {
          const c = cfgs[t.type] || cfgs.info;
          return (
            <div key={t.id} className="toast" style={{ background: c.bg, borderColor: c.bc, color: c.color }}>
              {c.Icon && <c.Icon size={14} style={{ flexShrink: 0, marginTop: 1 }}/>}
              <span style={{ flex: 1, fontSize: 13, lineHeight: 1.45 }}>{t.message}</span>
              <button onClick={() => remove(t.id)} style={{ background: 'none', color: 'inherit', opacity: 0.6, padding: 2, cursor: 'pointer', flexShrink: 0, border: 'none' }}>
                <window.IcoClose size={12}/>
              </button>
            </div>
          );
        })}
      </div>
    </ToastCtx.Provider>
  );
};

const useToast = () => useContext(ToastCtx);

/* ─── Mini bar (used in metrics/models) ─── */
const MiniBar = ({ value, max = 1, color = 'var(--accent)', height = 3 }) => {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
      <div style={{ flex: 1, height, background: 'var(--surface-3)', borderRadius: 99 }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 99 }}/>
      </div>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)', minWidth: 36, textAlign: 'right' }}>
        {(value * 100).toFixed(1)}%
      </span>
    </div>
  );
};

Object.assign(window, {
  StatusBadge, MetricCard, Skel, EmptyState,
  PageHeader, SectionHeader, Spinner, ProgressBar,
  Tabs, NavTooltip, ToastProvider, useToast, MiniBar, statusCfg,
});
