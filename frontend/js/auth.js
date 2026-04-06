/* ═══════════════════════════════════════════════
   auth.js — JWT helpers + login/register logic
   Used by all pages for auth state management
═══════════════════════════════════════════════ */

const API = '';

/* ── Token helpers ────────────────────────────── */
const Auth = {
  getToken:   () => localStorage.getItem('token'),
  getUser:    () => JSON.parse(localStorage.getItem('user') || 'null'),
  isLoggedIn: () => !!localStorage.getItem('token'),
  isAdmin:    () => { const u = Auth.getUser(); return u && u.is_admin; },

  save(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
  },

  headers() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${Auth.getToken()}`
    };
  }
};

/* ── Theme (dark / light) ─────────────────────── */
const Theme = {
  KEY: 'ai-classifier-theme',

  get() {
    return localStorage.getItem(this.KEY) || 'dark';
  },

  set(mode) {
    localStorage.setItem(this.KEY, mode);
    this.apply(mode);
  },

  apply(mode) {
    document.body.classList.toggle('light-mode', mode === 'light');
    // Update all toggle buttons on the page
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.textContent = mode === 'light' ? '🌙' : '☀️';
      btn.title       = mode === 'light' ? 'Switch to dark mode' : 'Switch to light mode';
    });
  },

  toggle() {
    const next = this.get() === 'dark' ? 'light' : 'dark';
    this.set(next);
  },

  init() {
    // Apply saved preference immediately (before DOM paint if possible)
    this.apply(this.get());
  }
};

// Apply theme as early as possible
Theme.init();

/* ── API request helper ───────────────────────── */
async function apiRequest(method, endpoint, body = null, isFormData = false) {
  const token = Auth.getToken();

  const headers = {};

  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const opts = { method, headers };

  if (body) {
    opts.body = isFormData ? body : JSON.stringify(body);
  }

  const res  = await fetch(`${API}${endpoint}`, opts);
  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    Auth.logout();
    return;
  }

  if (!res.ok) {
    throw new Error(data.detail || `Request failed (${res.status})`);
  }

  return data;
}

/* ── Guard: redirect if not logged in ────────── */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

/* ── Guard: redirect if not admin ────────────── */
function requireAdmin() {
  if (!Auth.isAdmin()) {
    window.location.href = '/index.html';
    return false;
  }
  return true;
}

/* ── Populate nav user info ──────────────────── */
function initNav() {
  const user    = Auth.getUser();
  const navUser = document.getElementById('nav-user');
  if (!navUser) return;

  if (user) {
    navUser.innerHTML = `
      <button class="theme-toggle" onclick="Theme.toggle()" title="Toggle theme">
        ${Theme.get() === 'light' ? '🌙' : '☀️'}
      </button>
      <span>${user.full_name || user.email}</span>
      ${user.is_admin ? '<span class="badge badge-purple">Admin</span>' : ''}
      <button class="btn btn-ghost btn-sm" onclick="Auth.logout()">Sign out</button>
    `;
  } else {
    navUser.innerHTML = `
      <button class="theme-toggle" onclick="Theme.toggle()" title="Toggle theme">
        ${Theme.get() === 'light' ? '🌙' : '☀️'}
      </button>
      <a href="/login.html" class="btn btn-primary btn-sm">Sign in</a>
    `;
  }
}

/* ── Show alert helper ───────────────────────── */
function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId);
  if (!el) return;
  const icons = { error: '⚠️', success: '✅', info: 'ℹ️' };
  el.innerHTML = `<div class="alert alert-${type}">${icons[type]} ${message}</div>`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 5000);
}

/* ── Login page logic ────────────────────────── */
function initLoginPage() {
  // Apply theme toggle to login page navbar if present
  const navUser = document.getElementById('nav-user');
  if (navUser && !Auth.isLoggedIn()) {
    navUser.innerHTML = `
      <button class="theme-toggle" onclick="Theme.toggle()" title="Toggle theme">
        ${Theme.get() === 'light' ? '🌙' : '☀️'}
      </button>
    `;
  }

  // If already logged in, redirect
  if (Auth.isLoggedIn()) {
    window.location.href = '/index.html';
    return;
  }

  const loginForm    = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const showRegister = document.getElementById('show-register');
  const showLogin    = document.getElementById('show-login');

  // Toggle between login and register
  showRegister?.addEventListener('click', () => {
    document.getElementById('login-panel').classList.add('hidden');
    document.getElementById('register-panel').classList.remove('hidden');
  });

  showLogin?.addEventListener('click', () => {
    document.getElementById('register-panel').classList.add('hidden');
    document.getElementById('login-panel').classList.remove('hidden');
  });

  // Login submit
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn      = loginForm.querySelector('button[type=submit]');
    const email    = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Signing in...';

    try {
      const data     = await apiRequest('POST', '/auth/login', { email, password });
      const tempToken = data.access_token;
      localStorage.setItem('token', tempToken);
      const user = await apiRequest('GET', '/auth/me');
      Auth.save(tempToken, user);
      window.location.href = '/index.html';
    } catch (err) {
      showAlert('login-alert', err.message);
      btn.disabled = false;
      btn.innerHTML = 'Sign in';
    }
  });

  // Register submit
  registerForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn       = registerForm.querySelector('button[type=submit]');
    const full_name = document.getElementById('reg-name').value;
    const email     = document.getElementById('reg-email').value;
    const password  = document.getElementById('reg-password').value;

    if (password.length < 6) {
      showAlert('register-alert', 'Password must be at least 6 characters');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Creating account...';

    try {
      await apiRequest('POST', '/auth/register', { email, password, full_name });
      showAlert('register-alert', 'Account created! Please sign in.', 'success');
      setTimeout(() => {
        document.getElementById('register-panel').classList.add('hidden');
        document.getElementById('login-panel').classList.remove('hidden');
        document.getElementById('login-email').value = email;
      }, 1500);
    } catch (err) {
      showAlert('register-alert', err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Create account';
    }
  });
}