function escapeHTML(str) {
    return String(str).replace(/[&<>'"]/g,
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

function renderJobs(jobs) {
    const jobsContainer = document.getElementById('jobs-container');
    if (!jobs || jobs.length === 0) {
        jobsContainer.innerHTML = "<p style='color: var(--text-secondary);'>No active jobs. Queue is empty.</p>";
        return;
    }
    jobsContainer.innerHTML = jobs.map((job) => `
        <div class="job-item" data-job-id="${escapeHTML(job.job_id)}">
            <div class="job-info">
                <span class="job-id">ID: ${escapeHTML(job.job_id).substring(0,12)}</span>
                <span class="job-task">${escapeHTML(job.task).substring(0, 60)}...</span>
            </div>
            <span class="status status-${escapeHTML(job.status)}">${escapeHTML(job.status)}</span>
        </div>
    `).join('');
}

async function fetchData() {
    try {
        const [jobsRes, skillsRes] = await Promise.all([fetch('/api/v1/jobs'), fetch('/api/v1/skills')]);
        const jobsPayload = await jobsRes.json();
        const skills = await skillsRes.json();
        renderJobs(jobsPayload.jobs || []);
        document.getElementById('skills-container').textContent = JSON.stringify(skills.skills, null, 2);
    } catch (err) {
        console.error('Failed to fetch dashboard data', err);
    }
}

function connectJobStream() {
    const wsProto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${wsProto}://${window.location.host}/ws/jobs`);
    ws.onmessage = (event) => {
        try {
            const frame = JSON.parse(event.data);
            if (frame.type !== 'job_update' || !frame.job_id || !frame.status) return;
            fetchData();
        } catch (e) {
            console.warn('Invalid websocket frame', e);
        }
    };
    ws.onclose = () => setTimeout(connectJobStream, 2000);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    connectJobStream();
    setInterval(fetchData, 5000);
});
