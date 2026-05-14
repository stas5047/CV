// Login + Register pages
const { useState } = React;

const AuthCard = ({ children }) => (
  <div style={{ background: 'var(--bg)', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
    <div className="auth-card">{children}</div>
  </div>
);

const AuthLogo = ({ subtitle }) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
    <div style={{
      width: 48, height: 48, borderRadius: 13, background: 'var(--accent)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: 17, color: '#fff',
    }}>AV</div>
    <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: 21, fontWeight: 700, letterSpacing: '-0.01em' }}>AeroVision</h1>
    {subtitle && <p style={{ color: 'var(--text-2)', fontSize: 13, textAlign: 'center', lineHeight: 1.4 }}>{subtitle}</p>}
  </div>
);

/* ─── Login ─── */
const LoginPage = ({ navigate, onLogin }) => {
  const [email, setEmail] = useState('');
  const [pw, setPw] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = (e) => {
    e.preventDefault();
    setError('');
    if (!email || !pw) { setError('Будь ласка, заповніть усі поля.'); return; }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      if (email === 'admin@aerovision.ua' && pw === 'admin123') {
        onLogin({ email, role: 'admin' });
      } else if (email.includes('@') && pw.length >= 8) {
        onLogin({ email, role: 'user' });
      } else if (email.includes('@') && pw.length > 0 && pw.length < 8) {
        setError('Пароль має містити щонайменше 8 символів.');
      } else {
        setError('Невірний email або пароль. Спробуйте ще раз.');
      }
    }, 850);
  };

  return (
    <AuthCard>
      <AuthLogo subtitle="Система комп'ютерного зору для аналізу медіафайлів"/>

      <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div className="form-field">
          <label className="form-label">Email</label>
          <input type="email" className="form-input" placeholder="email@example.com"
            value={email} onChange={e => setEmail(e.target.value)} autoFocus/>
        </div>
        <div className="form-field">
          <label className="form-label">Пароль</label>
          <input type="password" className="form-input" placeholder="••••••••"
            value={pw} onChange={e => setPw(e.target.value)}/>
        </div>

        {error && (
          <div className="error-banner" style={{ padding: '9px 12px' }}>
            <window.IcoAlertCircle size={14} style={{ flexShrink: 0, marginTop: 1 }}/>
            <span>{error}</span>
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={loading}
          style={{ width: '100%', justifyContent: 'center', padding: '10px', marginTop: 2 }}>
          {loading ? <><window.Spinner size={14}/> Вхід…</> : 'Увійти'}
        </button>
      </form>

      <div style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-3)' }}>
        Немає акаунту?{' '}
        <button onClick={() => navigate('/register')} style={{
          background: 'none', color: 'var(--accent-text)', border: 'none', cursor: 'pointer', fontSize: 12,
        }}>Зареєструватись</button>
      </div>

      <div style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '10px 12px', fontSize: 11, color: 'var(--text-3)', lineHeight: 1.6 }}>
        <strong style={{ color: 'var(--text-2)', display: 'block', marginBottom: 3 }}>Демо-доступ</strong>
        Адмін: admin@aerovision.ua / admin123<br/>
        Юзер: будь-який email + пароль ≥ 8 симв.

      </div>
    </AuthCard>
  );
};

/* ─── Register ─── */
const RegisterPage = ({ navigate }) => {
  const [fields, setFields] = useState({ email: '', pw: '', confirm: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const set = (k, v) => setFields(f => ({ ...f, [k]: v }));

  const validate = () => {
    const e = {};
    if (!fields.email) e.email = "Email є обов'язковим";
    else if (!/\S+@\S+\.\S+/.test(fields.email)) e.email = 'Введіть коректний email';
    if (!fields.pw) e.pw = "Пароль є обов'язковим";
    else if (fields.pw.length < 8) e.pw = 'Мінімум 8 символів';
    if (!fields.confirm) e.confirm = 'Підтвердіть пароль';
    else if (fields.pw !== fields.confirm) e.confirm = 'Паролі не збігаються';
    return e;
  };

  const submit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setLoading(true);
    setTimeout(() => { setLoading(false); navigate('/login'); }, 800);
  };

  const Field = ({ id, label, type, placeholder, hint }) => (
    <div className="form-field">
      <label className="form-label">{label}</label>
      <input type={type} className="form-input" placeholder={placeholder}
        value={fields[id]} onChange={e => set(id, e.target.value)}/>
      {errors[id] && <span style={{ fontSize: 11, color: 'var(--danger-text)' }}>{errors[id]}</span>}
      {hint && !errors[id] && <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{hint}</span>}
    </div>
  );

  return (
    <AuthCard>
      <AuthLogo subtitle="Створіть новий акаунт"/>

      <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <Field id="email"   label="Email"           type="email"    placeholder="email@example.com"/>
        <Field id="pw"      label="Пароль"          type="password" placeholder="Мінімум 8 символів" hint="Мінімальна довжина паролю — 8 символів"/>
        <Field id="confirm" label="Підтвердіть пароль" type="password" placeholder="Повторіть пароль"/>

        <button type="submit" className="btn btn-primary" disabled={loading}
          style={{ width: '100%', justifyContent: 'center', padding: '10px', marginTop: 2 }}>
          {loading ? <><window.Spinner size={14}/> Реєстрація…</> : 'Зареєструватись'}
        </button>
      </form>

      <div style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-3)' }}>
        Вже є акаунт?{' '}
        <button onClick={() => navigate('/login')} style={{
          background: 'none', color: 'var(--accent-text)', border: 'none', cursor: 'pointer', fontSize: 12,
        }}>Увійти</button>
      </div>
    </AuthCard>
  );
};

Object.assign(window, { LoginPage, RegisterPage });
