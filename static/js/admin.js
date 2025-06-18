// Admin Dashboard JavaScript
class AdminDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startRealTimeUpdates();
        this.setupNotifications();
    }

    setupEventListeners() {
        // Sidebar toggle for mobile
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', this.toggleSidebar);
        }

        // Search functionality
        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleGlobalSearch);
        }

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme);
        }

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', this.toggleAutoRefresh);
        }
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    }

    handleGlobalSearch(event) {
        const query = event.target.value.toLowerCase();
        const searchResults = document.getElementById('searchResults');
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }

        // Simulate search results
        const results = [
            { type: 'user', title: 'Nguyễn Văn A', url: '/admin/users?search=' + query },
            { type: 'food', title: 'Phở bò', url: '/food?search=' + query },
            { type: 'setting', title: 'AI Configuration', url: '/admin/settings#ai-settings' }
        ].filter(item => item.title.toLowerCase().includes(query));

        this.displaySearchResults(results);
    }

    displaySearchResults(results) {
        const searchResults = document.getElementById('searchResults');
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="p-3 text-muted">Không tìm thấy kết quả</div>';
        } else {
            searchResults.innerHTML = results.map(result => `
                <a href="${result.url}" class="dropdown-item">
                    <i class="fas fa-${this.getIconForType(result.type)} me-2"></i>
                    ${result.title}
                </a>
            `).join('');
        }
        
        searchResults.style.display = 'block';
    }

    getIconForType(type) {
        const icons = {
            user: 'user',
            food: 'hamburger',
            setting: 'cog',
            report: 'chart-bar'
        };
        return icons[type] || 'search';
    }

    toggleTheme() {
        const body = document.body;
        const isDark = body.classList.toggle('dark-theme');
        
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        
        // Update charts if they exist
        if (window.Chart) {
            Chart.defaults.color = isDark ? '#ffffff' : '#666666';
            Chart.defaults.borderColor = isDark ? '#404040' : '#e0e0e0';
        }
    }

    toggleAutoRefresh(event) {
        const enabled = event.target.checked;
        
        if (enabled) {
            this.autoRefreshInterval = setInterval(() => {
                this.refreshDashboardData();
            }, 30000); // Refresh every 30 seconds
        } else {
            clearInterval(this.autoRefreshInterval);
        }
        
        localStorage.setItem('autoRefresh', enabled);
    }

    initializeCharts() {
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js is not loaded. Skipping chart initialization.');
            return;
        }

        // Initialize charts with responsive options
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.plugins.legend.position = 'top';
        Chart.defaults.plugins.tooltip.mode = 'index';
        Chart.defaults.plugins.tooltip.intersect = false;
    }

    startRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            this.updateSystemStatus();
            this.updateNotificationCount();
        }, 10000); // Update every 10 seconds
    }

    updateSystemStatus() {
        const statusIndicators = document.querySelectorAll('.status-indicator');
        
        statusIndicators.forEach(indicator => {
            // Simulate status changes
            const isOnline = Math.random() > 0.1; // 90% uptime
            
            indicator.classList.remove('bg-success', 'bg-danger', 'bg-warning');
            indicator.classList.add(isOnline ? 'bg-success' : 'bg-danger');
        });
    }

    updateNotificationCount() {
        const notificationBadge = document.getElementById('notificationCount');
        if (notificationBadge) {
            const count = Math.floor(Math.random() * 5);
            notificationBadge.textContent = count;
            notificationBadge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    setupNotifications() {
        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    showNotification(title, message, type = 'info') {
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/img/logo.png'
            });
        }

        // In-app notification
        this.showToast(title, message, type);
    }

    showToast(title, message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    refreshDashboardData() {
        // Show loading state
        const refreshButton = document.querySelector('[onclick="refreshStats()"]');
        if (refreshButton) {
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang tải...';
            refreshButton.disabled = true;
        }

        // Simulate API call
        setTimeout(() => {
            // Update stats
            this.updateStats();
            
            // Reset button
            if (refreshButton) {
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Làm mới';
                refreshButton.disabled = false;
            }
            
            this.showToast('Cập nhật', 'Dữ liệu đã được cập nhật', 'success');
        }, 1500);
    }

    updateStats() {
        // Update stat cards with animation
        const statCards = document.querySelectorAll('.stat-card .h5');
        
        statCards.forEach(card => {
            const currentValue = parseInt(card.textContent) || 0;
            const newValue = currentValue + Math.floor(Math.random() * 10);
            
            this.animateNumber(card, currentValue, newValue);
        });
    }

    animateNumber(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    // Export functionality
    exportData(type, format = 'csv') {
        const data = this.getExportData(type);
        
        if (format === 'csv') {
            this.downloadCSV(data, `${type}_export_${new Date().toISOString().split('T')[0]}.csv`);
        } else if (format === 'json') {
            this.downloadJSON(data, `${type}_export_${new Date().toISOString().split('T')[0]}.json`);
        }
    }

    getExportData(type) {
        // Simulate data export
        switch (type) {
            case 'users':
                return [
                    { id: 1, name: 'Nguyễn Văn A', email: 'user1@example.com', created: '2024-01-01' },
                    { id: 2, name: 'Trần Thị B', email: 'user2@example.com', created: '2024-01-02' }
                ];
            case 'foods':
                return [
                    { id: 1, name: 'Phở bò', calories: 350, protein: 20, created: '2024-01-01' },
                    { id: 2, name: 'Cơm gà', calories: 450, protein: 25, created: '2024-01-02' }
                ];
            default:
                return [];
        }
    }

    downloadCSV(data, filename) {
        if (data.length === 0) return;
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
        ].join('\n');
        
        this.downloadFile(csvContent, filename, 'text/csv');
    }

    downloadJSON(data, filename) {
        const jsonContent = JSON.stringify(data, null, 2);
        this.downloadFile(jsonContent, filename, 'application/json');
    }

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
    
    // Load saved preferences
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
    
    const autoRefresh = localStorage.getItem('autoRefresh') === 'true';
    const autoRefreshToggle = document.getElementById('autoRefresh');
    if (autoRefreshToggle) {
        autoRefreshToggle.checked = autoRefresh;
        if (autoRefresh) {
            autoRefreshToggle.dispatchEvent(new Event('change'));
        }
    }
});

// Global functions for backward compatibility
function refreshStats() {
    window.adminDashboard.refreshDashboardData();
}

function exportReport() {
    window.adminDashboard.exportData('report', 'csv');
}
