// Main app — routing, state, tweaks
const { useState, useEffect } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "role": "admin",
  "showEmpty": false,
  "accent": "#3d8b6a"
}/*EDITMODE-END*/;

// Apply accent immediately before first render
document.documentElement.style.setProperty('--accent', TWEAK_DEFAULTS.accent);
document.documentElement.style.setProperty('--accent-hover', '#2d7a5a');

const App = () => {
  const [route,    setRoute]    = useState('/login');
  const [user,     setUser]     = useState(null);
  const [tweaks,   setTweaks]   = useState(TWEAK_DEFAULTS);
  const [twPanel,  setTwPanel]  = useState(false);

  /* Tweaks protocol */
  useEffect(() => {
    const handler = e => {
      if (e.data?.type === '__activate_edit_mode')   setTwPanel(true);
      if (e.data?.type === '__deactivate_edit_mode') setTwPanel(false);
    };
    window.addEventListener('message', handler);
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', handler);
  }, []);

  const setTweak = (key, val) => {
    setTweaks(prev => {
      const next = { ...prev, [key]: val };
      window.parent.postMessage({ type: '__edit_mode_set_keys', edits: { [key]: val } }, '*');
      if (key === 'accent') {
        document.documentElement.style.setProperty('--accent', val);
        // Compute a slightly darker hover tone
        document.documentElement.style.setProperty('--accent-hover', val);
      }
      if (key === 'role' && user) setUser(u => ({ ...u, role: val }));
      return next;
    });
  };

  /* Apply accent on mount */
  useEffect(() => {
    document.documentElement.style.setProperty('--accent', tweaks.accent);
  }, []);

  const navigate = path => setRoute(path);

  const handleLogin = u => {
    setUser({ ...u, role: tweaks.role });
    navigate('/dashboard');
  };

  /* Route → job ID */
  const jobId = route.startsWith('/jobs/') ? route.replace('/jobs/', '') : null;

  /* Page content */
  const renderPage = () => {
    if (route === '/login')    return <window.LoginPage    navigate={navigate} onLogin={handleLogin}/>;
    if (route === '/register') return <window.RegisterPage navigate={navigate}/>;

    if (!user) { navigate('/login'); return null; }

    const props = { navigate, user, showEmpty: tweaks.showEmpty };

    let content;
    if      (route === '/dashboard')                         content = <window.DashboardPage  {...props}/>;
    else if (route === '/upload')                            content = <window.UploadPage     {...props}/>;
    else if (route === '/jobs')                              content = <window.JobsPage       {...props}/>;
    else if (jobId)                                          content = <window.JobDetailPage  {...props} jobId={jobId}/>;
    else if (route === '/models')                            content = <window.ModelsPage     {...props}/>;
    else if (route === '/experiments')                       content = <window.ExperimentsPage {...props}/>;
    else if (route === '/admin' && user.role === 'admin')    content = <window.AdminPage      {...props}/>;
    else if (route === '/admin')                             content = (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 320, gap: 12, color: 'var(--text-3)' }}>
        <window.IcoShield size={32} style={{ opacity: 0.25 }}/>
        <div style={{ fontSize: 15, fontWeight: 500 }}>Доступ заборонено</div>
        <div style={{ fontSize: 13 }}>Ця сторінка доступна лише адміністраторам.</div>
      </div>
    );
    else content = <window.DashboardPage {...props}/>;

    return (
      <window.AppShell route={route} navigate={navigate} user={user}>
        {content}
      </window.AppShell>
    );
  };

  /* Tweaks panel options */
  const accentOptions = ['#3d8b6a', '#3b82f6', '#0ea5e9', '#6366f1', '#8b5cf6'];

  return (
    <window.ToastProvider>
      {renderPage()}

      {twPanel && (
        <window.TweaksPanel title="Tweaks · Прототип" onClose={() => {
          setTwPanel(false);
          window.parent.postMessage({ type: '__edit_mode_dismissed' }, '*');
        }}>
          <window.TweakSection title="Роль">
            <window.TweakRadio
              label="Тип акаунту"
              value={tweaks.role}
              options={[{ value: 'user', label: 'Юзер' }, { value: 'admin', label: 'Адмін' }]}
              onChange={v => setTweak('role', v)}
            />
          </window.TweakSection>

          <window.TweakSection title="Акцентний колір">
            <window.TweakColor
              label="Accent"
              value={tweaks.accent}
              options={accentOptions}
              onChange={v => setTweak('accent', v)}
            />
          </window.TweakSection>

          <window.TweakSection title="Демо-дані">
            <window.TweakToggle
              label="Показати порожні стани"
              value={tweaks.showEmpty}
              onChange={v => setTweak('showEmpty', v)}
            />
          </window.TweakSection>

          <window.TweakSection title="Навігація">
            <window.TweakSelect
              label="Перейти на сторінку"
              value={route}
              options={[
                { value: '/login',       label: 'Вхід'            },
                { value: '/dashboard',   label: 'Огляд'           },
                { value: '/upload',      label: 'Завантаження'    },
                { value: '/jobs',        label: 'Черга'           },
                { value: '/jobs/j001',   label: 'Деталі завдання' },
                { value: '/models',      label: 'Реєстр'          },
                { value: '/experiments', label: 'Досліди'         },
                { value: '/admin',       label: 'Адмін'           },
              ]}
              onChange={v => navigate(v)}
            />
          </window.TweakSection>
        </window.TweaksPanel>
      )}
    </window.ToastProvider>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
