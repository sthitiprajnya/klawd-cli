function escapeHTML(str) {
    return str.replace(/[&<>'"]/g,
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

async function fetchData() {
    try {
        const [jobsRes, skillsRes] = await Promise.all([
            fetch('/api/v1/jobs'),
            fetch('/api/v1/skills')
        ]);

        const jobs = await jobsRes.json();
        const skills = await skillsRes.json();

        // Render Jobs safely mitigating XSS
        const jobsContainer = document.getElementById('jobs-container');
        if (Object.keys(jobs).length === 0) {
            jobsContainer.innerHTML = "<p style='color: var(--text-secondary);'>No active jobs. Queue is empty.</p>";
        } else {
            jobsContainer.innerHTML = Object.entries(jobs).map(([id, job]) => `
                <div class="job-item">
                    <div class="job-info">
                        <span class="job-id">ID: ${escapeHTML(id).substring(0,12)}</span>
                        <span class="job-task">${escapeHTML(job.task).substring(0, 60)}...</span>
                    </div>
                    <span class="status status-${escapeHTML(job.status)}">${escapeHTML(job.status)}</span>
                </div>
            `).join('');
        }

        // Render Skills
        document.getElementById('skills-container').textContent = JSON.stringify(skills.skills, null, 2);

    } catch (err) {
        console.error("Failed to fetch dashboard data", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchData();
    setInterval(fetchData, 3000);
});
