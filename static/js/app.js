/**
 * Mognadsdialog – SPA (Phase 3: MCF structured assessment)
 *
 * New dialogue flow:
 *  1. Show subprocess diagram for each perspective
 *  2. For each dimension, show 4 level descriptions — user selects best match
 *  3. Dimension selections suggest an overall level (lowest/conservative)
 *  4. Group can override and add reasoning
 *  5. Guidance shown for reaching next level
 */

const API = '/api';
let refData = null;
let appSettings = {};
let currentUser = null; // { id, username, display_name, role } or null

function isAdmin() { return currentUser && currentUser.role === 'admin'; }

async function api(path, opts = {}) {
    const res = await fetch(API + path, {
        headers: { 'Content-Type': 'application/json', ...opts.headers },
        ...opts,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'API error');
    }
    return res.json();
}

const routes = {};
function navigate(view, params = {}) {
    const fn = routes[view];
    if (!fn) return console.error('Unknown view:', view);
    document.getElementById('app').innerHTML = '';
    window.scrollTo(0, 0);
    fn(params);
}

function applyTheme(s) {
    const r = document.documentElement.style;
    r.setProperty('--primary', s.primary || '#E27629');
    r.setProperty('--primary-light', s.primary_light || '#F09A5B');
    r.setProperty('--accent', s.accent || '#2E7D32');
    r.setProperty('--text', s.text || '#2c3e50');
    r.setProperty('--text-light', s.text_light || '#7f8c8d');
    r.setProperty('--bg', s.bg || '#f5f7fa');
    // Header title
    const h1 = document.querySelector('.app-header h1');
    if (h1) h1.textContent = s.app_title || 'Mognadsdialog';
    // Logo
    const logoEl = document.getElementById('header-logo');
    if (logoEl) {
        if (s.logo_url) { logoEl.src = s.logo_url; logoEl.style.display = 'block'; }
        else { logoEl.style.display = 'none'; }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    appSettings = await api('/settings');
    applyTheme(appSettings);
    // Check if already logged in
    const me = await api('/auth/me');
    if (me.authenticated) {
        currentUser = me.user;
        await bootApp();
    } else {
        navigate('login');
    }
});

async function bootApp() {
    refData = await api('/reference');
    updateHeaderUI();
    navigate('home');
}

function updateHeaderUI() {
    const h1 = document.querySelector('.app-header h1');
    if (h1) h1.addEventListener('click', () => navigate('home'));
    const settingsBtn = document.getElementById('btn-settings');
    if (settingsBtn) settingsBtn.style.display = isAdmin() ? '' : 'none';
    if (settingsBtn) settingsBtn.onclick = () => navigate('settings');
    // User info in header
    const userInfo = document.getElementById('header-user');
    if (userInfo && currentUser) {
        userInfo.innerHTML = `<span style="font-size:0.85rem;opacity:0.9">${esc(currentUser.display_name || currentUser.username)}</span>
            <button id="btn-logout" style="background:none;border:none;color:white;cursor:pointer;font-size:0.8rem;text-decoration:underline;opacity:0.8">Logga ut</button>`;
        userInfo.querySelector('#btn-logout')?.addEventListener('click', async () => {
            await api('/auth/logout', { method: 'POST' });
            currentUser = null;
            navigate('login');
        });
    }
}

// ── Helpers ────────────────────────────────────────────────────────

function esc(str) { if (!str) return ''; const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }
function fmtDate(dt) { return new Date(dt).toLocaleDateString('sv-SE'); }
function statusLabel(s) { return { draft: 'Utkast', in_progress: 'P\u00e5g\u00e5ende', finalized: 'Slutf\u00f6rd' }[s] || s; }
function setBreadcrumb(items) {
    const el = document.querySelector('.breadcrumb');
    if (!el) return;
    if (!items.length) { el.innerHTML = 'Systemst\u00f6d f\u00f6r mognadsdialog'; return; }
    el.innerHTML = items.map(it => `<a onclick="navigate('${it.view}'${it.params ? ', ' + JSON.stringify(it.params) : ''})">${it.label}</a>`).join(' &rsaquo; ');
}
function flashSave(elId) { const el = document.getElementById(elId); if (!el) return; el.classList.add('visible'); setTimeout(() => el.classList.remove('visible'), 1500); }
function createModal(html) {
    const m = document.createElement('div'); m.className = 'modal-overlay';
    m.innerHTML = `<div class="card">${html}</div>`;
    document.body.appendChild(m);
    m.addEventListener('click', e => { if (e.target === m) m.remove(); });
    return m;
}
function getMcfData(perspKey) { return refData.perspective_maturity.find(pm => pm.perspective_key === perspKey); }
const LEVEL_COLORS = { 1: '#e74c3c', 2: '#f39c12', 3: '#27ae60', 4: '#2980b9' };
const LEVEL_BG = { 1: '#fdf2f2', 2: '#fef9f0', 3: '#f0faf4', 4: '#f0f6fc' };

// ── VIEW: Login ────────────────────────────────────────────────────

