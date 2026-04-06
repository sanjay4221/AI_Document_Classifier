/* ═══════════════════════════════════════════════
   admin.js — Admin Dashboard Logic
═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  if (!requireAuth()) return;
  if (!requireAdmin()) return;
  initNav();
  loadStats();
  loadUsers();
  loadClassifications();
});

/* ── Load Stats ───────────────────────────────── */
async function loadStats() {
  try {
    const stats = await apiRequest('GET', '/admin/stats');

    document.getElementById('stat-users').textContent         = stats.total_users;
    document.getElementById('stat-documents').textContent     = stats.total_documents;
    document.getElementById('stat-classified').textContent    = stats.total_classified;
    document.getElementById('stat-avg-confidence').textContent = `${stats.avg_confidence}%`;

    renderDeptChart(stats.by_department || {});
    renderMethodChart(stats.by_method || {});
  } catch (err) {
    showAlert('admin-alert', 'Failed to load stats: ' + err.message);
  }
}

/* ── Department Chart ─────────────────────────── */
function renderDeptChart(byDept) {
  const container = document.getElementById('dept-chart');
  if (!container) return;

  const DEPT_COLORS = {
    'Finance': '#f59e0b', 'Human Resources': '#10b981',
    'Legal & Regulatory': '#8b5cf6', 'Licensing & Compliance': '#06b6d4',
    'IT & Technology': '#3b82f6', 'Operations': '#ec4899',
  };

  const max = Math.max(...Object.values(byDept), 1);
  container.innerHTML = Object.entries(byDept).map(([dept, count]) => `
    <div class="dept-bar-row">
      <div class="dept-bar-label">
        <span>${dept}</span>
        <span style="color:${DEPT_COLORS[dept]}">${count}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width:${(count/max*100).toFixed(0)}%;background:${DEPT_COLORS[dept]}"></div>
      </div>
    </div>`).join('') || '<p class="text-muted">No data yet</p>';
}

/* ── Method Chart ─────────────────────────────── */
function renderMethodChart(byMethod) {
  const container = document.getElementById('method-chart');
  if (!container) return;

  const colors = { llm: '#8b5cf6', ml: '#06b6d4', hybrid: '#10b981' };
  const total  = Object.values(byMethod).reduce((a,b) => a+b, 0) || 1;

  container.innerHTML = Object.entries(byMethod).map(([method, count]) => `
    <div class="method-stat">
      <div class="method-stat-bar" style="height:${(count/total*120).toFixed(0)}px;background:${colors[method]||'#8b5cf6'}"></div>
      <div class="method-stat-label">${method.toUpperCase()}</div>
      <div class="method-stat-count">${count}</div>
    </div>`).join('') || '<p class="text-muted">No data yet</p>';
}

/* ── Load Users ───────────────────────────────── */
async function loadUsers() {
  try {
    const users = await apiRequest('GET', '/admin/users');
    const tbody = document.getElementById('users-tbody');
    if (!tbody) return;

    tbody.innerHTML = users.map(u => `
      <tr>
        <td>${u.id}</td>
        <td>${u.full_name}</td>
        <td>${u.email}</td>
        <td>${u.is_admin ? '<span class="badge badge-purple">Admin</span>' : '<span class="badge">User</span>'}</td>
        <td>${u.is_active ? '<span class="badge badge-green">Active</span>' : '<span class="badge badge-red">Inactive</span>'}</td>
        <td>${new Date(u.created_at).toLocaleDateString()}</td>
        <td>
          ${!u.is_admin ? `<button class="btn btn-secondary btn-sm" onclick="makeAdmin(${u.id})">Make Admin</button>` : '—'}
        </td>
      </tr>`).join('');
  } catch (err) {
    console.error('Failed to load users:', err);
  }
}

/* ── Make Admin ───────────────────────────────── */
async function makeAdmin(userId) {
  if (!confirm('Make this user an admin?')) return;
  try {
    await apiRequest('POST', `/admin/users/${userId}/make-admin`);
    showAlert('admin-alert', 'User is now admin', 'success');
    loadUsers();
  } catch (err) {
    showAlert('admin-alert', err.message);
  }
}

/* ── Load Classifications ─────────────────────── */
async function loadClassifications() {
  try {
    const results = await apiRequest('GET', '/admin/classifications');
    const tbody   = document.getElementById('class-tbody');
    if (!tbody) return;

    const DEPT_COLORS = {
      'Finance': '#f59e0b', 'Human Resources': '#10b981',
      'Legal & Regulatory': '#8b5cf6', 'Licensing & Compliance': '#06b6d4',
      'IT & Technology': '#3b82f6', 'Operations': '#ec4899',
    };

    tbody.innerHTML = results.slice(0, 50).map(r => {
      const color = DEPT_COLORS[r.department] || '#8b5cf6';
      const methodColors = { llm: 'badge-purple', ml: 'badge-cyan', hybrid: 'badge-green' };
      return `
        <tr>
          <td>${r.id}</td>
          <td>${r.document_id}</td>
          <td><span style="color:${color};font-weight:500">${r.department}</span></td>
          <td>${(r.confidence_score * 100).toFixed(1)}%</td>
          <td><span class="badge ${methodColors[r.method_used]||'badge-purple'}">${r.method_used}</span></td>
          <td>${new Date(r.created_at).toLocaleString()}</td>
        </tr>`;
    }).join('');
  } catch (err) {
    console.error('Failed to load classifications:', err);
  }
}

/* ── Tab switching ────────────────────────────── */
function switchTab(tabName) {
  document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
  document.getElementById(`tab-${tabName}`)?.classList.remove('hidden');
}
