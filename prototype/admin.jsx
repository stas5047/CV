// Admin page
const { useState } = React;

const GLOBAL_STATS = { totalUsers: 12, totalFiles: 1847, totalJobs: 2341, totalDetections: 23419, storageUsed: 48.7, storageTotal: 200 };

const USERS_LIST = [
  { id: 'u001', email: 'admin@aerovision.ua',       role: 'admin', jobCount: 45,  created: '2026-01-15' },
  { id: 'u002', email: 'analyst@aerovision.ua',     role: 'user',  jobCount: 312, created: '2026-02-10' },
  { id: 'u003', email: 'operator01@aerovision.ua',  role: 'user',  jobCount: 189, created: '2026-03-05' },
  { id: 'u004', email: 'operator02@aerovision.ua',  role: 'user',  jobCount: 97,  created: '2026-03-20' },
  { id: 'u005', email: 'researcher@aerovision.ua',  role: 'user',  jobCount: 28,  created: '2026-04-11' },
];

const AdminPage = ({ navigate, showEmpty }) => {
  const [cleanConfirm, setCleanConfirm] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [cleaned, setCleaned] = useState(false);
  const toast = window.useToast?.();

  const stats = showEmpty ? null : GLOBAL_STATS;
  const users = showEmpty ? [] : USERS_LIST;
  const jobs  = showEmpty ? [] : (window.ALL_JOBS || []);

  const storagePct = stats ? Math.round((stats.storageUsed / stats.storageTotal) * 100) : 0;
  const storageColor = storagePct > 80 ? 'var(--danger)' : storagePct > 60 ? 'var(--warning)' : 'var(--accent)';

  const handleCleanup = () => {
    setCleaning(true);
    setTimeout(() => {
      setCleaning(false);
      setCleanConfirm(false);
      setCleaned(true);
      toast?.addToast('Очищення сховища завершено. Видалено 1.2 ГБ тимчасових файлів.', 'success');
    }, 1400);
  };

  return (
    <>
      <window.PageHeader title="Адміністрування" subtitle="Глобальна статистика, управління моделями та користувачами"/>

      {/* Global stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 22 }} className="resp-grid-4">
        <window.MetricCard label="Користувачів"   value={stats?.totalUsers ?? '—'}                           icon={<window.IcoUsers size={14}/>}/>
        <window.MetricCard label="Завдань всього"  value={stats?.totalJobs?.toLocaleString('uk-UA') ?? '—'}  icon={<window.IcoJobs size={14}/>}/>
        <window.MetricCard label="Виявлень всього" value={stats?.totalDetections?.toLocaleString('uk-UA') ?? '—'} icon={<window.IcoActivity size={14}/>}/>
        <div className="card metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span className="metric-label">Сховище</span>
            <span style={{ color: 'var(--text-3)', opacity: 0.55, flexShrink: 0 }}><window.IcoHardDrive size={14}/></span>
          </div>
          <div className="metric-value">{stats ? `${stats.storageUsed} ГБ` : '—'}</div>
          {stats && (
            <>
              <window.ProgressBar value={stats.storageUsed} max={stats.storageTotal} color={storageColor}/>
              <div className="metric-sub">{storagePct}% з {stats.storageTotal} ГБ</div>
            </>
          )}
        </div>
      </div>

      {/* Main content grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 260px', gap: 18, marginBottom: 22 }} className="resp-grid-col-side">

        {/* Recent global jobs */}
        <div className="card">
          <div style={{ padding: '14px 20px 0' }}>
            <window.SectionHeader title="Останні завдання (усі користувачі)" action={
              <button className="btn btn-ghost btn-sm" onClick={() => navigate('/jobs')}>
                Усі <window.IcoChevronRight size={12}/>
              </button>
            }/>
          </div>
          {jobs.length === 0 ? (
            <window.EmptyState icon={<window.IcoInbox size={24}/>} title="Завдань ще немає"/>
          ) : (
            <table className="data-table">
              <thead><tr><th>Статус</th><th>Файл</th><th>Модель</th><th>Дата</th><th></th></tr></thead>
              <tbody>
                {jobs.slice(0, 6).map((j, idx) => (
                  <tr key={j.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/jobs/${j.id}`)}>
                    <td><window.StatusBadge status={j.status} size="sm"/></td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ color: 'var(--text-3)', flexShrink: 0 }}>{j.mediaType === 'video' ? <window.IcoVideo size={11}/> : <window.IcoImage size={11}/>}</span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.filename}</span>
                      </div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-3)' }}>{j.model}</td>
                    <td style={{ fontSize: 11, color: 'var(--text-3)', whiteSpace: 'nowrap' }}>{new Date(j.created).toLocaleDateString('uk-UA')}</td>
                    <td>
                      <button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); navigate(`/jobs/${j.id}`); }}>
                        <window.IcoEye size={11}/>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* System actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div className="card" style={{ padding: '15px 18px' }}>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: 13, fontWeight: 600, marginBottom: 13 }}>Управління системою</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
              <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }} onClick={() => navigate('/models')}>
                <window.IcoCpu size={13}/> Реєстр моделей
              </button>
              <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }} onClick={() => navigate('/experiments')}>
                <window.IcoFlask size={13}/> Імпорт метрик
              </button>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: 10, marginTop: 4 }}>
                {!cleanConfirm ? (
                  <button className="btn btn-danger" style={{ width: '100%', justifyContent: 'flex-start' }} onClick={() => setCleanConfirm(true)} disabled={cleaned}>
                    <window.IcoHardDrive size={13}/> {cleaned ? 'Очищено' : 'Очистити сховище'}
                  </button>
                ) : (
                  <div style={{ background: 'var(--danger-dim)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius)', padding: '11px 13px' }}>
                    <div style={{ fontSize: 12, color: 'var(--danger-text)', marginBottom: 10, lineHeight: 1.5 }}>
                      Видаляються лише невикористані тимчасові файли. Активні моделі та збережені результати не торкаються.
                    </div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn btn-sm" style={{ background: 'var(--danger)', color: '#fff', flex: 1, justifyContent: 'center' }}
                        onClick={handleCleanup} disabled={cleaning}>
                        {cleaning ? <window.Spinner size={12}/> : 'Підтвердити'}
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setCleanConfirm(false)}>Скасувати</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Users table */}
      <div>
        <window.SectionHeader title="Користувачі системи"/>
        <div className="card">
          {users.length === 0 ? (
            <window.EmptyState icon={<window.IcoUsers size={24}/>} title="Користувачів не знайдено"/>
          ) : (
            <table className="data-table">
              <thead><tr><th>Email</th><th>Роль</th><th>Завдань</th><th>Зареєстрований</th></tr></thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{u.email}</td>
                    <td>
                      <span style={{
                        fontSize: 10, padding: '2px 8px', borderRadius: 99, fontWeight: 700, letterSpacing: '0.03em',
                        background: u.role === 'admin' ? 'var(--accent-dim)' : 'var(--surface-3)',
                        color:      u.role === 'admin' ? 'var(--accent-text)' : 'var(--text-3)',
                      }}>
                        {u.role === 'admin' ? 'АДМІН' : 'ЮЗЕР'}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>{u.jobCount}</td>
                    <td style={{ fontSize: 12, color: 'var(--text-3)' }}>{u.created}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
};

Object.assign(window, { AdminPage });