routes.login = async () => {
    const app = document.getElementById('app');
    document.getElementById('header-user') && (document.getElementById('header-user').innerHTML = '');
    document.getElementById('btn-settings') && (document.getElementById('btn-settings').style.display = 'none');
    setBreadcrumb([]);
    app.innerHTML = `
    <div class="container" style="max-width:400px;margin-top:3rem">
        <div class="card" style="text-align:center">
            <h2>Logga in</h2>
            <div id="login-error" style="color:var(--danger);font-size:0.9rem;margin-bottom:1rem;display:none"></div>
            <div class="form-group" style="text-align:left">
                <label>Anv\u00e4ndarnamn</label>
                <input id="login-user" type="text" autofocus />
            </div>
            <div class="form-group" style="text-align:left">
                <label>L\u00f6senord</label>
                <input id="login-pass" type="password" />
            </div>
            <button class="btn btn-primary" id="login-btn" style="width:100%">Logga in</button>
        </div>
    </div>`;

    async function doLogin() {
        const username = app.querySelector('#login-user').value.trim();
        const password = app.querySelector('#login-pass').value;
        const errEl = app.querySelector('#login-error');
        if (!username || !password) { errEl.textContent = 'Ange anv\u00e4ndarnamn och l\u00f6senord'; errEl.style.display = 'block'; return; }
        try {
            const res = await fetch(API + '/auth/login', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await res.json();
            if (!res.ok) { errEl.textContent = data.detail || 'Inloggning misslyckades'; errEl.style.display = 'block'; return; }
            currentUser = data.user;
            await bootApp();
        } catch (e) { errEl.textContent = 'N\u00e5got gick fel'; errEl.style.display = 'block'; }
    }

    app.querySelector('#login-btn')?.addEventListener('click', doLogin);
    app.querySelector('#login-pass')?.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
    app.querySelector('#login-user')?.addEventListener('keydown', e => { if (e.key === 'Enter') app.querySelector('#login-pass')?.focus(); });
};

// ── VIEW: Users (admin) ────────────────────────────────────────────

routes.users = async () => {
    const app = document.getElementById('app');
    if (!isAdmin()) { navigate('home'); return; }
    setBreadcrumb([{ label: 'Hem', view: 'home' }]);

    const users = await api('/users');

    app.innerHTML = `
    <div class="container" style="max-width:800px">
        <div class="card">
            <div class="flex-between mb-2">
                <h2>Anv\u00e4ndare</h2>
                <button class="btn btn-primary btn-sm" id="btn-new-user">+ Ny anv\u00e4ndare</button>
            </div>
            <table style="width:100%;border-collapse:collapse">
                <thead>
                    <tr style="border-bottom:2px solid var(--border)">
                        <th style="text-align:left;padding:0.5rem">Anv\u00e4ndarnamn</th>
                        <th style="text-align:left;padding:0.5rem">Namn</th>
                        <th style="text-align:center;padding:0.5rem">Roll</th>
                        <th style="text-align:right;padding:0.5rem"></th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(u => `
                    <tr style="border-bottom:1px solid var(--border)">
                        <td style="padding:0.5rem;font-weight:600">${esc(u.username)}</td>
                        <td style="padding:0.5rem">${esc(u.display_name)}</td>
                        <td style="padding:0.5rem;text-align:center">
                            <span class="badge ${u.role === 'admin' ? 'badge-finalized' : 'badge-draft'}">${u.role === 'admin' ? 'Admin' : 'Deltagare'}</span>
                        </td>
                        <td style="padding:0.5rem;text-align:right">
                            <button class="btn btn-outline btn-sm btn-edit-user" data-id="${u.id}" data-username="${esc(u.username)}" data-name="${esc(u.display_name)}" data-role="${u.role}">\u00c4ndra</button>
                            ${u.id !== currentUser.id ? `<button class="btn btn-outline btn-sm btn-del-user" data-id="${u.id}" data-username="${esc(u.username)}" style="color:var(--danger);border-color:var(--danger);margin-left:0.3rem">Ta bort</button>` : ''}
                        </td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
    </div>`;

    app.querySelector('#btn-new-user')?.addEventListener('click', () => showUserDialog());
    app.querySelectorAll('.btn-edit-user').forEach(btn => {
        btn.addEventListener('click', () => showUserDialog({
            id: +btn.dataset.id, username: btn.dataset.username,
            display_name: btn.dataset.name, role: btn.dataset.role,
        }));
    });
    app.querySelectorAll('.btn-del-user').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm(`Ta bort anv\u00e4ndare "${btn.dataset.username}"?`)) return;
            await api(`/users/${btn.dataset.id}`, { method: 'DELETE' });
            navigate('users');
        });
    });
};

function showUserDialog(existing = null) {
    const isEdit = !!existing;
    const m = createModal(`
        <h2>${isEdit ? '\u00c4ndra anv\u00e4ndare' : 'Ny anv\u00e4ndare'}</h2>
        <div class="form-group">
            <label>Anv\u00e4ndarnamn</label>
            <input id="u-username" type="text" value="${isEdit ? esc(existing.username) : ''}" ${isEdit ? 'disabled style="background:#f5f5f5"' : ''} />
        </div>
        <div class="form-group">
            <label>Visningsnamn</label>
            <input id="u-name" type="text" value="${isEdit ? esc(existing.display_name) : ''}" />
        </div>
        <div class="form-group">
            <label>Roll</label>
            <select id="u-role">
                <option value="participant" ${existing?.role === 'participant' ? 'selected' : ''}>Deltagare</option>
                <option value="admin" ${existing?.role === 'admin' ? 'selected' : ''}>Administrat\u00f6r</option>
            </select>
        </div>
        <div class="form-group">
            <label>${isEdit ? 'Nytt l\u00f6senord (l\u00e4mna tomt f\u00f6r att beh\u00e5lla)' : 'L\u00f6senord'}</label>
            <input id="u-pass" type="password" />
        </div>
        <div id="u-error" style="color:var(--danger);font-size:0.9rem;display:none;margin-bottom:0.5rem"></div>
        <div style="display:flex;gap:0.5rem;justify-content:flex-end">
            <button class="btn btn-outline" id="modal-cancel">Avbryt</button>
            <button class="btn btn-primary" id="modal-save">${isEdit ? 'Spara' : 'Skapa'}</button>
        </div>
    `);

    m.querySelector('#modal-cancel').addEventListener('click', () => m.remove());
    m.querySelector('#modal-save').addEventListener('click', async () => {
        const errEl = m.querySelector('#u-error');
        const username = m.querySelector('#u-username').value.trim();
        const display_name = m.querySelector('#u-name').value.trim();
        const role = m.querySelector('#u-role').value;
        const password = m.querySelector('#u-pass').value;

        if (!isEdit && (!username || !password)) {
            errEl.textContent = 'Anv\u00e4ndarnamn och l\u00f6senord kr\u00e4vs'; errEl.style.display = 'block'; return;
        }
        try {
            if (isEdit) {
                const body = { display_name, role };
                if (password) body.password = password;
                await api(`/users/${existing.id}`, { method: 'PUT', body: JSON.stringify(body) });
            } else {
                await api('/users', { method: 'POST', body: JSON.stringify({ username, password, display_name, role }) });
            }
            m.remove();
            navigate('users');
        } catch (e) {
            errEl.textContent = e.message; errEl.style.display = 'block';
        }
    });
}

// ── VIEW: Home ─────────────────────────────────────────────────────

routes.home = async () => {
    const app = document.getElementById('app');
    setBreadcrumb([]);
    const orgs = await api('/organizations');
    app.innerHTML = `<div class="container"><div class="card">
        <div class="flex-between mb-2"><h2>Enheter</h2>
        ${isAdmin() ? '<button class="btn btn-primary" id="btn-new-org">+ Ny enhet</button>' : ''}</div>
        ${orgs.length === 0 ? '<div class="empty-state">Inga enheter \u00e4nnu. Skapa en f\u00f6r att b\u00f6rja.</div>'
        : `<ul class="item-list">${orgs.map(o => `<li data-id="${o.id}"><div><strong>${esc(o.name)}</strong><div style="font-size:0.85rem;color:var(--text-light)">${esc(o.description)}</div></div><span style="font-size:0.85rem;color:var(--text-light)">${fmtDate(o.created_at)}</span></li>`).join('')}</ul>`}
    </div></div>`;
    app.querySelector('#btn-new-org')?.addEventListener('click', () => {
        const m = createModal(`<h2>Ny enhet</h2><div class="form-group"><label>Namn</label><input id="org-name" type="text" placeholder="T.ex. T.ex. IT-avdelningen" /></div><div class="form-group"><label>Beskrivning</label><textarea id="org-desc" rows="2" placeholder="Valfri"></textarea></div><div style="display:flex;gap:0.5rem;justify-content:flex-end"><button class="btn btn-outline" id="modal-cancel">Avbryt</button><button class="btn btn-primary" id="modal-save">Skapa</button></div>`);
        m.querySelector('#modal-cancel').addEventListener('click', () => m.remove());
        m.querySelector('#modal-save').addEventListener('click', async () => { const n = m.querySelector('#org-name').value.trim(); if (!n) return alert('Ange ett namn f\u00f6r enheten'); await api('/organizations', { method: 'POST', body: JSON.stringify({ name: n, description: m.querySelector('#org-desc').value.trim() }) }); m.remove(); navigate('home'); });
    });
    app.querySelectorAll('.item-list li').forEach(li => li.addEventListener('click', () => navigate('org', { orgId: +li.dataset.id })));
};

// ── VIEW: Organization ─────────────────────────────────────────────

routes.org = async ({ orgId }) => {
    const app = document.getElementById('app');
    const org = await api(`/organizations/${orgId}`);
    const assessments = await api(`/organizations/${orgId}/assessments`);
    setBreadcrumb([{ label: 'Hem', view: 'home' }]);
    const fin = assessments.filter(a => a.status === 'finalized');
    app.innerHTML = `<div class="container">
        <div class="card"><div class="flex-between mb-2"><div><h2>${esc(org.name)}</h2><p style="color:var(--text-light);font-size:0.9rem">${esc(org.description)}</p></div>
        <div class="btn-group">${isAdmin() && fin.length >= 2 ? `<button class="btn btn-outline btn-sm" id="btn-compare">J\u00e4mf\u00f6r \u00f6ver tid</button>` : ''}${isAdmin() ? '<button class="btn btn-primary" id="btn-new-assessment">+ Ny mognadsdialog</button>' : ''}</div></div></div>
        <div class="card"><h2>Mognadsdialog (ledning)</h2>
        ${assessments.length === 0 ? '<div class="empty-state">Inga dialoger \u00e4nnu.</div>'
        : `<ul class="item-list">${assessments.map(a => `<li data-id="${a.id}" data-type="dialogue"><div><strong>${esc(a.title)}</strong><div style="font-size:0.85rem;color:var(--text-light)">${a.facilitator ? 'Ansvarig: '+esc(a.facilitator) : ''}${a.participants ? ' &middot; '+esc(a.participants) : ''}</div></div><div style="text-align:right"><span class="badge badge-${a.status}">${statusLabel(a.status)}</span><div style="font-size:0.8rem;color:var(--text-light);margin-top:0.3rem">${fmtDate(a.created_at)}</div></div></li>`).join('')}</ul>`}
        </div>
        <div class="card"><div class="flex-between mb-2"><h2>Mognadsmätning (enheter)</h2>
        ${isAdmin() ? '<button class="btn btn-primary btn-sm" id="btn-new-survey">+ Ny mätning</button>' : ''}</div>
        <div id="survey-list"></div>
        </div></div>`;
    app.querySelector('#btn-new-assessment')?.addEventListener('click', () => {
        const m = createModal(`<h2>Ny mognadsdialog</h2><div class="form-group"><label>Titel</label><input id="a-title" type="text" placeholder="T.ex. Mognadsdialog VT 2026" /></div><div class="form-group"><label>Ansvarig</label><input id="a-facilitator" type="text" /></div><div class="form-group"><label>Deltagare</label><textarea id="a-participants" rows="2" placeholder="Namn, separerade med komma"></textarea></div><div style="display:flex;gap:0.5rem;justify-content:flex-end"><button class="btn btn-outline" id="modal-cancel">Avbryt</button><button class="btn btn-primary" id="modal-save">Skapa & starta</button></div>`);
        m.querySelector('#modal-cancel').addEventListener('click', () => m.remove());
        m.querySelector('#modal-save').addEventListener('click', async () => { const t = m.querySelector('#a-title').value.trim(); if (!t) return alert('Ange titel'); const r = await api('/assessments', { method: 'POST', body: JSON.stringify({ organization_id: orgId, title: t, facilitator: m.querySelector('#a-facilitator').value.trim(), participants: m.querySelector('#a-participants').value.trim() }) }); m.remove(); navigate('dialogue', { assessmentId: r.id }); });
    });
    app.querySelector('#btn-compare')?.addEventListener('click', () => navigate('compare', { orgId }));
    app.querySelectorAll('.item-list li[data-type="dialogue"]').forEach(li => li.addEventListener('click', () => navigate('dialogue', { assessmentId: +li.dataset.id })));
    app.querySelector('#btn-new-survey')?.addEventListener('click', () => showNewSurveyDialog(orgId));

    // Load surveys
    api(`/organizations/${orgId}/surveys`).then(surveys => {
        const sl = app.querySelector('#survey-list');
        if (!sl) return;
        if (surveys.length === 0) { sl.innerHTML = '<div class="empty-state" style="padding:1.5rem">Inga m\u00e4tningar \u00e4nnu.</div>'; return; }
        sl.innerHTML = `<ul class="item-list">${surveys.map(s => {
            const profileName = surveyRefData?.profiles?.[s.profile_key]?.name || s.profile_key;
            return `<li data-id="${s.id}" data-type="survey"><div><strong>${esc(s.title)}</strong><div style="font-size:0.85rem;color:var(--text-light)">${esc(profileName)}${s.respondent_name ? ' \u00b7 '+esc(s.respondent_name) : ''}</div></div><div style="text-align:right"><span class="badge badge-${s.status === 'completed' ? 'finalized' : 'in_progress'}">${s.status === 'completed' ? 'Slutf\u00f6rd' : 'P\u00e5g\u00e5ende'}</span><div style="font-size:0.8rem;color:var(--text-light);margin-top:0.3rem">${fmtDate(s.created_at)}</div></div></li>`;
        }).join('')}</ul>`;
        sl.querySelectorAll('li[data-type="survey"]').forEach(li => li.addEventListener('click', () => navigate('survey', { surveyId: +li.dataset.id })));
    });
};

let surveyRefData = null;
async function getSurveyRef() {
    if (!surveyRefData) surveyRefData = await api('/survey/reference');
    return surveyRefData;
}

function showNewSurveyDialog(orgId) {
    getSurveyRef().then(ref => {
        const m = createModal(`
            <h2>Ny mognadsmätning</h2>
            <div class="form-group"><label>Titel</label><input id="sv-title" type="text" placeholder="T.ex. Infosäk-mätning IT VT2026" /></div>
            <div class="form-group"><label>Enhetsprofil</label>
                <select id="sv-profile">${Object.entries(ref.profiles).map(([k, v]) => `<option value="${k}">${v.name} (${v.example_units.join(', ')})</option>`).join('')}</select>
                <div class="hint">Profilen styr vilka frågor som visas — välj den som bäst matchar enheten.</div>
            </div>
            <div class="form-group"><label>Respondent (valfritt)</label><input id="sv-name" type="text" placeholder="Namn på den som svarar" /></div>
            <div style="display:flex;gap:0.5rem;justify-content:flex-end">
                <button class="btn btn-outline" id="modal-cancel">Avbryt</button>
                <button class="btn btn-primary" id="modal-save">Skapa</button>
            </div>
        `);
        m.querySelector('#modal-cancel').addEventListener('click', () => m.remove());
        m.querySelector('#modal-save').addEventListener('click', async () => {
            const t = m.querySelector('#sv-title').value.trim();
            if (!t) return alert('Ange en titel');
            const res = await api('/surveys', { method: 'POST', body: JSON.stringify({
                organization_id: orgId, title: t,
                profile_key: m.querySelector('#sv-profile').value,
                respondent_name: m.querySelector('#sv-name').value.trim(),
            })});
            m.remove();
            navigate('survey', { surveyId: res.id });
        });
    });
}

// ── VIEW: Dialogue (MCF structured assessment) ─────────────────────

routes.dialogue = async ({ assessmentId }) => {
    const app = document.getElementById('app');
    const data = await api(`/assessments/${assessmentId}`);
    const assessment = data.assessment;
    const perspectives = data.perspectives;
    const isFinalized = assessment.status === 'finalized';

    if (assessment.status === 'draft') {
        await api(`/assessments/${assessmentId}/status?status=in_progress`, { method: 'PATCH' });
        assessment.status = 'in_progress';
    }

    const perspOrder = refData.perspectives.map(p => p.key);
    perspectives.sort((a, b) => perspOrder.indexOf(a.perspective_key) - perspOrder.indexOf(b.perspective_key));

    let currentIdx = 0;

    setBreadcrumb([
        { label: 'Hem', view: 'home' },
        { label: esc(assessment.title), view: 'org', params: { orgId: assessment.organization_id } },
    ]);

    function getSuggestedLevel(persp) {
        const dims = persp.dimension_assessments || [];
        const levels = dims.map(d => d.selected_level).filter(l => l !== null && l !== undefined);
        if (levels.length === 0) return null;
        return Math.min(...levels); // Conservative: lowest dimension determines level
    }

    function getProgress() {
        const assessed = perspectives.filter(p => p.chosen_level !== null).length;
        return { assessed, total: perspectives.length, pct: Math.round((assessed / perspectives.length) * 100) };
    }

    async function render() {
        const persp = perspectives[currentIdx];
        const pRef = refData.perspectives.find(p => p.key === persp.perspective_key);
        const mcf = getMcfData(persp.perspective_key);
        const progress = getProgress();
        const suggested = getSuggestedLevel(persp);

        app.innerHTML = `
        <div class="container">
            <div class="flex-between mb-2">
                <div><h2 style="margin:0">${esc(assessment.title)}</h2>
                <span style="font-size:0.85rem;color:var(--text-light)">${esc(assessment.facilitator)} &middot; ${fmtDate(assessment.created_at)}</span></div>
                <div class="btn-group">
                    <button class="btn btn-outline btn-sm" id="btn-results">Resultat\u00f6versikt</button>
                    ${isFinalized ? '<span class="badge badge-finalized">Slutf\u00f6rd</span>' : ''}
                </div>
            </div>

            <div class="progress-label">${progress.assessed} av ${progress.total} perspektiv bed\u00f6mda (${progress.pct}%)</div>
            <div class="progress-bar"><div class="progress-fill" style="width:${progress.pct}%"></div></div>

            <!-- Stepper -->
            <div class="stepper">
                ${perspectives.map((p, i) => {
                    const ref = refData.perspectives.find(r => r.key === p.perspective_key);
                    const lvl = p.chosen_level;
                    const dimsDone = (p.dimension_assessments || []).filter(d => d.selected_level).length;
                    return `<div class="stepper-item ${i === currentIdx ? 'active' : ''} ${dimsDone > 0 ? 'has-notes' : ''}" data-idx="${i}">
                        ${ref.name_sv}<br><span class="level-badge level-${lvl || 'none'}">${lvl || '\u2013'}</span>
                    </div>`;
                }).join('')}
            </div>

            <!-- Perspective content -->
            <div class="card">
                <h2>${pRef.name_sv}</h2>
                <p style="color:var(--text-light);margin-bottom:1rem">${pRef.description_sv}</p>

                <!-- Subprocess diagram -->
                ${mcf ? `
                <div style="margin-bottom:1.5rem">
                    <h3>Delprocesser</h3>
                    <div style="display:flex;gap:0;flex-wrap:wrap;margin:0.5rem 0">
                        ${mcf.subprocesses.map((sp, i) => `
                            <div style="background:#c0392b;color:white;padding:0.6rem 1rem;border-radius:6px;font-size:0.85rem;font-weight:600;min-width:100px;text-align:center;position:relative;${i < mcf.subprocesses.length - 1 ? 'margin-right:0.3rem' : ''}" title="${esc(sp.description)}">
                                ${esc(sp.name)}
                            </div>
                        `).join('<div style="display:flex;align-items:center;color:var(--text-light);font-size:1.2rem;margin:0 0.1rem">\u2192</div>')}
                    </div>
                </div>` : ''}

                <!-- Culture label -->
                ${mcf && persp.chosen_level ? `
                <div style="background:${LEVEL_BG[persp.chosen_level]};border-left:4px solid ${LEVEL_COLORS[persp.chosen_level]};padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem;font-size:0.9rem">
                    <strong>K\u00e4nnetecken:</strong> ${esc(mcf.culture_labels[persp.chosen_level])}
                </div>` : ''}

                <!-- Dimension assessments -->
                ${refData.dimensions.map(dim => {
                    const da = (persp.dimension_assessments || []).find(d => d.dimension_key === dim.key) || { selected_level: null, notes: '' };
                    const descriptions = mcf ? mcf.descriptions[dim.key] || {} : {};
                    return `
                    <div class="card" style="background:var(--bg);box-shadow:none;border:1px solid var(--border);margin-bottom:1rem">
                        <h3>${dim.name_sv}</h3>
                        <p style="font-size:0.85rem;color:var(--text-light);margin-bottom:0.8rem">${dim.description_sv}</p>

                        <div class="level-descriptions">
                            ${[1,2,3,4].map(lvl => {
                                const desc = descriptions[lvl] || '';
                                const isSelected = da.selected_level === lvl;
                                return `
                                <div class="level-desc-option ${isSelected ? 'selected' : ''}" data-perspective="${persp.perspective_key}" data-dimension="${dim.key}" data-level="${lvl}" ${isFinalized ? '' : 'role="button"'}
                                     style="border-left:4px solid ${LEVEL_COLORS[lvl]};${isSelected ? `background:${LEVEL_BG[lvl]}` : ''}">
                                    <div class="level-desc-header">
                                        <span class="level-badge level-${lvl}" style="display:inline-block;width:22px;height:22px;line-height:22px;font-size:0.7rem">${lvl}</span>
                                        <strong style="font-size:0.85rem;margin-left:0.4rem">Niv\u00e5 ${lvl}</strong>
                                        ${isSelected ? '<span style="margin-left:auto;color:var(--accent);font-weight:600;font-size:0.8rem">\u2713 Vald</span>' : ''}
                                    </div>
                                    <p style="font-size:0.85rem;margin-top:0.4rem;color:var(--text);line-height:1.5">${esc(desc)}</p>
                                </div>`;
                            }).join('')}
                        </div>

                        <div class="form-group mt-1">
                            <label style="font-size:0.85rem">Kommentar (valfritt)</label>
                            <textarea class="dim-comment" data-perspective="${persp.perspective_key}" data-dimension="${dim.key}" rows="2" ${isFinalized ? 'disabled' : ''} placeholder="Noteringar fr\u00e5n dialogen...">${esc(da.notes)}</textarea>
                            <span class="save-indicator" id="save-${dim.key}">Sparat</span>
                        </div>
                    </div>`;
                }).join('')}

                <!-- Overall level (auto-calculated) -->
                <div class="card" style="background:#fafbfc;border:2px solid var(--primary-light)">
                    <h3>Samlad bed\u00f6mning \u2013 ${pRef.name_sv}</h3>
                    ${(() => {
                        const dims = persp.dimension_assessments || [];
                        const answered = dims.filter(d => d.selected_level);
                        const allAnswered = answered.length === 4;
                        if (!allAnswered) {
                            return `<p style="font-size:0.9rem;color:var(--text-light)">Bed\u00f6m alla fyra dimensioner ovan f\u00f6r att f\u00e5 en samlad niv\u00e5. <strong>${answered.length} av 4</strong> dimensioner bed\u00f6mda.</p>`;
                        }
                        const lvl = suggested;
                        const dimNames = { ways_of_working: 'Arbetss\u00e4tt', application: 'Till\u00e4mpning', results: 'Resultat', follow_up_learn_improve: 'F\u00f6lja upp, l\u00e4ra och f\u00f6rb\u00e4ttra' };
                        return `
                        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                            <span class="level-badge level-${lvl}" style="display:inline-block;width:48px;height:48px;line-height:48px;font-size:1.4rem">${lvl}</span>
                            <div>
                                <div style="font-size:1.1rem;font-weight:700;color:${LEVEL_COLORS[lvl]}">Niv\u00e5 ${lvl} \u2013 ${refData.maturity_levels.find(m=>m.level===lvl).name_sv.replace(/Niv\u00e5 \d \u2013 /,'')}</div>
                                ${mcf ? `<div style="font-size:0.85rem;color:var(--text-light)">${esc(mcf.culture_labels[lvl])}</div>` : ''}
                            </div>
                        </div>
                        <div style="font-size:0.9rem;margin-bottom:1rem">
                            <strong>Baserat p\u00e5:</strong>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem 1rem;margin-top:0.4rem">
                                ${dims.map(d => {
                                    const name = dimNames[d.dimension_key] || d.dimension_key;
                                    const dl = d.selected_level;
                                    const isLowest = dl === lvl;
                                    return `<div style="display:flex;align-items:center;gap:0.4rem">
                                        <span class="level-badge level-${dl}" style="display:inline-block;width:20px;height:20px;line-height:20px;font-size:0.65rem">${dl}</span>
                                        <span style="font-size:0.85rem;${isLowest && dl < Math.max(...dims.map(x=>x.selected_level)) ? 'font-weight:600;color:var(--danger)' : ''}">${name}</span>
                                    </div>`;
                                }).join('')}
                            </div>
                            <p style="font-size:0.8rem;color:var(--text-light);margin-top:0.5rem">Den samlade niv\u00e5n baseras p\u00e5 den l\u00e4gsta dimensionsniv\u00e5n.</p>
                        </div>`;
                    })()}

                    ${persp.chosen_level ? `<div id="guidance-container"></div>` : ''}
                </div>

                <!-- Nav -->
                <div class="flex-between mt-2">
                    <button class="btn btn-outline" id="btn-prev" ${currentIdx === 0 ? 'disabled' : ''}>&larr; F\u00f6reg\u00e5ende</button>
                    <span style="color:var(--text-light);font-size:0.9rem">${currentIdx + 1} / ${perspectives.length}</span>
                    ${currentIdx < perspectives.length - 1
                        ? `<button class="btn btn-primary" id="btn-next">N\u00e4sta &rarr;</button>`
                        : (!isFinalized && isAdmin() && progress.pct === 100
                            ? `<button class="btn btn-accent" id="btn-finalize">Slutf\u00f6r dialog</button>`
                            : `<button class="btn btn-primary" id="btn-results-end">Visa resultat</button>`
                        )
                    }
                </div>
            </div>
        </div>`;

        // Load guidance if level set
        if (persp.chosen_level) {
            api(`/guidance/${persp.perspective_key}/${persp.chosen_level}`).then(g => {
                const gc = document.getElementById('guidance-container');
                if (!gc) return;
                gc.innerHTML = `<div class="guidance-panel"><h4>V\u00e4gledning mot niv\u00e5 ${g.next_level}</h4><ul>${g.suggestions.map(s => `<li>${esc(s)}</li>`).join('')}</ul><p style="font-size:0.8rem;color:var(--text-light);margin-top:0.5rem;font-style:italic">Riktningsgivande f\u00f6rslag, inte en checklista.</p></div>`;
            }).catch(() => {});
        }

        bindEvents();
    }

    function bindEvents() {
        const persp = perspectives[currentIdx];

        app.querySelectorAll('.stepper-item').forEach(el => el.addEventListener('click', () => { currentIdx = +el.dataset.idx; render(); }));
        app.querySelector('#btn-prev')?.addEventListener('click', () => { if (currentIdx > 0) { currentIdx--; render(); } });
        app.querySelector('#btn-next')?.addEventListener('click', () => { if (currentIdx < perspectives.length - 1) { currentIdx++; render(); } });
        app.querySelector('#btn-results')?.addEventListener('click', () => navigate('results', { assessmentId }));
        app.querySelector('#btn-finalize')?.addEventListener('click', async () => {
            if (!confirm('\u00c4r du s\u00e4ker p\u00e5 att du vill slutf\u00f6ra dialogen? Den kan inte \u00e4ndras efter\u00e5t.')) return;
            await api(`/assessments/${assessmentId}/status?status=finalized`, { method: 'PATCH' });
            navigate('results', { assessmentId });
        });
        app.querySelector('#btn-results-end')?.addEventListener('click', () => navigate('results', { assessmentId }));

        if (isFinalized) return;

        // Dimension level selection
        const dimNames = { ways_of_working: 'Arbetss\u00e4tt', application: 'Till\u00e4mpning', results: 'Resultat', follow_up_learn_improve: 'F\u00f6lja upp, l\u00e4ra och f\u00f6rb\u00e4ttra' };
        app.querySelectorAll('.level-desc-option[role="button"]').forEach(el => {
            el.addEventListener('click', async () => {
                const pk = el.dataset.perspective, dk = el.dataset.dimension, lvl = +el.dataset.level;
                const da = persp.dimension_assessments.find(d => d.dimension_key === dk);
                const newLevel = (da && da.selected_level === lvl) ? null : lvl;
                if (da) da.selected_level = newLevel;
                await api(`/assessments/${assessmentId}/perspectives/${pk}/dimensions/${dk}`, {
                    method: 'PUT', body: JSON.stringify({ selected_level: newLevel, notes: da ? da.notes : '' }),
                });
                // Auto-calculate level and reasoning
                const level = getSuggestedLevel(persp);
                persp.chosen_level = level;
                persp.suggested_level = level;
                // Auto-generate reasoning from dimension selections
                const dims = persp.dimension_assessments.filter(d => d.selected_level);
                const reasoning = dims.length === 4
                    ? dims.map(d => `${dimNames[d.dimension_key] || d.dimension_key}: Niv\u00e5 ${d.selected_level}`).join('. ') + `. Samlad niv\u00e5: ${level} (l\u00e4gsta dimensionen).`
                    : '';
                persp.reasoning = reasoning;
                await api(`/assessments/${assessmentId}/perspectives/${pk}`, {
                    method: 'PUT', body: JSON.stringify({ chosen_level: level, suggested_level: level, reasoning }),
                });
                render();
            });
        });

        // Comments auto-save
        let saveTimers = {};
        app.querySelectorAll('.dim-comment').forEach(ta => {
            ta.addEventListener('input', () => {
                const pk = ta.dataset.perspective, dk = ta.dataset.dimension;
                const da = persp.dimension_assessments.find(d => d.dimension_key === dk);
                clearTimeout(saveTimers[dk]);
                saveTimers[dk] = setTimeout(async () => {
                    if (da) da.notes = ta.value;
                    await api(`/assessments/${assessmentId}/perspectives/${pk}/dimensions/${dk}`, {
                        method: 'PUT', body: JSON.stringify({ selected_level: da ? da.selected_level : null, notes: ta.value }),
                    });
                    flashSave(`save-${dk}`);
                }, 600);
            });
        });

    }

    render();
};

// ── VIEW: Results ──────────────────────────────────────────────────

routes.results = async ({ assessmentId }) => {
    const app = document.getElementById('app');
    const data = await api(`/assessments/${assessmentId}`);
    const assessment = data.assessment;
    const perspectives = data.perspectives;
    const perspOrder = refData.perspectives.map(p => p.key);
    perspectives.sort((a, b) => perspOrder.indexOf(a.perspective_key) - perspOrder.indexOf(b.perspective_key));

    setBreadcrumb([
        { label: 'Hem', view: 'home' },
        { label: esc(assessment.title), view: 'dialogue', params: { assessmentId } },
    ]);

    let activeTab = 'overview';

    function render() {
        app.innerHTML = `<div class="container-wide">
            <div class="flex-between mb-2"><h2>${esc(assessment.title)} \u2013 Resultat</h2>
            <div class="btn-group"><button class="btn btn-primary btn-sm" id="btn-pdf">Exportera PDF</button><button class="btn btn-outline btn-sm" id="btn-print">Skriv ut</button><button class="btn btn-outline btn-sm" id="btn-back">Tillbaka</button></div></div>
            <div class="tabs">
                <div class="tab ${activeTab === 'overview' ? 'active' : ''}" data-tab="overview">\u00d6versikt</div>
                <div class="tab ${activeTab === 'heatmap' ? 'active' : ''}" data-tab="heatmap">Dimensioner</div>
                <div class="tab ${activeTab === 'guidance' ? 'active' : ''}" data-tab="guidance">V\u00e4gledning</div>
                <div class="tab ${activeTab === 'detail' ? 'active' : ''}" data-tab="detail">Detaljer</div>
            </div>
            <div id="tab-content"></div>
        </div>`;
        app.querySelector('#btn-back')?.addEventListener('click', () => navigate('dialogue', { assessmentId }));
        app.querySelector('#btn-print')?.addEventListener('click', () => window.print());
        app.querySelector('#btn-pdf')?.addEventListener('click', () => downloadPdf(assessmentId));
        app.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => { activeTab = t.dataset.tab; render(); }));

        const tc = app.querySelector('#tab-content');
        if (activeTab === 'overview') renderOverview(tc, perspectives);
        else if (activeTab === 'heatmap') renderHeatmap(tc, perspectives);
        else if (activeTab === 'guidance') renderGuidance(tc, perspectives);
        else if (activeTab === 'detail') renderDetail(tc, perspectives);
    }
    render();
};

function renderOverview(c, perspectives) {
    c.innerHTML = `
    <div class="card">
        <h2>Mognadsdialogen \u2013 Resultat</h2>
        <div class="chart-container"><canvas id="bar-chart" width="700" height="380"></canvas></div>
    </div>
    <div class="charts-grid">
        <div class="card"><h2>Radardiagram</h2><div class="chart-container"><canvas id="radar" width="450" height="450"></canvas></div></div>
        <div class="card"><h2>Mognadstrappa</h2><div id="ladder"></div></div>
    </div>
    <div class="card"><h2>Sammanfattning</h2>
    <table style="width:100%;border-collapse:collapse"><thead><tr style="border-bottom:2px solid var(--border)"><th style="text-align:left;padding:0.5rem">Perspektiv</th><th>Niv\u00e5</th><th style="text-align:left;padding:0.5rem">Motivering</th></tr></thead><tbody>
    ${perspectives.map(p => {
        const ref = refData.perspectives.find(r => r.key === p.perspective_key);
        return `<tr style="border-bottom:1px solid var(--border)"><td style="padding:0.5rem;font-weight:600">${ref.name_sv}</td><td style="padding:0.5rem;text-align:center"><span class="level-badge level-${p.chosen_level || 'none'}" style="display:inline-block">${p.chosen_level || '\u2013'}</span></td><td style="padding:0.5rem;font-size:0.9rem;color:var(--text-light)">${esc(p.reasoning) || '<em>Ingen motivering</em>'}</td></tr>`;
    }).join('')}
    </tbody></table></div>`;
    drawBarChart(perspectives);
    drawRadar(perspectives);
    drawLadder(perspectives);
}

// ── MSB-style bar chart (Nivå 1-4 y-axis, perspectives x-axis) ────

function drawBarChart(perspectives) {
    const canvas = document.getElementById('bar-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const padLeft = 60, padRight = 20, padTop = 20, padBottom = 70;
    const chartW = W - padLeft - padRight;
    const chartH = H - padTop - padBottom;
    const n = perspectives.length;
    const levels = 4;
    const barColors = { 1: '#c0392b', 2: '#e67e22', 3: '#f1c40f', 4: '#27ae60' };
    const cellBg = { 1: '#c0392b22', 2: '#e67e2222', 3: '#f1c40f22', 4: '#27ae6022' };

    ctx.clearRect(0, 0, W, H);

    // Background grid — colored rows like MSB material
    for (let l = 1; l <= levels; l++) {
        const y = padTop + chartH - (l / levels) * chartH;
        const rowH = chartH / levels;
        ctx.fillStyle = cellBg[l];
        ctx.fillRect(padLeft, y, chartW, rowH);
    }

    // Grid lines + y-axis labels
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#555';
    ctx.font = 'bold 13px sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let l = 0; l <= levels; l++) {
        const y = padTop + chartH - (l / levels) * chartH;
        ctx.beginPath();
        ctx.moveTo(padLeft, y);
        ctx.lineTo(padLeft + chartW, y);
        ctx.stroke();
        if (l > 0) {
            ctx.fillText(`Niv\u00e5 ${l}`, padLeft - 8, y + (chartH / levels) / 2);
        }
    }

    // Bars
    const barGap = 12;
    const totalBarArea = chartW / n;
    const barW = Math.min(totalBarArea - barGap * 2, 80);

    for (let i = 0; i < n; i++) {
        const p = perspectives[i];
        const ref = refData.perspectives.find(r => r.key === p.perspective_key);
        const lvl = p.chosen_level || 0;
        const x = padLeft + i * totalBarArea + (totalBarArea - barW) / 2;

        if (lvl > 0) {
            const barH = (lvl / levels) * chartH;
            const y = padTop + chartH - barH;

            // Bar with gradient-like solid color
            ctx.fillStyle = barColors[lvl];
            ctx.beginPath();
            const radius = 4;
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + barW - radius, y);
            ctx.quadraticCurveTo(x + barW, y, x + barW, y + radius);
            ctx.lineTo(x + barW, padTop + chartH);
            ctx.lineTo(x, padTop + chartH);
            ctx.lineTo(x, y + radius);
            ctx.quadraticCurveTo(x, y, x + radius, y);
            ctx.fill();

            // Level number on bar
            ctx.fillStyle = lvl === 3 ? '#555' : 'white';
            ctx.font = 'bold 18px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(lvl.toString(), x + barW / 2, y + Math.min(barH / 2, 25));
        }

        // X-axis labels (perspective names, abbreviated)
        const shortNames = {
            risk_management: 'Risk-\\nhantering',
            information_classification: 'Info-\\nklassning',
            incident_management: 'Incident-\\nhantering',
            procurement: 'Upp-\\nhandling',
            competence: 'Kompetens',
            follow_up: 'Upp-\\nf\u00f6ljning',
        };
        const label = (shortNames[p.perspective_key] || ref.name_sv).split('\\n');
        ctx.fillStyle = '#333';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        label.forEach((line, li) => {
            ctx.fillText(line, x + barW / 2, padTop + chartH + 8 + li * 16);
        });
    }
}

function renderHeatmap(c, perspectives) {
    c.innerHTML = `<div class="card"><h2>Dimensionsniv\u00e5er per perspektiv</h2>
    <table class="heatmap"><thead><tr><th></th>${refData.dimensions.map(d => `<th>${d.name_sv}</th>`).join('')}<th>Samlad</th></tr></thead><tbody>
    ${perspectives.map(p => {
        const ref = refData.perspectives.find(r => r.key === p.perspective_key);
        return `<tr><td>${ref.name_sv}</td>
        ${refData.dimensions.map(d => {
            const da = (p.dimension_assessments || []).find(x => x.dimension_key === d.key);
            const lvl = da ? da.selected_level : null;
            return `<td><span class="level-badge level-${lvl || 'none'}" style="display:inline-block">${lvl || '\u2013'}</span></td>`;
        }).join('')}
        <td><span class="level-badge level-${p.chosen_level || 'none'}" style="display:inline-block;width:28px;height:28px;line-height:28px;font-size:0.85rem">${p.chosen_level || '\u2013'}</span></td></tr>`;
    }).join('')}
    </tbody></table></div>`;
}

async function renderGuidance(c, perspectives) {
    const assessed = perspectives.filter(p => p.chosen_level);
    if (!assessed.length) { c.innerHTML = '<div class="card"><div class="empty-state">Inga perspektiv bed\u00f6mda \u00e4nnu.</div></div>'; return; }
    c.innerHTML = '<div class="empty-state">Laddar...</div>';
    const gs = await Promise.all(assessed.map(p => api(`/guidance/${p.perspective_key}/${p.chosen_level}`).catch(() => null)));
    c.innerHTML = `<div class="card"><h2>V\u00e4gledning mot n\u00e4sta niv\u00e5</h2>
    ${assessed.map((p, i) => {
        const ref = refData.perspectives.find(r => r.key === p.perspective_key);
        const g = gs[i]; if (!g) return '';
        return `<div style="margin-bottom:1.5rem"><div class="flex-between mb-1"><h3 style="margin:0">${ref.name_sv}</h3><div><span class="level-badge level-${p.chosen_level}" style="display:inline-block">${p.chosen_level}</span>${g.next_level !== g.current_level ? ` <span style="color:var(--text-light)">\u2192</span> <span class="level-badge level-${g.next_level}" style="display:inline-block">${g.next_level}</span>` : ''}</div></div>
        <div class="guidance-panel" style="margin-top:0"><ul>${g.suggestions.map(s => `<li>${esc(s)}</li>`).join('')}</ul></div></div>`;
    }).join('')}
    </div>`;
}

function renderDetail(c, perspectives) {
    c.innerHTML = `<div class="card"><h2>Fullst\u00e4ndig dokumentation</h2>
    ${perspectives.map(p => {
        const ref = refData.perspectives.find(r => r.key === p.perspective_key);
        return `<div style="margin-bottom:2rem;page-break-inside:avoid">
        <h3 style="border-bottom:2px solid var(--border);padding-bottom:0.5rem">${ref.name_sv} <span class="level-badge level-${p.chosen_level || 'none'}" style="display:inline-block;margin-left:0.5rem">${p.chosen_level || '\u2013'}</span></h3>
        ${refData.dimensions.map(d => {
            const da = (p.dimension_assessments || []).find(x => x.dimension_key === d.key);
            const lvl = da?.selected_level;
            const mcf = getMcfData(p.perspective_key);
            const desc = mcf && lvl ? (mcf.descriptions[d.key] || {})[lvl] : null;
            return `<div style="margin:0.8rem 0 0.8rem 1rem">
                <strong style="font-size:0.9rem">${d.name_sv}: <span class="level-badge level-${lvl || 'none'}" style="display:inline-block;width:18px;height:18px;line-height:18px;font-size:0.65rem">${lvl || '\u2013'}</span></strong>
                ${desc ? `<p style="font-size:0.85rem;color:var(--text);margin-top:0.2rem">${esc(desc)}</p>` : ''}
                ${da?.notes ? `<p style="font-size:0.85rem;color:var(--text-light);margin-top:0.2rem;font-style:italic">${esc(da.notes)}</p>` : ''}
            </div>`;
        }).join('')}
        ${p.reasoning ? `<div style="margin:0.8rem 0 0.8rem 1rem;padding:0.8rem;background:var(--bg);border-radius:var(--radius)"><strong>Motivering:</strong><p style="margin-top:0.2rem">${esc(p.reasoning)}</p></div>` : ''}
        </div>`;
    }).join('')}
    </div>`;
}

// ── VIEW: Compare ──────────────────────────────────────────────────

routes.compare = async ({ orgId }) => {
    const app = document.getElementById('app');
    const comp = await api(`/organizations/${orgId}/comparison`);
    const assessments = comp.assessments;
    const perspOrder = refData.perspectives.map(p => p.key);
    setBreadcrumb([{ label: 'Hem', view: 'home' }, { label: esc(comp.organization_name), view: 'org', params: { orgId } }]);

    app.innerHTML = `<div class="container-wide">
        <div class="flex-between mb-2"><h2>${esc(comp.organization_name)} \u2013 Mognadsutveckling</h2>
        <button class="btn btn-outline btn-sm" id="btn-back">Tillbaka</button></div>
        <div class="card"><h2>Utveckling \u00f6ver tid</h2><div id="timeline-chart"></div></div>
        <div class="card"><h2>Detaljerad j\u00e4mf\u00f6relse</h2>
        <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;min-width:600px">
        <thead><tr style="border-bottom:2px solid var(--border)"><th style="text-align:left;padding:0.5rem">Perspektiv</th>
        ${assessments.map(a => `<th style="text-align:center;padding:0.5rem;font-size:0.85rem">${esc(a.title)}<br><span style="font-weight:normal;color:var(--text-light)">${fmtDate(a.created_at)}</span></th>`).join('')}
        ${assessments.length >= 2 ? '<th style="text-align:center;padding:0.5rem">F\u00f6r\u00e4ndring</th>' : ''}
        </tr></thead><tbody>
        ${perspOrder.map(pk => {
            const ref = refData.perspectives.find(r => r.key === pk);
            const levels = assessments.map(a => { const pl = a.levels.find(l => l.perspective_key === pk); return pl ? pl.chosen_level : null; });
            const first = levels.find(l => l != null), last = [...levels].reverse().find(l => l != null);
            let change = '';
            if (first != null && last != null && assessments.length >= 2) {
                const d = last - first;
                change = d > 0 ? `<span class="dev-arrow up">\u2191 +${d}</span>` : d < 0 ? `<span class="dev-arrow down">\u2193 ${d}</span>` : `<span class="dev-arrow same">\u2192 0</span>`;
            }
            return `<tr style="border-bottom:1px solid var(--border)"><td style="padding:0.5rem;font-weight:600">${ref.name_sv}</td>${levels.map(l => `<td style="padding:0.5rem;text-align:center"><span class="level-badge level-${l || 'none'}" style="display:inline-block">${l || '\u2013'}</span></td>`).join('')}${assessments.length >= 2 ? `<td style="text-align:center">${change}</td>` : ''}</tr>`;
        }).join('')}
        </tbody></table></div></div>
    </div>`;
    app.querySelector('#btn-back')?.addEventListener('click', () => navigate('org', { orgId }));
    drawTimeline(assessments, perspOrder);
};

// ── Charts ─────────────────────────────────────────────────────────

function drawRadar(perspectives) {
    const canvas = document.getElementById('radar'); if (!canvas) return;
    const ctx = canvas.getContext('2d'), W = canvas.width, H = canvas.height, cx = W/2, cy = H/2, maxR = Math.min(cx,cy) - 60, n = perspectives.length, levels = 4;
    ctx.clearRect(0, 0, W, H);
    for (let l = 1; l <= levels; l++) { const r = (l/levels)*maxR; ctx.beginPath(); for (let i = 0; i <= n; i++) { const a = (Math.PI*2*i)/n - Math.PI/2; const x = cx+r*Math.cos(a), y = cy+r*Math.sin(a); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); } ctx.strokeStyle='#dce1e8'; ctx.lineWidth=1; ctx.stroke(); ctx.fillStyle='#aab'; ctx.font='11px sans-serif'; ctx.textAlign='left'; ctx.fillText(l.toString(), cx+(l/levels)*maxR*Math.cos(-Math.PI/2)+4, cy+(l/levels)*maxR*Math.sin(-Math.PI/2)+4); }
    for (let i = 0; i < n; i++) { const a = (Math.PI*2*i)/n - Math.PI/2; ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+maxR*Math.cos(a), cy+maxR*Math.sin(a)); ctx.strokeStyle='#dce1e8'; ctx.stroke(); const ref = refData.perspectives.find(r => r.key === perspectives[i].perspective_key); const lr = maxR+25, lx = cx+lr*Math.cos(a), ly = cy+lr*Math.sin(a); ctx.fillStyle='#2c3e50'; ctx.font='12px sans-serif'; ctx.textAlign=Math.cos(a)<-0.1?'right':Math.cos(a)>0.1?'left':'center'; ctx.textBaseline=Math.sin(a)<-0.1?'bottom':Math.sin(a)>0.1?'top':'middle'; ctx.fillText(ref.name_sv, lx, ly); }
    const vals = perspectives.map(p => p.chosen_level||0);
    ctx.beginPath(); for (let i = 0; i <= n; i++) { const idx=i%n, a=(Math.PI*2*idx)/n-Math.PI/2, r=(vals[idx]/levels)*maxR; const x=cx+r*Math.cos(a), y=cy+r*Math.sin(a); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); } ctx.fillStyle='rgba(41,128,185,0.2)'; ctx.fill(); ctx.strokeStyle='#2980b9'; ctx.lineWidth=2.5; ctx.stroke();
    for (let i = 0; i < n; i++) { const a=(Math.PI*2*i)/n-Math.PI/2, r=(vals[i]/levels)*maxR; ctx.beginPath(); ctx.arc(cx+r*Math.cos(a), cy+r*Math.sin(a), 5, 0, Math.PI*2); ctx.fillStyle=vals[i]?'#2980b9':'#bdc3c7'; ctx.fill(); ctx.strokeStyle='white'; ctx.lineWidth=2; ctx.stroke(); }
}

function drawLadder(perspectives) {
    const c = document.getElementById('ladder'); if (!c) return;
    const lc = ['','var(--level-1)','var(--level-2)','var(--level-3)','var(--level-4)'];
    let h = '<div style="display:flex;flex-direction:column-reverse;gap:2px">';
    for (let l = 4; l >= 1; l--) { const ml = refData.maturity_levels.find(m=>m.level===l); const at = perspectives.filter(p=>p.chosen_level===l); h += `<div style="display:flex;align-items:center;gap:1rem;padding:0.8rem 1rem;background:${at.length?lc[l]+'15':'#fafafa'};border-left:4px solid ${lc[l]};border-radius:4px"><div style="min-width:90px;font-weight:700;font-size:0.85rem;color:${lc[l]}">Niv\u00e5 ${l}</div><div style="display:flex;gap:0.5rem;flex-wrap:wrap">${at.map(p=>{const r=refData.perspectives.find(x=>x.key===p.perspective_key);return`<span class="badge" style="background:${lc[l]};color:white">${r.name_sv}</span>`;}).join('')||'<span style="color:var(--text-light);font-size:0.85rem">\u2013</span>'}</div></div>`; }
    const un = perspectives.filter(p=>!p.chosen_level);
    if (un.length) h += `<div style="display:flex;align-items:center;gap:1rem;padding:0.8rem 1rem;background:#f5f5f5;border-left:4px solid var(--level-none);border-radius:4px"><div style="min-width:90px;font-weight:700;font-size:0.85rem;color:var(--text-light)">Ej bed\u00f6md</div><div style="display:flex;gap:0.5rem;flex-wrap:wrap">${un.map(p=>{const r=refData.perspectives.find(x=>x.key===p.perspective_key);return`<span class="badge badge-draft">${r.name_sv}</span>`;}).join('')}</div></div>`;
    h += '</div>'; c.innerHTML = h;
}

function drawTimeline(assessments, perspOrder) {
    const c = document.getElementById('timeline-chart'); if (!c || !assessments.length) return;
    const lc = {1:'#e74c3c',2:'#f39c12',3:'#27ae60',4:'#2980b9'};
    let h = `<div class="timeline-header"><div class="timeline-label"></div><div class="timeline-header-track">${assessments.map(a=>`<span>${fmtDate(a.created_at)}</span>`).join('')}</div></div>`;
    for (const pk of perspOrder) {
        const ref = refData.perspectives.find(r=>r.key===pk);
        const pts = assessments.map((a,i)=>({level:(a.levels.find(l=>l.perspective_key===pk)||{}).chosen_level,idx:i}));
        h += `<div class="timeline-row"><div class="timeline-label">${ref.name_sv}</div><div class="timeline-track">`;
        const vp = pts.filter(p=>p.level!=null);
        for (let i=0;i<vp.length-1;i++){const f=vp[i],t=vp[i+1],lp=(f.idx/Math.max(assessments.length-1,1))*100,rp=(t.idx/Math.max(assessments.length-1,1))*100,col=t.level>=f.level?'#27ae6040':'#e74c3c40';h+=`<div class="timeline-connector" style="left:calc(${lp}% + 14px);width:calc(${rp-lp}% - 28px);background:${col}"></div>`;}
        for(const pt of pts){const lp=(pt.idx/Math.max(assessments.length-1,1))*100;h+=pt.level!=null?`<div class="timeline-point" style="left:calc(${lp}% - 14px);background:${lc[pt.level]}">${pt.level}</div>`:`<div class="timeline-point" style="left:calc(${lp}% - 14px);background:#bdc3c7">\u2013</div>`;}
        h += '</div></div>';
    }
    c.innerHTML = h;
}

// ── VIEW: Survey (answer questions) ─────────────────────────────────

routes.survey = async ({ surveyId }) => {
    const app = document.getElementById('app');
    const data = await api(`/surveys/${surveyId}`);
    const survey = data.survey;
    const answers = data.answers;
    const ref = await getSurveyRef();
    const isCompleted = survey.status === 'completed';
    const profileName = ref.profiles[survey.profile_key]?.name || survey.profile_key;

    setBreadcrumb([
        { label: 'Hem', view: 'home' },
        { label: profileName, view: 'org', params: { orgId: survey.organization_id } },
    ]);

    // Group answers by section
    const sections = ref.sections.filter(s => answers.some(a => a.section === s.key));
    let currentSection = 0;

    function getProgress() {
        const answered = answers.filter(a => a.selected_level !== null).length;
        return { answered, total: answers.length, pct: Math.round((answered / answers.length) * 100) };
    }

    function render() {
        const sec = sections[currentSection];
        const secAnswers = answers.filter(a => a.section === sec.key);
        const progress = getProgress();

        app.innerHTML = `
        <div class="container">
            <div class="flex-between mb-2">
                <div><h2 style="margin:0">${esc(survey.title)}</h2>
                <span style="font-size:0.85rem;color:var(--text-light)">${esc(profileName)} ${survey.respondent_name ? '\u00b7 '+esc(survey.respondent_name) : ''}</span></div>
                ${isCompleted ? '<span class="badge badge-finalized">Slutf\u00f6rd</span>' : ''}
            </div>

            <div class="progress-label">${progress.answered} av ${progress.total} fr\u00e5gor besvarade (${progress.pct}%)</div>
            <div class="progress-bar"><div class="progress-fill" style="width:${progress.pct}%"></div></div>

            <!-- Section stepper -->
            <div class="stepper">
                ${sections.map((s, i) => {
                    const sAns = answers.filter(a => a.section === s.key);
                    const sDone = sAns.filter(a => a.selected_level !== null).length;
                    const sTotal = sAns.length;
                    return `<div class="stepper-item ${i === currentSection ? 'active' : ''} ${sDone === sTotal && sTotal > 0 ? 'has-notes' : ''}" data-idx="${i}">
                        ${s.icon || ''} ${s.name}<br>
                        <span style="font-size:0.75rem">${sDone}/${sTotal}</span>
                    </div>`;
                }).join('')}
            </div>

            <!-- Questions -->
            <div class="card">
                <h2>${sec.icon || ''} ${sec.name}</h2>
                <p style="color:var(--text-light);margin-bottom:1.5rem">${sec.description}</p>

                ${secAnswers.map((a, qi) => `
                <div class="card" style="background:var(--bg);box-shadow:none;border:1px solid var(--border);margin-bottom:1rem">
                    <h3 style="font-size:0.95rem;margin-bottom:0.3rem">${qi + 1}. ${esc(a.text)}</h3>
                    <p style="font-size:0.85rem;color:var(--text-light);margin-bottom:0.8rem">${esc(a.help_text)}</p>
                    <div class="level-descriptions">
                        ${ref.levels.map(lvl => {
                            const isSelected = a.selected_level === lvl.level;
                            return `
                            <div class="level-desc-option ${isSelected ? 'selected' : ''}" data-qid="${a.question_id}" data-level="${lvl.level}" ${isCompleted ? '' : 'role="button"'}
                                 style="border-left:4px solid ${lvl.color};${isSelected ? 'background:'+lvl.color+'15' : ''}">
                                <div class="level-desc-header">
                                    <span class="level-badge" style="display:inline-block;width:22px;height:22px;line-height:22px;font-size:0.7rem;background:${lvl.color};color:white;border-radius:50%;text-align:center">${lvl.level}</span>
                                    <strong style="font-size:0.85rem;margin-left:0.4rem">${lvl.name}</strong>
                                    ${isSelected ? '<span style="margin-left:auto;color:var(--accent);font-weight:600;font-size:0.8rem">\u2713</span>' : ''}
                                </div>
                                <p style="font-size:0.8rem;margin-top:0.3rem;color:var(--text-light)">${lvl.description}</p>
                            </div>`;
                        }).join('')}
                    </div>
                </div>`).join('')}

                <!-- Nav -->
                <div class="flex-between mt-2">
                    <button class="btn btn-outline" id="sv-prev" ${currentSection === 0 ? 'disabled' : ''}>&larr; F\u00f6reg\u00e5ende</button>
                    <span style="color:var(--text-light);font-size:0.9rem">${currentSection + 1} / ${sections.length}</span>
                    ${currentSection < sections.length - 1
                        ? '<button class="btn btn-primary" id="sv-next">N\u00e4sta &rarr;</button>'
                        : (!isCompleted && progress.pct === 100
                            ? '<button class="btn btn-accent" id="sv-complete">Slutf\u00f6r m\u00e4tning</button>'
                            : (isCompleted
                                ? '<button class="btn btn-primary" id="sv-results">Visa resultat</button>'
                                : '<span style="font-size:0.85rem;color:var(--text-light)">Besvara alla fr\u00e5gor f\u00f6r att slutf\u00f6ra</span>'
                            )
                        )
                    }
                </div>
            </div>
        </div>`;

        // Events
        app.querySelectorAll('.stepper-item').forEach(el => el.addEventListener('click', () => { currentSection = +el.dataset.idx; render(); }));
        app.querySelector('#sv-prev')?.addEventListener('click', () => { if (currentSection > 0) { currentSection--; render(); } });
        app.querySelector('#sv-next')?.addEventListener('click', () => { if (currentSection < sections.length - 1) { currentSection++; render(); } });
        app.querySelector('#sv-complete')?.addEventListener('click', async () => {
            if (!confirm('Slutf\u00f6r m\u00e4tningen? Den kan inte \u00e4ndras efter\u00e5t.')) return;
            await api(`/surveys/${surveyId}/complete`, { method: 'POST' });
            navigate('surveyResults', { surveyId });
        });
        app.querySelector('#sv-results')?.addEventListener('click', () => navigate('surveyResults', { surveyId }));

        if (!isCompleted) {
            app.querySelectorAll('.level-desc-option[role="button"]').forEach(el => {
                el.addEventListener('click', async () => {
                    const qid = el.dataset.qid, lvl = +el.dataset.level;
                    const ans = answers.find(a => a.question_id === qid);
                    const newLvl = (ans && ans.selected_level === lvl) ? null : lvl;
                    if (ans) ans.selected_level = newLvl;
                    await api(`/surveys/${surveyId}/answers/${qid}`, {
                        method: 'PUT', body: JSON.stringify({ selected_level: newLvl, comment: ans?.comment || '' }),
                    });
                    render();
                });
            });
        }
    }
    render();
};

// ── VIEW: Survey Results ───────────────────────────────────────────

routes.surveyResults = async ({ surveyId }) => {
    const app = document.getElementById('app');
    const data = await api(`/surveys/${surveyId}`);
    const survey = data.survey;
    const answers = data.answers;
    const ref = await getSurveyRef();
    const profileName = ref.profiles[survey.profile_key]?.name || survey.profile_key;

    setBreadcrumb([
        { label: 'Hem', view: 'home' },
        { label: profileName, view: 'org', params: { orgId: survey.organization_id } },
    ]);

    // Calculate averages per section
    const sections = ref.sections.filter(s => answers.some(a => a.section === s.key));
    const sectionResults = sections.map(s => {
        const sAns = answers.filter(a => a.section === s.key && a.selected_level !== null);
        const avg = sAns.length > 0 ? sAns.reduce((sum, a) => sum + a.selected_level, 0) / sAns.length : 0;
        return { ...s, avg: Math.round(avg * 10) / 10, count: sAns.length };
    });
    const totalAvg = answers.filter(a => a.selected_level).length > 0
        ? Math.round(answers.filter(a => a.selected_level).reduce((s, a) => s + a.selected_level, 0) / answers.filter(a => a.selected_level).length * 10) / 10
        : 0;

    app.innerHTML = `
    <div class="container-wide">
        <div class="flex-between mb-2">
            <div><h2>${esc(survey.title)} \u2013 Resultat</h2>
            <span style="font-size:0.85rem;color:var(--text-light)">${esc(profileName)} ${survey.respondent_name ? '\u00b7 '+esc(survey.respondent_name) : ''} \u00b7 ${fmtDate(survey.created_at)}</span></div>
            <button class="btn btn-outline btn-sm" id="sv-back">Tillbaka</button>
        </div>

        <!-- Overall score -->
        <div class="card" style="text-align:center">
            <h2>Samlat resultat</h2>
            <div style="font-size:3rem;font-weight:700;color:${ref.levels[Math.min(Math.round(totalAvg) - 1, 4)]?.color || '#999'}">${totalAvg}</div>
            <div style="color:var(--text-light)">av 5.0</div>
        </div>

        <!-- Bar chart per section -->
        <div class="card">
            <h2>Resultat per omr\u00e5de</h2>
            ${sectionResults.map(s => {
                const pct = (s.avg / 5) * 100;
                const color = ref.levels[Math.min(Math.round(s.avg) - 1, 4)]?.color || '#bdc3c7';
                return `
                <div style="margin-bottom:1rem">
                    <div class="flex-between" style="margin-bottom:0.3rem">
                        <span style="font-weight:600;font-size:0.9rem">${s.icon || ''} ${s.name}</span>
                        <span style="font-weight:700;color:${color}">${s.avg}</span>
                    </div>
                    <div style="background:var(--border);border-radius:4px;height:24px;overflow:hidden">
                        <div style="background:${color};height:100%;width:${pct}%;border-radius:4px;transition:width 0.3s"></div>
                    </div>
                </div>`;
            }).join('')}
        </div>

        <!-- Detail table -->
        <div class="card">
            <h2>Alla svar</h2>
            <table style="width:100%;border-collapse:collapse">
                <thead><tr style="border-bottom:2px solid var(--border)">
                    <th style="text-align:left;padding:0.5rem">Fr\u00e5ga</th>
                    <th style="text-align:center;padding:0.5rem;width:80px">Niv\u00e5</th>
                </tr></thead>
                <tbody>
                ${answers.map(a => {
                    const lvl = a.selected_level;
                    const color = lvl ? ref.levels[lvl - 1]?.color : '#bdc3c7';
                    return `<tr style="border-bottom:1px solid var(--border)">
                        <td style="padding:0.5rem;font-size:0.9rem">${esc(a.text)}</td>
                        <td style="padding:0.5rem;text-align:center">
                            <span class="level-badge" style="display:inline-block;width:24px;height:24px;line-height:24px;font-size:0.75rem;background:${color};color:white;border-radius:50%;text-align:center">${lvl || '\u2013'}</span>
                        </td>
                    </tr>`;
                }).join('')}
                </tbody>
            </table>
        </div>
    </div>`;

    app.querySelector('#sv-back')?.addEventListener('click', () => navigate('org', { orgId: survey.organization_id }));
};

// ── VIEW: Settings ─────────────────────────────────────────────────

routes.settings = async () => {
    if (!isAdmin()) { navigate('home'); return; }
    const app = document.getElementById('app');
    const s = await api('/settings');
    setBreadcrumb([{ label: 'Hem', view: 'home' }]);

    const colorFields = [
        { key: 'primary', label: 'Prim\u00e4rf\u00e4rg (header, knappar)', default: '#E27629' },
        { key: 'primary_light', label: 'Prim\u00e4rf\u00e4rg ljus (hover, accenter)', default: '#F09A5B' },
        { key: 'accent', label: 'Accentf\u00e4rg (spara, framg\u00e5ng)', default: '#2E7D32' },
        { key: 'bg', label: 'Bakgrundsf\u00e4rg', default: '#f5f7fa' },
        { key: 'text', label: 'Textf\u00e4rg', default: '#2c3e50' },
        { key: 'text_light', label: 'Textf\u00e4rg ljus', default: '#7f8c8d' },
    ];

    app.innerHTML = `
    <div class="container" style="max-width:700px">
        <div class="card">
            <div class="flex-between mb-2">
                <h2 style="margin:0">Inst\u00e4llningar</h2>
                <button class="btn btn-outline btn-sm" id="btn-manage-users">Hantera anv\u00e4ndare</button>
            </div>

            <div class="form-group">
                <label>Applikationsnamn</label>
                <input id="s-title" type="text" value="${esc(s.app_title || 'Mognadsdialog')}" />
            </div>

            <h3 style="margin-top:1.5rem">Logotyp</h3>
            <div style="display:flex;align-items:center;gap:1rem;margin:0.5rem 0 1rem">
                ${s.logo_url ? `<img src="${s.logo_url}" style="height:48px;border-radius:4px;border:1px solid var(--border)" />` : '<span style="color:var(--text-light)">Ingen logga uppladdad</span>'}
                <label class="btn btn-outline btn-sm" style="cursor:pointer">
                    Ladda upp
                    <input type="file" id="s-logo-file" accept="image/png,image/jpeg,image/svg+xml,image/webp" style="display:none" />
                </label>
                ${s.logo_url ? '<button class="btn btn-outline btn-sm" id="s-logo-delete" style="color:var(--danger);border-color:var(--danger)">Ta bort</button>' : ''}
            </div>

            <h3>F\u00e4rger</h3>
            <p style="font-size:0.85rem;color:var(--text-light);margin-bottom:1rem">Klicka p\u00e5 f\u00e4rgrutan f\u00f6r att \u00e4ndra. F\u00f6rhandsvisning sker direkt.</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem">
                ${colorFields.map(f => `
                <div class="form-group" style="margin-bottom:0">
                    <label style="font-size:0.85rem">${f.label}</label>
                    <div style="display:flex;gap:0.5rem;align-items:center">
                        <input type="color" class="color-input" data-key="${f.key}" value="${s[f.key] || f.default}" style="width:40px;height:32px;border:1px solid var(--border);border-radius:4px;cursor:pointer;padding:0" />
                        <input type="text" class="color-hex" data-key="${f.key}" value="${s[f.key] || f.default}" style="width:90px;font-size:0.85rem;font-family:monospace" />
                    </div>
                </div>`).join('')}
            </div>

            <div style="display:flex;gap:0.5rem;margin-top:1.5rem">
                <button class="btn btn-primary" id="s-save">Spara inst\u00e4llningar</button>
                <button class="btn btn-outline" id="s-reset">\u00c5terst\u00e4ll standardf\u00e4rger</button>
            </div>
            <span class="save-indicator" id="s-saved" style="margin-left:0.5rem">Sparat!</span>
        </div>
    </div>`;

    // Live preview: sync color picker <-> hex input
    app.querySelector('#btn-manage-users')?.addEventListener('click', () => navigate('users'));

    app.querySelectorAll('.color-input').forEach(ci => {
        ci.addEventListener('input', () => {
            const hex = app.querySelector(`.color-hex[data-key="${ci.dataset.key}"]`);
            if (hex) hex.value = ci.value;
            previewTheme();
        });
    });
    app.querySelectorAll('.color-hex').forEach(hi => {
        hi.addEventListener('input', () => {
            const ci = app.querySelector(`.color-input[data-key="${hi.dataset.key}"]`);
            if (ci && /^#[0-9a-fA-F]{6}$/.test(hi.value)) ci.value = hi.value;
            previewTheme();
        });
    });

    function previewTheme() {
        const preview = { app_title: app.querySelector('#s-title').value };
        app.querySelectorAll('.color-hex').forEach(h => { preview[h.dataset.key] = h.value; });
        applyTheme({ ...appSettings, ...preview });
    }

    // Save
    app.querySelector('#s-save')?.addEventListener('click', async () => {
        const data = { app_title: app.querySelector('#s-title').value.trim() };
        app.querySelectorAll('.color-hex').forEach(h => { data[h.dataset.key] = h.value; });
        await api('/settings', { method: 'PUT', body: JSON.stringify(data) });
        appSettings = { ...appSettings, ...data };
        applyTheme(appSettings);
        flashSave('s-saved');
    });

    // Reset
    app.querySelector('#s-reset')?.addEventListener('click', () => {
        colorFields.forEach(f => {
            const ci = app.querySelector(`.color-input[data-key="${f.key}"]`);
            const hi = app.querySelector(`.color-hex[data-key="${f.key}"]`);
            if (ci) ci.value = f.default;
            if (hi) hi.value = f.default;
        });
        previewTheme();
    });

    // Logo upload
    app.querySelector('#s-logo-file')?.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const form = new FormData();
        form.append('file', file);
        try {
            const res = await fetch(API + '/settings/logo', { method: 'POST', body: form });
            if (!res.ok) { const err = await res.json(); alert(err.detail || 'Upload failed'); return; }
            const data = await res.json();
            appSettings.logo_url = data.logo_url;
            applyTheme(appSettings);
            navigate('settings');
        } catch (err) { alert('Uppladdning misslyckades: ' + err.message); }
    });

    // Logo delete
    app.querySelector('#s-logo-delete')?.addEventListener('click', async () => {
        await api('/settings/logo', { method: 'DELETE' });
        appSettings.logo_url = '';
        applyTheme(appSettings);
        navigate('settings');
    });
};

async function downloadPdf(assessmentId) {
    const btn = document.getElementById('btn-pdf');
    if (btn) { btn.disabled = true; btn.textContent = 'Genererar...'; }
    try {
        const res = await fetch(`${API}/assessments/${assessmentId}/export/pdf`);
        if (!res.ok) throw new Error('PDF error');
        const blob = await res.blob(), url = URL.createObjectURL(blob), a = document.createElement('a');
        a.href = url; a.download = `mognadsdialog-${assessmentId}.pdf`; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    } catch (e) { alert('Kunde inte generera PDF: ' + e.message); }
    finally { if (btn) { btn.disabled = false; btn.textContent = 'Exportera PDF'; } }
}
