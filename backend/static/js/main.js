/**
 * STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
 * Interactive Client Scripts & Chart.js Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }

    // 2. Auto-dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // 3. Confirm Destructive Operations
    document.querySelectorAll('.confirm-action').forEach(el => {
        el.addEventListener('click', (e) => {
            const message = el.getAttribute('data-confirm-message') || 'Are you sure you want to proceed with this operation?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 4. Modal Population Handlers
    // Schedule Interview Modal
    const interviewModal = document.getElementById('scheduleInterviewModal');
    if (interviewModal) {
        interviewModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const appId = button.getAttribute('data-app-id');
            const studentName = button.getAttribute('data-student-name') || '';
            const jobTitle = button.getAttribute('data-job-title') || '';

            const form = interviewModal.querySelector('form');
            if (form && appId) {
                form.action = `/applications/${appId}/schedule-interview`;
            }
            const modalTitle = interviewModal.querySelector('.modal-candidate-info');
            if (modalTitle) {
                modalTitle.textContent = `${studentName} — ${jobTitle}`;
            }
        });
    }

    // Select Candidate & Offer Modal
    const selectModal = document.getElementById('selectCandidateModal');
    if (selectModal) {
        selectModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const appId = button.getAttribute('data-app-id');
            const studentName = button.getAttribute('data-student-name') || '';
            const jobTitle = button.getAttribute('data-job-title') || '';
            const defaultSalary = button.getAttribute('data-default-salary') || '';

            const form = selectModal.querySelector('form');
            if (form && appId) {
                form.action = `/applications/${appId}/select`;
            }
            const nameEl = selectModal.querySelector('.select-candidate-name');
            if (nameEl) nameEl.textContent = studentName;
            const jobEl = selectModal.querySelector('.select-job-title');
            if (jobEl) jobEl.textContent = jobTitle;
            const salaryInput = selectModal.querySelector('input[name="package_lpa"]');
            if (salaryInput && defaultSalary) {
                salaryInput.value = defaultSalary;
            }
        });
    }

    // 5. Initialize Charts (Only on pages where window.dashboardData exists)
    if (window.dashboardData && typeof Chart !== 'undefined') {
        initDashboardCharts(window.dashboardData);
    }

    // 6. Smooth Live Instant Search & Filtering
    initLiveFiltering();

    // 7. Form Submission Loading Spinners
    initFormLoadingFeedback();
});

/**
 * Modern Floating Toast Notification System
 * @param {string} message - Notification text
 * @param {string} type - 'success', 'danger', 'warning', 'info'
 * @param {string} title - Optional title
 */
window.showToast = function(message, type = 'info', title = '') {
    let container = document.querySelector('.spms-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'spms-toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `spms-toast spms-toast-${type}`;

    const iconMap = {
        success: 'fa-circle-check',
        danger: 'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info: 'fa-circle-info'
    };
    const iconClass = iconMap[type] || 'fa-bell';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass} spms-toast-icon"></i>
        <div style="flex: 1;">
            ${title ? `<strong style="display:block; font-size: 0.9rem; margin-bottom: 2px;">${title}</strong>` : ''}
            <span>${message}</span>
        </div>
        <button type="button" class="spms-toast-close" aria-label="Close">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    const closeBtn = toast.querySelector('.spms-toast-close');
    const dismiss = () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    };

    closeBtn.addEventListener('click', dismiss);
    setTimeout(dismiss, 5000);
};

/**
 * Real-time debounced table and card filtering
 */
