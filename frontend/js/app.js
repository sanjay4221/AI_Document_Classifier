/* ═══════════════════════════════════════════════
   app.js — Main Upload + Classification Logic
═══════════════════════════════════════════════ */

const DEPT_COLORS = {
  'Finance':                '#f59e0b',
  'Human Resources':        '#10b981',
  'Legal & Regulatory':     '#8b5cf6',
  'Licensing & Compliance': '#06b6d4',
  'IT & Technology':        '#3b82f6',
  'Operations':             '#ec4899',
};

const DEPT_ICONS = {
  'Finance':                '💰',
  'Human Resources':        '👥',
  'Legal & Regulatory':     '⚖️',
  'Licensing & Compliance': '📋',
  'IT & Technology':        '💻',
  'Operations':             '⚙️',
};

// ── Confidence thresholds ──────────────────────
const CONFIDENCE = {
  HIGH:   80,
  MEDIUM: 65,
  LOW:    0,
};

let documents        = [];
let activeDeptFilter = 'all';   // current dept filter
let activeResult     = null;    // last shown result (for download)

/* ── Init ─────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (!requireAuth()) return;
  initNav();
  initUploadZone();
  initDeptFilter();
  loadDocuments();
});

/* ── Confidence helpers ───────────────────────── */
function getConfidenceLevel(score) {
  const pct = score > 1 ? score : score * 100;
  if (pct >= CONFIDENCE.HIGH)   return 'high';
  if (pct >= CONFIDENCE.MEDIUM) return 'medium';
  return 'low';
}

function getConfidenceMeta(score) {
  const level = getConfidenceLevel(score);
  return {
    high:   { color: 'var(--emerald)', icon: '✅', label: 'High confidence',  badge: 'badge-green' },
    medium: { color: 'var(--amber)',   icon: '⚠️', label: 'Review suggested', badge: 'badge-amber' },
    low:    { color: 'var(--red)',     icon: '🔴', label: 'Low confidence',    badge: 'badge-red'   },
  }[level];
}

function getWarningBanner(score, department) {
  const level = getConfidenceLevel(score);
  if (level === 'high') return '';
  if (level === 'medium') {
    return `
      <div class="confidence-warning warning-medium">
        <span class="warning-icon">⚠️</span>
        <div>
          <strong>Review suggested</strong> — The AI is moderately confident this is a
          <strong>${department}</strong> document. Please verify before routing.
        </div>
      </div>`;
  }
  return `
    <div class="confidence-warning warning-low">
      <span class="warning-icon">🔴</span>
      <div>
        <strong>Low confidence — manual review required.</strong>
        The AI struggled to classify this document clearly.
        It may contain content from multiple departments, be a scanned image,
        or fall outside the trained categories.
        <br/><span class="warning-hint">💡 Tip: Check the department scores below to see alternatives.</span>
      </div>
    </div>`;
}

/* ── Department Filter Pills ──────────────────── */
function initDeptFilter() {
  const container = document.getElementById('dept-filter');
  if (!container) return;

  const allDepts = Object.keys(DEPT_COLORS);

  container.innerHTML = `
    <button class="dept-pill active" data-dept="all" onclick="setDeptFilter('all')">
      🗂️ All
    </button>
    ${allDepts.map(dept => `
      <button class="dept-pill" data-dept="${dept}" onclick="setDeptFilter('${dept}')"
              style="--pill-color:${DEPT_COLORS[dept]}">
        <span class="dept-pill-dot" style="background:${DEPT_COLORS[dept]}"></span>
        ${dept}
      </button>
    `).join('')}
  `;
}

function setDeptFilter(dept) {
  activeDeptFilter = dept;

  // Update pill active state
  document.querySelectorAll('.dept-pill').forEach(p => {
    const isActive = p.dataset.dept === dept;
    p.classList.toggle('active', isActive);
    if (isActive && dept !== 'all') {
      p.style.background    = DEPT_COLORS[dept];
      p.style.borderColor   = DEPT_COLORS[dept];
    } else if (isActive) {
      p.style.background  = 'var(--grad-primary)';
      p.style.borderColor = 'transparent';
    } else {
      p.style.background  = '';
      p.style.borderColor = '';
    }
  });

  renderDocumentList();
}

