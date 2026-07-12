import { useMemo, useState } from 'react';

const DEFAULT_API = '';

function App() {
  const [apiBase, setApiBase] = useState(DEFAULT_API);
  const [token, setToken] = useState('');
  const [status, setStatus] = useState('');
  const [registerForm, setRegisterForm] = useState({
    email: 'admin@booking.com',
    password: 'secret123',
    full_name: 'Demo Admin',
    role_name: 'admin',
  });
  const [loginForm, setLoginForm] = useState({
    username: 'admin@booking.com',
    password: 'secret123',
  });
  const [venues, setVenues] = useState([]);
  const [events, setEvents] = useState([]);

  const apiUrl = useMemo(() => apiBase.replace(/\/$/, ''), [apiBase]);

  async function registerUser() {
    const response = await fetch(`${apiUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerForm),
    });
    const payload = await response.json();
    setStatus(`Register: ${response.status} ${JSON.stringify(payload)}`);
  }

  async function loginUser() {
    const formData = new URLSearchParams();
    formData.append('username', loginForm.username);
    formData.append('password', loginForm.password);

    const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    const payload = await response.json();
    setToken(payload.access_token ?? '');
    setStatus(`Login: ${response.status} ${JSON.stringify(payload)}`);
  }

  async function fetchVenues() {
    const response = await fetch(`${apiUrl}/api/v1/venues`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const payload = await response.json();
    setVenues(payload);
    setStatus(`Venues: ${response.status} ${JSON.stringify(payload)}`);
  }

  async function fetchEvents() {
    const response = await fetch(`${apiUrl}/api/v1/events`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const payload = await response.json();
    setEvents(payload);
    setStatus(`Events: ${response.status} ${JSON.stringify(payload)}`);
  }

  async function healthCheck() {
    const response = await fetch(`${apiUrl}/health`);
    const payload = await response.json();
    setStatus(`Health: ${response.status} ${JSON.stringify(payload)}`);
  }

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Full-stack portfolio project</p>
          <h1>Ticket Booking System</h1>
          <p className="hero-copy">
            A modular FastAPI backend with a React frontend, PostgreSQL persistence, and
            Redis-backed seat hold behavior.
          </p>
        </div>
        <div className="status-box">
          <strong>API Base</strong>
          <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
        </div>
      </header>

      <main className="grid-layout">
        <section className="panel">
          <h2>Register</h2>
          <div className="stack">
            <input value={registerForm.email} onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })} placeholder="Email" />
            <input value={registerForm.full_name} onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })} placeholder="Full name" />
            <input value={registerForm.password} onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })} placeholder="Password" />
            <select value={registerForm.role_name} onChange={(e) => setRegisterForm({ ...registerForm, role_name: e.target.value })}>
              <option value="admin">admin</option>
              <option value="organizer">organizer</option>
              <option value="customer">customer</option>
            </select>
            <button onClick={registerUser}>Register</button>
          </div>
        </section>

        <section className="panel">
          <h2>Login</h2>
          <div className="stack">
            <input value={loginForm.username} onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })} placeholder="Email" />
            <input value={loginForm.password} onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} placeholder="Password" />
            <button onClick={loginUser}>Login</button>
            <code className="token-box">{token || 'No token yet'}</code>
          </div>
        </section>

        <section className="panel wide">
          <h2>Runtime checks</h2>
          <div className="button-row">
            <button onClick={healthCheck}>Health</button>
            <button onClick={fetchVenues}>Fetch venues</button>
            <button onClick={fetchEvents}>Fetch events</button>
          </div>
          <pre>{status || 'Run a check to view JSON responses.'}</pre>
        </section>

        <section className="panel">
          <h2>Venues</h2>
          <pre>{JSON.stringify(venues, null, 2)}</pre>
        </section>

        <section className="panel">
          <h2>Events</h2>
          <pre>{JSON.stringify(events, null, 2)}</pre>
        </section>
      </main>
    </div>
  );
}

export default App;
