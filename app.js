// You can override API_BASE by setting window.API_BASE before this script runs
// e.g., in HTML: <script>window.API_BASE = 'http://127.0.0.1:8000';</script>
const API_BASE = window.API_BASE || '';

function api(path) {
  if (!API_BASE) return path; // same-origin
  return API_BASE.replace(/\/$/, '') + path;
}

async function login(event) {
  event.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const statusEl = document.getElementById('status');
  statusEl.className = 'status';
  statusEl.textContent = 'Signing in...';
  try {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);
    const res = await fetch(api('/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString()
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(t || 'Login failed');
    }
    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);
    statusEl.className = 'status ok';
    statusEl.textContent = 'Logged in';
    updateAuthState();
  } catch (err) {
    statusEl.className = 'status err';
    statusEl.textContent = err.message || String(err);
  }
}

function getToken() { return localStorage.getItem('access_token') || ''; }

async function whoAmI() {
  const out = document.getElementById('output');
  out.textContent = 'Loading /me ...';
  try {
    const res = await fetch(api('/me'), {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    const text = await res.text();
    out.textContent = text;
  } catch (e) {
    out.textContent = String(e);
  }
}

async function logout() {
  const statusEl = document.getElementById('status');
  statusEl.className = 'status';
  statusEl.textContent = 'Logging out...';
  try {
    const res = await fetch(api('/logout'), {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    // Regardless of server response, clear local token
    localStorage.removeItem('access_token');
    if (!res.ok) {
      const t = await res.text();
      throw new Error(t || 'Logout failed');
    }
    statusEl.className = 'status ok';
    statusEl.textContent = 'Logged out';
  } catch (e) {
    statusEl.className = 'status err';
    statusEl.textContent = e.message || String(e);
  } finally {
    updateAuthState();
  }
}

function updateAuthState() {
  const token = getToken();
  const authed = !!token;
  document.getElementById('authed').style.display = authed ? 'block' : 'none';
  document.getElementById('login-form').style.display = authed ? 'none' : 'block';
  const tokenEl = document.getElementById('token');
  tokenEl.textContent = token ? token.slice(0, 8) + '…' + token.slice(-6) : '(none)';
}

window.addEventListener('DOMContentLoaded', updateAuthState);