function initLiveFiltering() {
    const searchInputs = document.querySelectorAll('input[type="text"][name="search"], .live-filter-input');
    
    searchInputs.forEach(input => {
        let debounceTimer;
        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = input.value.trim().toLowerCase();
                
                // 1. Filter standard tables on the page
                const table = document.querySelector('.table-custom tbody, .table tbody');
                if (table) {
                    const rows = table.querySelectorAll('tr');
                    let visibleCount = 0;
                    rows.forEach(row => {
                        const text = row.textContent.toLowerCase();
                        if (text.includes(query)) {
                            row.style.display = '';
                            row.classList.add('fade-in-item');
                            visibleCount++;
                        } else {
                            row.style.display = 'none';
                        }
                    });

                    // Empty row handler
                    let noMatchRow = table.querySelector('.no-match-row');
                    if (visibleCount === 0 && query.length > 0) {
                        if (!noMatchRow) {
                            noMatchRow = document.createElement('tr');
                            noMatchRow.className = 'no-match-row';
                            noMatchRow.innerHTML = `<td colspan="100%" class="text-center py-4 text-muted"><i class="fa-solid fa-magnifying-glass me-2"></i>No matching records found for "${input.value}"</td>`;
                            table.appendChild(noMatchRow);
                        }
                    } else if (noMatchRow) {
                        noMatchRow.remove();
                    }
                }

                // 2. Filter card grids (e.g., job cards, company cards)
                const cardGrid = document.querySelectorAll('.job-card, .company-card, .stats-card-filter');
                if (cardGrid.length > 0) {
                    cardGrid.forEach(card => {
                        const text = card.textContent.toLowerCase();
                        if (text.includes(query)) {
                            card.closest('.col-12, .col-md-6, .col-lg-4, .col-xl-3').style.display = '';
                        } else {
                            card.closest('.col-12, .col-md-6, .col-lg-4, .col-xl-3').style.display = 'none';
                        }
                    });
                }
            }, 120);
        });
    });
}

/**
 * Form Submit Button Loading Feedback
 */
function initFormLoadingFeedback() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]:not(.no-spin)');
            if (submitBtn && !submitBtn.disabled) {
                const originalHtml = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...`;
                // Allow fallback re-enable after 8 seconds in case of client cancel
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalHtml;
                }, 8000);
            }
        });
    });
}

/**
 * Initializes modern responsive dark-themed Chart.js visualizations
 */
function initDashboardCharts(data) {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

    // Common chart options
    const commonScales = {
        x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8' }
        },
        y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', stepSize: 1 },
            beginAtZero: true
        }
    };

    // Chart 1: Applications by Status (Doughnut)
    const statusCtx = document.getElementById('applicationsStatusChart');
    if (statusCtx && data.status_chart_data) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: data.status_chart_data.labels,
                datasets: [{
                    data: data.status_chart_data.values,
                    backgroundColor: [
                        '#06b6d4', // Applied - Cyan
                        '#a855f7', // Shortlisted - Purple
                        '#f59e0b', // Interview - Amber
                        '#10b981', // Selected - Emerald
                        '#ef4444', // Rejected - Red
                        '#64748b'  // Withdrawn - Slate
                    ],
                    borderColor: '#111827',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15 } }
                },
                cutout: '70%'
            }
        });
    }

    // Chart 2: Placements by Department (Bar)
    const deptCtx = document.getElementById('deptPlacementsChart');
    if (deptCtx && data.dept_chart_data) {
        new Chart(deptCtx, {
            type: 'bar',
            data: {
                labels: data.dept_chart_data.labels,
                datasets: [{
                    label: 'Students Placed',
                    data: data.dept_chart_data.values,
                    backgroundColor: '#6366f1',
                    borderRadius: 6,
                    maxBarThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: commonScales,
                plugins: { legend: { display: false } }
            }
        });
    }

    // Chart 3: Recruitment by Company (Horizontal Bar)
    const companyCtx = document.getElementById('companyHiresChart');
    if (companyCtx && data.company_chart_data) {
        new Chart(companyCtx, {
            type: 'bar',
            indexAxis: 'y',
            data: {
                labels: data.company_chart_data.labels,
                datasets: [{
                    label: 'Hires Count',
                    data: data.company_chart_data.values,
                    backgroundColor: '#10b981',
                    borderRadius: 6,
                    maxBarThickness: 24
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { stepSize: 1 },
                        beginAtZero: true
                    },
                    y: {
                        grid: { display: false }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // Chart 4: Placement Trends by Graduation Year (Line)
    const gradCtx = document.getElementById('gradYearTrendsChart');
    if (gradCtx && data.grad_chart_data) {
        new Chart(gradCtx, {
            type: 'line',
            data: {
                labels: data.grad_chart_data.labels,
                datasets: [{
                    label: 'Placed Students',
                    data: data.grad_chart_data.values,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointBackgroundColor: '#8b5cf6',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: commonScales,
                plugins: { legend: { display: false } }
            }
        });
    }
}