/* ── Upload Zone ──────────────────────────────── */
function initUploadZone() {
  const zone  = document.getElementById('upload-zone');
  const input = document.getElementById('file-input');
  const btn   = document.getElementById('upload-btn');

  zone?.addEventListener('click', () => input?.click());
  btn?.addEventListener('click', (e) => { e.stopPropagation(); input?.click(); });

  zone?.addEventListener('dragover',  (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone?.addEventListener('dragleave', ()  => zone.classList.remove('drag-over'));
  zone?.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
    if (files.length) uploadFiles(files);
    else showAlert('main-alert', 'Only PDF files are supported', 'error');
  });

  input?.addEventListener('change', () => {
    if (input.files.length) uploadFiles(Array.from(input.files));
    input.value = '';
  });
}

/* ── Upload Files (improved bulk progress) ────── */
async function uploadFiles(files) {
  const progressSection = document.getElementById('upload-progress');
  const progressList    = document.getElementById('progress-list');
  progressSection?.classList.remove('hidden');

  // Clear previous progress items
  progressList.innerHTML = '';

  // Bulk summary bar for multiple files
  if (files.length > 1) {
    progressList.innerHTML = `
      <div class="bulk-summary" id="bulk-summary">
        Processing <strong>0 / ${files.length}</strong> files…
      </div>`;
  }

  let doneCount  = 0;
  let errorCount = 0;

  for (const file of files) {
    if (file.size > 10 * 1024 * 1024) {
      showAlert('main-alert', `${file.name} exceeds 10MB limit`, 'error');
      errorCount++;
      continue;
    }

    const itemId   = `prog-${Date.now()}-${Math.random().toString(36).slice(2,6)}`;
    const shortName = file.name.length > 40 ? file.name.slice(0, 38) + '…' : file.name;

    // Each file gets 3 step indicators: Upload → Classify → Done
    progressList.innerHTML += `
      <div class="progress-item" id="${itemId}">
        <div class="progress-item-info">
          <span class="progress-item-name">📄 ${shortName}</span>
          <span class="progress-item-status" id="${itemId}-status">Uploading…</span>
        </div>
        <div class="progress-item-step">
          <div class="progress-step step-active" id="${itemId}-s1" title="Upload"></div>
          <div class="progress-step"             id="${itemId}-s2" title="Classify"></div>
          <div class="progress-step"             id="${itemId}-s3" title="Complete"></div>
        </div>
      </div>`;

    try {
      // ── Step 1: Upload
      const formData = new FormData();
      formData.append('file', file);
      const uploaded = await apiRequest('POST', '/documents/upload', formData, true);

      document.getElementById(`${itemId}-s1`).className = 'progress-step step-done';
      document.getElementById(`${itemId}-s2`).className = 'progress-step step-active';
      document.getElementById(`${itemId}-status`).textContent = 'Classifying…';

      // ── Step 2: Classify
      const result = await apiRequest('POST', `/classify/${uploaded.document_id}`);
      const score  = result.confidence_score > 1 ? result.confidence_score : result.confidence_score * 100;
      const meta   = getConfidenceMeta(score);

      document.getElementById(`${itemId}-s2`).className = 'progress-step step-done';
      document.getElementById(`${itemId}-s3`).className = 'progress-step step-done';
      document.getElementById(`${itemId}-status`).innerHTML =
        `<span style="color:${meta.color}">${meta.icon} ${result.department} (${score.toFixed(1)}%)</span>`;
      document.getElementById(itemId).classList.add('progress-done');

      doneCount++;
      await loadDocuments();

      // Auto-show last result
      if (files.length === 1) setTimeout(() => showResult(result), 300);

    } catch (err) {
      document.getElementById(`${itemId}-s1`).className = 'progress-step step-error';
      document.getElementById(`${itemId}-s2`).className = 'progress-step step-error';
      document.getElementById(`${itemId}-s3`).className = 'progress-step step-error';
      document.getElementById(`${itemId}-status`).innerHTML =
        `<span style="color:var(--red)">✗ ${err.message}</span>`;
      document.getElementById(itemId).classList.add('progress-error');
      errorCount++;
    }

    // Update bulk summary
    const summary = document.getElementById('bulk-summary');
    if (summary) {
      const done  = doneCount + errorCount;
      const total = files.length;
      summary.innerHTML = done < total
        ? `Processing <strong>${done} / ${total}</strong> files…`
        : errorCount > 0
          ? `✅ ${doneCount} classified &nbsp;·&nbsp; ❌ ${errorCount} failed`
          : `✅ All <strong>${doneCount}</strong> files classified`;
    }
  }

  setTimeout(() => progressSection?.classList.add('hidden'), 6000);
}

