// Sidebar + AppShell with responsive mobile drawer
const { useState } = React;

const NAV_ITEMS = [
  { path: '/dashboard',    Icon: window.IcoDashboard, label: 'Огляд'          },
  { path: '/upload',       Icon: window.IcoUpload,    label: 'Завантаження'   },
  { path: '/jobs',         Icon: window.IcoJobs,      label: 'Черга'          },
  { path: '/models',       Icon: window.IcoPackage,   label: 'Реєстр'         },
  { path: '/experiments',  Icon: window.IcoFlask,     label: 'Досліди'        },
];

const ADMIN_ITEM = { path: '/admin', Icon: window.IcoShield, label: 'Адміністратор' };

const Sidebar = ({ route, navigate, user }) => {
  const isAdmin = user?.role === 'admin';
  const items = isAdmin ? [...NAV_ITEMS, ADMIN_ITEM] : NAV_ITEMS;
  const isActive = p => p === '/jobs' ? (route === '/jobs' || route.startsWith('/jobs/')) : route === p;

  return (
    <nav className="sidebar">
      <div style={{ marginBottom: 10 }}>
        <div className="logo-mark">AV</div>
      </div>
      <div className="sidebar-divider"/>
      {items.map(({ path, Icon, label }) => (
        <window.NavTooltip key={path} label={label}>
          <button className={`nav-item ${isActive(path) ? 'active' : ''}`} onClick={() => navigate(path)}>
            <Icon size={17}/>
          </button>
        </window.NavTooltip>
      ))}
      <div style={{ flex: 1 }}/>
      <div className="sidebar-divider"/>
      <window.NavTooltip label={user?.email || 'Профіль'}>
        <button className="nav-item"><window.IcoUser size={17}/></button>
      </window.NavTooltip>
      <window.NavTooltip label="Вийти">
        <button className="nav-item" onClick={() => navigate('/login')}><window.IcoLogout size={17}/></button>
      </window.NavTooltip>
    </nav>
  );
};

/* ─── Mobile top bar + drawer ─── */
const MobileNav = ({ route, navigate, user }) => {
  const [open, setOpen] = useState(false);
  const isAdmin = user?.role === 'admin';
  const items = isAdmin ? [...NAV_ITEMS, ADMIN_ITEM] : NAV_ITEMS;
  const isActive = p => p === '/jobs' ? (route === '/jobs' || route.startsWith('/jobs/')) : route === p;

  const go = (path) => { navigate(path); setOpen(false); };

  return (
    <>
      <div className="mobile-topbar">
        <div className="logo-mark" style={{ width: 28, height: 28, fontSize: 11 }}>AV</div>
        <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: 15 }}>AeroVision</span>
        <button className="btn btn-ghost btn-sm" onClick={() => setOpen(v => !v)} style={{ padding: 6 }}>
          {open ? <window.IcoClose size={18}/> : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          )}
        </button>
      </div>
      <div className="mobile-topbar-push"/>

      {open && <div className="mobile-overlay" onClick={() => setOpen(false)}/>}

      <div className={`mobile-drawer ${open ? 'open' : ''}`}>
        {items.map(({ path, Icon, label }) => (
          <div key={path} className={`drawer-item ${isActive(path) ? 'active' : ''}`} onClick={() => go(path)}>
            <Icon size={16}/> {label}
          </div>
        ))}
        <div style={{ flex: 1 }}/>
        <div style={{ borderTop: '1px solid var(--border)', margin: '6px 0' }}/>
        <div className="drawer-item" onClick={() => { navigate('/login'); setOpen(false); }}>
          <window.IcoLogout size={16}/> Вийти
        </div>
      </div>
    </>
  );
};

/* ─── App shell ─── */
const AppShell = ({ route, navigate, user, children }) => (
  <div className="app-shell">
    <Sidebar route={route} navigate={navigate} user={user}/>
    <main className="main-content">
      <MobileNav route={route} navigate={navigate} user={user}/>
      <div className="page-content" key={route}>
        {children}
      </div>
    </main>
  </div>
);

Object.assign(window, { Sidebar, AppShell });
