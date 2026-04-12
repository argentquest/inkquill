/**
 * Scheduler Management UI - Main Application
 */

const API_BASE = '';

// State
let state = {
    health: null,
    tasks: [],
    jobs: [],
    loading: false,
};

// API Functions
async function apiFetch(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

async function apiPost(endpoint, body = null) {
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

// Data Loading
async function loadHealth() {
    try {
        state.health = await apiFetch('/scheduler/health');
        renderHealth();
    } catch (err) {
        console.error('Failed to load health:', err);
        document.getElementById('healthStatus').innerHTML =
            `<div class="empty-state">Failed to load health status: ${err.message}</div>`;
    }
}

async function loadTasks() {
    try {
        const data = await apiFetch('/scheduler/status');
        state.tasks = data.tasks || [];
        renderTasks();
    } catch (err) {
        console.error('Failed to load tasks:', err);
        document.getElementById('tasksList').innerHTML =
            `<div class="empty-state">Failed to load tasks: ${err.message}</div>`;
    }
}

async function loadJobs() {
    try {
        const data = await apiFetch('/scheduler/jobs');
        state.jobs = data.jobs || [];
        renderJobs();
    } catch (err) {
        console.error('Failed to load jobs:', err);
        document.getElementById('jobsList').innerHTML =
            `<div class="empty-state">Failed to load jobs: ${err.message}</div>`;
    }
}

async function refreshAll() {
    state.loading = true;
    await Promise.all([loadHealth(), loadTasks(), loadJobs()]);
    state.loading = false;
    document.getElementById('lastUpdate').textContent =
        `Updated: ${new Date().toLocaleTimeString()}`;
}

// Render Functions
function renderHealth() {
    const container = document.getElementById('healthStatus');
    if (!state.health) {
        container.innerHTML = '<div class="loading">Loading...</div>';
        return;
    }

    const statusClass = state.health.status === 'healthy' ? 'healthy' : 'unhealthy';

    container.innerHTML = `
        <div class="health-metric ${statusClass}">
            <div class="value">${state.health.status}</div>
            <div class="label">Status</div>
        </div>
        <div class="health-metric">
            <div class="value">${state.health.scheduler_running ? 'Yes' : 'No'}</div>
            <div class="label">Running</div>
        </div>
        <div class="health-metric">
            <div class="value">${state.health.registered_tasks}</div>
            <div class="label">Registered Tasks</div>
        </div>
        <div class="health-metric">
            <div class="value">${state.health.scheduled_jobs}</div>
            <div class="label">Scheduled Jobs</div>
        </div>
    `;
}

function renderTasks() {
    const container = document.getElementById('tasksList');
    if (!state.tasks.length) {
        container.innerHTML = '<div class="empty-state">No tasks registered</div>';
        return;
    }

    container.innerHTML = state.tasks.map(task => {
        const job = state.jobs.find(j => j.id === task.key);
        const isPaused = job && job.next_run === null;
        const statusBadge = isPaused
            ? '<span class="badge badge-paused">Paused</span>'
            : '<span class="badge badge-active">Active</span>';

        return `
            <div class="task-item">
                <div class="task-info">
                    <h3>${escapeHtml(task.name)}</h3>
                    <p>${escapeHtml(task.key)}</p>
                    <div class="task-meta">
                        <span class="badge badge-cron">${escapeHtml(task.cron)}</span>
                        ${statusBadge}
                        ${task.next_run ? `<span>Next: ${formatDate(task.next_run)}</span>` : ''}
                    </div>
                </div>
                <div class="task-actions">
                    <button class="btn btn-sm btn-success" onclick="triggerJob('${task.key}')">
                        Run Now
                    </button>
                    ${isPaused
                        ? `<button class="btn btn-sm btn-warning" onclick="resumeJob('${task.key}')">Resume</button>`
                        : `<button class="btn btn-sm btn-warning" onclick="pauseJob('${task.key}')">Pause</button>`
                    }
                    <button class="btn btn-sm btn-secondary" onclick="showRescheduleModal('${task.key}', '${task.cron}')">
                        Reschedule
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderJobs() {
    const container = document.getElementById('jobsList');
    if (!state.jobs.length) {
        container.innerHTML = '<div class="empty-state">No jobs scheduled</div>';
        return;
    }

    container.innerHTML = `
        <table class="jobs-table">
            <thead>
                <tr>
                    <th>Job ID</th>
                    <th>Name</th>
                    <th>Next Run</th>
                    <th>Trigger</th>
                </tr>
            </thead>
            <tbody>
                ${state.jobs.map(job => `
                    <tr>
                        <td><code>${escapeHtml(job.id)}</code></td>
                        <td>${escapeHtml(job.name)}</td>
                        <td>${job.next_run ? formatDate(job.next_run) : 'N/A'}</td>
                        <td>${escapeHtml(job.trigger)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Action Functions
async function triggerJob(taskKey) {
    try {
        await apiPost(`/scheduler/jobs/${taskKey}/run`);
        showToast(`Task "${taskKey}" triggered successfully`, 'success');
        await refreshAll();
    } catch (err) {
        showToast(`Failed to trigger task: ${err.message}`, 'error');
    }
}

async function pauseJob(taskKey) {
    try {
        await apiPost(`/scheduler/jobs/${taskKey}/pause`);
        showToast(`Task "${taskKey}" paused`, 'success');
        await refreshAll();
    } catch (err) {
        showToast(`Failed to pause task: ${err.message}`, 'error');
    }
}

async function resumeJob(taskKey) {
    try {
        await apiPost(`/scheduler/jobs/${taskKey}/resume`);
        showToast(`Task "${taskKey}" resumed`, 'success');
        await refreshAll();
    } catch (err) {
        showToast(`Failed to resume task: ${err.message}`, 'error');
    }
}

function showRescheduleModal(taskKey, currentCron) {
    const modal = document.getElementById('taskModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');

    title.textContent = `Reschedule: ${taskKey}`;
    body.innerHTML = `
        <div class="form-group">
            <label for="cronInput">Cron Expression</label>
            <input
                type="text"
                id="cronInput"
                value="${escapeHtml(currentCron)}"
                placeholder="e.g., 0 8 * * *"
            />
            <small>Format: minute hour day month weekday</small>
        </div>
        <div class="form-group">
            <label>Quick Presets</label>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                <button class="btn btn-sm btn-secondary" onclick="document.getElementById('cronInput').value='0 6 * * *'">6:00 AM Daily</button>
                <button class="btn btn-sm btn-secondary" onclick="document.getElementById('cronInput').value='0 8 * * *'">8:00 AM Daily</button>
                <button class="btn btn-sm btn-secondary" onclick="document.getElementById('cronInput').value='0 3 * * 0'">Sunday 3:00 AM</button>
                <button class="btn btn-sm btn-secondary" onclick="document.getElementById('cronInput').value='0 */6 * * *'">Every 6 Hours</button>
            </div>
        </div>
    `;

    const footer = modal.querySelector('.modal-footer');
    footer.innerHTML = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="rescheduleJob('${taskKey}')">Save</button>
    `;

    modal.classList.add('active');
}

async function rescheduleJob(taskKey) {
    const cron = document.getElementById('cronInput').value.trim();
    if (!cron) {
        showToast('Cron expression is required', 'error');
        return;
    }

    try {
        await apiPost(`/scheduler/jobs/${taskKey}/reschedule`, { cron });
        showToast(`Task "${taskKey}" rescheduled to "${cron}"`, 'success');
        closeModal();
        await refreshAll();
    } catch (err) {
        showToast(`Failed to reschedule: ${err.message}`, 'error');
    }
}

// Modal
function closeModal() {
    document.getElementById('taskModal').classList.remove('active');
}

// Toast Notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// Utilities
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
    // Auto-refresh every 30 seconds
    setInterval(refreshAll, 30000);
});

// Close modal on outside click
document.getElementById('taskModal').addEventListener('click', (e) => {
    if (e.target.id === 'taskModal') {
        closeModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});