/* ── Load Documents ───────────────────────────── */
async function loadDocuments() {
  try {
    documents = await apiRequest('GET', '/documents/');
    renderDocumentList();
    renderStats();
  } catch (err) {
    console.error('Failed to load documents:', err);
  }
}

/* ── Render Document List ─────────────────────── */
function renderDocumentList() {
  const list  = document.getElementById('doc-list');
  const empty = document.getElementById('doc-empty');
  if (!list) return;

  // Apply department filter
  const filtered = activeDeptFilter === 'all'
    ? documents
    : documents.filter(d => d.classification?.department === activeDeptFilter);

  if (!filtered.length) {
    list.classList.add('hidden');
    empty?.classList.remove('hidden');
    if (activeDeptFilter !== 'all') {
      empty.innerHTML = `
        <span class="empty-icon">🔍</span>
        <p>No <strong style="color:${DEPT_COLORS[activeDeptFilter]}">${activeDeptFilter}</strong> documents yet.</p>`;
    } else {
      empty.innerHTML = `
        <span class="empty-icon">📭</span>
        <p>No documents yet. Upload your first PDF above!</p>`;
    }
    return;
  }

  empty?.classList.add('hidden');
  list.classList.remove('hidden');

  list.innerHTML = filtered.map(doc => {
    const c     = doc.classification;
    const color = c ? DEPT_COLORS[c.department] || '#8b5cf6' : '#6b6880';
    const icon  = c ? DEPT_ICONS[c.department]  || '📁'      : '⏳';

    let confIndicator = '';
    if (c) {
      const score = c.confidence_score > 1 ? c.confidence_score * 100 : c.confidence_score;
      const meta  = getConfidenceMeta(score);
      confIndicator = `<span class="badge ${meta.badge}" title="${meta.label}">${meta.icon} ${score.toFixed(0)}%</span>`;
    }

    const statusBadge = doc.status === 'classified'
      ? confIndicator
      : doc.status === 'failed'
      ? `<span class="badge badge-red">✗ Failed</span>`
      : `<span class="badge badge-amber">⏳ Pending</span>`;

    return `
      <div class="doc-card animate-up" onclick="fetchAndShowResult(${doc.id})"
           style="--dept-accent:${color}">
        <div class="doc-card-icon">${icon}</div>
        <div class="doc-card-body">
          <div class="doc-card-name">${doc.filename}</div>
          <div class="doc-card-meta">
            ${c
              ? `<span style="color:${color};font-weight:500">${c.department}</span>
                 <span class="doc-card-method">${c.method_used?.toUpperCase()}</span>`
              : '<span>Not classified</span>'
            }
          </div>
        </div>
        <div class="doc-card-right">
          ${statusBadge}
          <button
            class="btn-delete-doc"
            title="Delete document"
            onclick="deleteDocument(event, ${doc.id})">🗑️</button>
        </div>
      </div>`;
  }).join('');
}

/* ── Render Stats ─────────────────────────────── */
function renderStats() {
  const total       = documents.length;
  const classified  = documents.filter(d => d.status === 'classified').length;
  const pending     = documents.filter(d => d.status === 'pending').length;
  const needsReview = documents.filter(d => {
    if (!d.classification) return false;
    const s   = d.classification.confidence_score;
    const pct = s > 1 ? s * 100 : s;
    return pct < CONFIDENCE.HIGH;
  }).length;

  setText('stat-total',      total);
  setText('stat-classified', classified);
  setText('stat-pending',    pending);
  setText('stat-review',     needsReview);

  const reviewChip = document.getElementById('stat-review')?.closest('.stat-chip');
  if (reviewChip) {
    reviewChip.style.borderColor = needsReview > 0
      ? 'rgba(245,158,11,0.4)'
      : 'var(--border)';
  }
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ── Fetch and Show Result ────────────────────── */
async function fetchAndShowResult(docId) {
  try {
    const result = await apiRequest('GET', `/classify/${docId}/result`);
    showResult(result);
  } catch (err) {
    showAlert('main-alert', 'No classification result yet.', 'info');
  }
}

/* ── Show Result Panel ────────────────────────── */
function showResult(result) {
  const panel = document.getElementById('result-panel');
  if (!panel) return;

  activeResult = result;  // store for download

  const color   = DEPT_COLORS[result.department] || '#8b5cf6';
  const icon    = DEPT_ICONS[result.department]  || '📁';
  const score   = result.confidence_score > 1
    ? result.confidence_score
    : result.confidence_score * 100;
  const pct     = score.toFixed(1);
  const meta    = getConfidenceMeta(score);
  const warning = getWarningBanner(score, result.department);

  const methodColors = { llm: 'badge-purple', ml: 'badge-cyan', hybrid: 'badge-green' };
  const methodBadge  = `<span class="badge ${methodColors[result.method_used] || 'badge-purple'}">${result.method_used?.toUpperCase()}</span>`;

  panel.innerHTML = `
    <div class="result-card animate-up">

      ${warning}

      <div class="result-header" style="--dept-color:${color}">
        <div class="result-dept-icon">${icon}</div>
        <div style="flex:1">
          <div class="result-label">Classified as</div>
          <div class="result-dept" style="color:${color}">${result.department}</div>
          <div style="margin-top:4px">
            <span class="badge ${meta.badge}">${meta.icon} ${meta.label}</span>
          </div>
        </div>
        <div class="result-score-ring" style="--score-color:${color}">
          <svg viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="15.9" fill="none"
              stroke="rgba(255,255,255,0.06)" stroke-width="2.5"/>
            <circle cx="18" cy="18" r="15.9" fill="none"
              stroke="${meta.color}" stroke-width="2.5"
              stroke-dasharray="${pct}, 100" stroke-linecap="round"
              transform="rotate(-90 18 18)"
              style="transition:stroke-dasharray 1s ease"/>
          </svg>
          <span style="color:${meta.color}">${pct}%</span>
        </div>
      </div>

      <div class="result-meta">
        <span class="text-muted">📄 ${result.filename}</span>
        ${methodBadge}
        ${result.classified_at
          ? `<span class="text-muted">${new Date(result.classified_at).toLocaleString()}</span>`
          : ''}
        <button
          class="btn btn-ghost btn-sm"
          style="margin-left:auto"
          onclick="reclassifyDocument(${result.document_id})"
          title="Run classification again">
          🔄 Reclassify
        </button>
      </div>

      <div class="result-explanation">
        <div class="result-section-label">💡 Why this classification?</div>
        <p>${result.explanation}</p>
      </div>

      <div class="result-chart-section">
        <div class="result-section-label">📊 All Department Scores</div>
        <div id="dept-bars"></div>
      </div>

      <!-- ── Download Row ── -->
      <div class="download-row">
        <button class="btn-download btn-download-csv" onclick="downloadCSV()" title="Download as CSV">
          📥 Download CSV
        </button>
        <button class="btn-download btn-download-pdf" onclick="downloadPDF()" title="Download as PDF report">
          📄 Download PDF
        </button>
      </div>

    </div>`;

  renderDeptBars(result);
  panel.classList.remove('hidden');
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ── Department Bar Chart ─────────────────────── */
function renderDeptBars(result) {
  const container = document.getElementById('dept-bars');
  if (!container) return;

  const mlScores    = result.ml_result?.all_scores || {};
  const winnerScore = result.confidence_score > 1
    ? result.confidence_score / 100
    : result.confidence_score;

  const allDepts = Object.keys(DEPT_COLORS);
  const scores   = {};
  allDepts.forEach(d => {
    scores[d] = mlScores[d] || (d === result.department ? winnerScore : 0);
  });

  const sorted = allDepts.sort((a, b) => scores[b] - scores[a]);

  container.innerHTML = sorted.map(dept => {
    const pct      = (scores[dept] * 100).toFixed(1);
    const color    = DEPT_COLORS[dept];
    const isWinner = dept === result.department;
    const barMeta  = getConfidenceMeta(parseFloat(pct));

    return `
      <div class="dept-bar-row ${isWinner ? 'dept-bar-winner' : ''}">
        <div class="dept-bar-label">
          <span>${DEPT_ICONS[dept]} ${dept}
            ${isWinner ? `<span class="badge ${barMeta.badge}" style="margin-left:6px;font-size:0.7rem">${barMeta.icon} ${barMeta.label}</span>` : ''}
          </span>
          <span style="color:${color};font-weight:${isWinner ? '600' : '400'}">${pct}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill"
               style="width:${pct}%;background:${color};opacity:${isWinner ? 1 : 0.4}">
          </div>
        </div>
      </div>`;
  }).join('');
}

/* ── Download CSV ─────────────────────────────── */
function downloadCSV() {
  if (!activeResult) return;
  const r = activeResult;

  const score = r.confidence_score > 1 ? r.confidence_score : r.confidence_score * 100;

  const rows = [
    ['Field', 'Value'],
    ['Filename',         r.filename],
    ['Department',       r.department],
    ['Confidence',       `${score.toFixed(1)}%`],
    ['Method',           r.method_used?.toUpperCase() || ''],
    ['Confidence Level', getConfidenceLevel(score).toUpperCase()],
    ['Explanation',      `"${(r.explanation || '').replace(/"/g, '""')}"`],
    ['Classified At',    r.classified_at ? new Date(r.classified_at).toLocaleString() : ''],
    [],
    ['Department', 'Score'],
    ...Object.keys(DEPT_COLORS).map(dept => {
      const mlScores    = r.ml_result?.all_scores || {};
      const winnerScore = r.confidence_score > 1 ? r.confidence_score / 100 : r.confidence_score;
      const s = mlScores[dept] || (dept === r.department ? winnerScore : 0);
      return [dept, `${(s * 100).toFixed(1)}%`];
    }),
  ];

  const csv  = rows.map(row => row.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  const name = (r.filename || 'result').replace(/\.pdf$/i, '');

  a.href     = url;
  a.download = `${name}_classification.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/* ── Download PDF (HTML → print) ─────────────── */
function downloadPDF() {
  if (!activeResult) return;
  const r = activeResult;

  const score      = r.confidence_score > 1 ? r.confidence_score : r.confidence_score * 100;
  const meta       = getConfidenceMeta(score);
  const color      = DEPT_COLORS[r.department] || '#8b5cf6';
  const icon       = DEPT_ICONS[r.department]  || '📁';
  const mlScores   = r.ml_result?.all_scores || {};
  const winnerScore = r.confidence_score > 1 ? r.confidence_score / 100 : r.confidence_score;

  // Build raw scores for all depts
  const allDeptScores = {};
  Object.keys(DEPT_COLORS).forEach(dept => {
    allDeptScores[dept] = mlScores[dept] || (dept === r.department ? winnerScore : 0);
  });

  // Normalise bar widths so they always render visually
  // If only winner has a score, show winner at 100% bar width and others at 0%
  // If multiple scores exist, normalise relative to max
  const maxScore = Math.max(...Object.values(allDeptScores));

  const deptRows = Object.keys(DEPT_COLORS)
    .sort((a, b) => allDeptScores[b] - allDeptScores[a])
    .map(dept => {
      const s       = allDeptScores[dept];
      const pct     = (s * 100).toFixed(1);
      const barPct  = maxScore > 0 ? ((s / maxScore) * 100).toFixed(1) : 0;
      const isWin   = dept === r.department;
      return `<tr style="${isWin ? `font-weight:600;color:${color}` : ''}">
        <td>${DEPT_ICONS[dept]} ${dept}</td>
        <td>${pct}%</td>
        <td style="width:200px">
          <div style="height:8px;background:#eee;border-radius:4px;overflow:hidden">
            <div style="height:100%;width:${barPct}%;background:${DEPT_COLORS[dept]};border-radius:4px;opacity:${isWin ? 1 : 0.55}"></div>
          </div>
        </td>
      </tr>`;
    }).join('');

  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Classification Report — ${r.filename}</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a1333; padding: 40px; max-width: 700px; margin: 0 auto; }
    h1   { font-size: 1.6rem; color: ${color}; margin-bottom: 4px; }
    .sub { color: #888; font-size: 0.9rem; margin-bottom: 24px; }
    .badge { display:inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th    { text-align: left; padding: 8px 12px; background: #f5f4ff; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; }
    td    { padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 0.88rem; }
    .section { margin-top: 28px; }
    .section-title { font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin-bottom: 10px; }
    .explanation { background: #f9f8ff; border-left: 3px solid ${color}; padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 0.9rem; line-height: 1.7; }
    .meta-row { display: flex; gap: 20px; flex-wrap: wrap; margin: 16px 0; }
    .meta-item { font-size: 0.85rem; }
    .meta-label { color: #888; display: block; font-size: 0.75rem; }
    @media print { body { padding: 20px; } }
  </style>
</head>
<body>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
    <span style="font-size:2.5rem">${icon}</span>
    <div>
      <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em">Classified as</div>
      <h1>${r.department}</h1>
    </div>
    <span class="badge" style="margin-left:auto;background:${color}22;color:${color};border:1px solid ${color}44">
      ${meta.icon} ${score.toFixed(1)}% — ${meta.label}
    </span>
  </div>

  <div class="sub">📄 ${r.filename}</div>

  <div class="meta-row">
    <div class="meta-item">
      <span class="meta-label">Method</span>
      ${r.method_used?.toUpperCase()}
    </div>
    <div class="meta-item">
      <span class="meta-label">Classified at</span>
      ${r.classified_at ? new Date(r.classified_at).toLocaleString() : 'N/A'}
    </div>
    <div class="meta-item">
      <span class="meta-label">Generated</span>
      ${new Date().toLocaleString()}
    </div>
  </div>

  <div class="section">
    <div class="section-title">💡 Why this classification?</div>
    <div class="explanation">${r.explanation || 'No explanation available.'}</div>
  </div>

  <div class="section">
    <div class="section-title">📊 All Department Scores</div>
    <table>
      <thead><tr><th>Department</th><th>Score</th><th>Bar</th></tr></thead>
      <tbody>${deptRows}</tbody>
    </table>
  </div>

  <div style="margin-top:40px;font-size:0.75rem;color:#aaa;border-top:1px solid #eee;padding-top:12px">
    Generated by AI Document Classifier · ${new Date().toLocaleDateString()}
  </div>

  <script>window.onload = () => { window.print(); }<\/script>
</body>
</html>`;

  const blob = new Blob([html], { type: 'text/html' });
  const url  = URL.createObjectURL(blob);
  const win  = window.open(url, '_blank');
  if (!win) {
    // Fallback: direct download if popup blocked
    const a    = document.createElement('a');
    const name = (r.filename || 'result').replace(/\.pdf$/i, '');
    a.href     = url;
    a.download = `${name}_classification.html`;
    a.click();
  }
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}

/* ── Delete Document ──────────────────────────── */
async function deleteDocument(event, docId) {
  event.stopPropagation(); // prevent card click opening result

  try {
    await apiRequest('DELETE', `/documents/${docId}`);

    // Fade card out instantly
    const card = event.target.closest('.doc-card');
    if (card) {
      card.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
      card.style.opacity    = '0';
      card.style.transform  = 'translateX(10px)';
      setTimeout(() => card.remove(), 200);
    }

    // Clear result panel if it was showing this doc
    const panel = document.getElementById('result-panel');
    if (panel?.innerHTML.includes(`reclassifyDocument(${docId})`)) {
      panel.innerHTML = `
        <div class="card result-empty">
          <span class="empty-icon">🗑️</span>
          <p class="text-muted">Document deleted.</p>
        </div>`;
      activeResult = null;
    }

    await loadDocuments();

  } catch (err) {
    showAlert('main-alert', `Delete failed: ${err.message}`, 'error');
  }
}

/* ── Reclassify Document ──────────────────────── */
async function reclassifyDocument(docId) {
  const btn = document.querySelector(`[onclick="reclassifyDocument(${docId})"]`);

  if (btn) {
    btn.disabled  = true;
    btn.innerHTML = '<span class="spinner"></span> Classifying...';
  }

  const deptEl = document.querySelector('.result-dept');
  if (deptEl) deptEl.innerHTML = '<span class="spinner"></span> Reclassifying...';

  try {
    const result = await apiRequest('POST', `/documents/${docId}/reclassify`);
    showResult(result);
    await loadDocuments();
    showAlert('main-alert', `✅ Reclassified as ${result.department} (${result.confidence_score}%)`, 'success');
  } catch (err) {
    showAlert('main-alert', `Reclassify failed: ${err.message}`, 'error');
    if (btn) {
      btn.disabled  = false;
      btn.innerHTML = '🔄 Reclassify';
    }
  }
}

/* ── Filter documents (text search) ──────────── */
function filterDocs(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.doc-card').forEach(card => {
    const name = card.querySelector('.doc-card-name')?.textContent.toLowerCase() || '';
    const dept = card.querySelector('.doc-card-meta span')?.textContent.toLowerCase() || '';
    card.style.display = name.includes(q) || dept.includes(q) ? '' : 'none';
  });
}