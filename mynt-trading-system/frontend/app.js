console.log('App.js loaded - Trading System');

// ========================================
// CONFIGURATION
// ========================================
const API_BASE = 'http://localhost:8000';

// ========================================
// STATE
// ========================================
const state = {
    token: null,
    user: null,
    sessionExpiry: null,
    sessionTimer: null,
    charts: {
        pnl: null,
        distribution: null
    }
};

// ========================================
// DOM HELPERS
// ========================================
const $ = (id) => document.getElementById(id);

// ========================================
// UTILITY FUNCTIONS
// ========================================
function formatDate(date) {
    if (!date) return '--';
    try {
        return new Date(date).toLocaleString('en-IN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (e) {
        return date;
    }
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) return '₹0.00';
    return '₹' + Number(amount).toFixed(2);
}

function getTimeRemaining(expiry) {
    const now = Date.now();
    const diff = expiry - now;
    if (diff <= 0) return 'Expired';
    const minutes = Math.floor(diff / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function showLoading() {
    const overlay = $('loadingOverlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = $('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const page = $(pageId);
    if (page) page.classList.add('active');
}

function showLoginStatus(type, message) {
    const status = $('loginStatus');
    if (status) {
        status.className = 'login-status ' + type;
        status.textContent = message;
    }
}

// ========================================
// API FUNCTIONS
// ========================================
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    const data = await response.json();
    
    if (response.status === 401) {
        handleSessionExpired();
        throw new Error('Session expired');
    }
    
    if (!response.ok) {
        throw new Error(data.message || data.detail || 'Request failed');
    }
    
    return data;
}

// ========================================
// AUTHENTICATION
// ========================================
function handleLogin() {
    window.location.href = `${API_BASE}/auth/login`;
}

async function handleCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    console.log('Callback code found:', code);
    
    if (!code) {
        console.log('No code found in URL');
        return;
    }
    
    showLoading();
    showLoginStatus('info', 'Processing login...');
    
    try {
        const response = await fetch(`${API_BASE}/callback?code=${code}`);
        const data = await response.json();
        
        console.log('Callback response:', data);
        
        if (data.success) {
            // Store token and user info
            state.token = data.access_token;
            state.user = {
                username: data.username,
                full_name: data.full_name || data.username,
                status: data.status || 'Active'
            };
            
            // Save to localStorage
            localStorage.setItem('token', state.token);
            localStorage.setItem('user', JSON.stringify(state.user));
            
            // Set session expiry
            state.sessionExpiry = Date.now() + (30 * 60 * 1000);
            localStorage.setItem('sessionExpiry', state.sessionExpiry.toString());
            
            showLoginStatus('success', 'Login successful! Redirecting...');
            showToast(`Welcome ${state.user.full_name}!`, 'success');
            
            // Load dashboard and redirect
            try {
                await loadDashboard();
                showPage('dashboardPage');
                startSessionTimer();
                
                // Clear URL parameters
                window.history.replaceState({}, document.title, window.location.pathname);
                console.log('Dashboard loaded successfully!');
            } catch (dashboardError) {
                console.error('Dashboard load error:', dashboardError);
                showToast('Error loading dashboard: ' + dashboardError.message, 'error');
            }
        } else {
            showLoginStatus('error', 'Login failed: ' + (data.message || 'Unknown error'));
            showToast('Login failed: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showLoginStatus('error', 'Login failed: ' + error.message);
        showToast('Login failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function handleSessionExpired() {
    state.token = null;
    state.user = null;
    state.sessionExpiry = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionExpiry');
    if (state.sessionTimer) {
        clearInterval(state.sessionTimer);
        state.sessionTimer = null;
    }
    showPage('loginPage');
    showLoginStatus('error', 'Session expired. Please login again.');
}

function startSessionTimer() {
    if (state.sessionTimer) {
        clearInterval(state.sessionTimer);
    }
    
    state.sessionTimer = setInterval(() => {
        if (state.sessionExpiry) {
            const remaining = getTimeRemaining(state.sessionExpiry);
            const sessionTime = $('sessionTime');
            if (sessionTime) {
                sessionTime.textContent = `Session: ${remaining}`;
            }
            if (remaining === 'Expired') {
                handleSessionExpired();
            }
        }
        updateTimeDisplay();
    }, 1000);
}

function updateTimeDisplay() {
    const now = new Date();
    const dateDisplay = $('currentDate');
    const timeDisplay = $('currentTimeDisplay');
    
    if (dateDisplay) {
        dateDisplay.textContent = now.toLocaleDateString('en-IN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
    if (timeDisplay) {
        timeDisplay.textContent = now.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

// ========================================
// DASHBOARD
// ========================================
async function loadDashboard() {
    try {
        showLoading();
        
        const user = state.user || {};
        
        // Update user info
        const fullName = $('userFullName');
        const username = $('userUsername');
        const userNameDisplay = $('userNameDisplay');
        
        if (fullName) fullName.textContent = user.full_name || 'User';
        if (username) username.textContent = user.username || '--';
        if (userNameDisplay) userNameDisplay.textContent = user.full_name || user.username || '--';
        
        // Update status badges
        const userStatusBadge = $('userStatusBadge');
        if (userStatusBadge) {
            userStatusBadge.textContent = user.status || 'Active';
            userStatusBadge.className = `badge badge-${user.status === 'Active' ? 'success' : 'danger'}`;
        }
        
        // Get dashboard data
        const data = await apiRequest('/api/dashboard/dashboard-data');
        console.log('Dashboard data:', data);
        
        // Update account status
        const accountStatusDisplay = $('accountStatusDisplay');
        const accountStatusBadge = $('accountStatusBadge');
        if (accountStatusDisplay) accountStatusDisplay.textContent = data.account?.status || 'Active';
        if (accountStatusBadge) {
            accountStatusBadge.textContent = data.account?.status || 'Active';
            accountStatusBadge.className = `badge badge-${data.account?.status === 'Active' ? 'success' : 'danger'}`;
        }
        
        // Update balance
        const balanceDisplay = $('availableBalance');
        if (balanceDisplay) {
            balanceDisplay.textContent = formatCurrency(data.account?.balance || 0);
        }
        
        // Update market status
        const marketStatusDisplay = $('marketStatusDisplay');
        const marketStatusBadge = $('marketStatusBadge');
        if (marketStatusDisplay) marketStatusDisplay.textContent = data.market?.status || 'Closed';
        if (marketStatusBadge) {
            marketStatusBadge.textContent = data.market?.status || 'Closed';
            marketStatusBadge.className = `badge badge-${data.market?.status === 'Open' ? 'success' : 'danger'}`;
        }
        
        // Update statistics
        const totalTrades = $('totalTrades');
        const netPnl = $('netPnl');
        const openTrades = $('openTrades');
        const winRate = $('winRate');
        
        if (totalTrades) totalTrades.textContent = data.statistics?.total_trades || 0;
        
        const pnl = data.statistics?.net_pnl || 0;
        if (netPnl) {
            netPnl.textContent = formatCurrency(pnl);
            netPnl.style.color = pnl >= 0 ? '#28a745' : '#dc3545';
        }
        
        if (openTrades) openTrades.textContent = data.statistics?.open_trades || 0;
        if (winRate) winRate.textContent = `${data.statistics?.win_rate || 0}%`;
        
        // Update session expiry
        if (!state.sessionExpiry) {
            state.sessionExpiry = Date.now() + (30 * 60 * 1000);
        }
        
        // Update time display
        updateTimeDisplay();
        
        return true;
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        if (error.message === 'Session expired') {
            handleSessionExpired();
        } else {
            showToast('Failed to load dashboard: ' + error.message, 'error');
        }
        return false;
    } finally {
        hideLoading();
    }
}

// ========================================
// QUICK ACTIONS
// ========================================
async function downloadData() {
    showLoading();
    try {
        const data = await apiRequest('/historical/download');
        if (data.success) {
            showToast('Data downloaded successfully!', 'success');
            await loadDashboard();
        } else {
            showToast('Download failed: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        showToast('Download failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function runStrategy() {
    showLoading();
    try {
        const data = await apiRequest('/strategy/run', { method: 'POST' });
        if (data.success) {
            showToast(`Strategy completed! ${data.signals_found || 0} signals found.`, 'success');
            await loadDashboard();
        } else {
            showToast('Strategy failed: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        showToast('Strategy failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function runBacktest() {
    showLoading();
    try {
        const data = await apiRequest('/api/strategy/run', { method: 'POST' });
        if (data.success) {
            showBacktestResults(data);
            showToast('Backtest completed successfully!', 'success');
            await loadDashboard();
        } else {
            showToast('Backtest failed: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        showToast('Backtest failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function viewTrades() {
    showLoading();
    try {
        const data = await apiRequest('/api/dashboard/trades');
        const tradesSection = $('tradesSection');
        if (data.trades && data.trades.length > 0) {
            showAllTradesTable(data.trades);
            tradesSection.style.display = 'block';
            showToast(`Loaded ${data.trades.length} trades`, 'success');
        } else {
            showToast('No trades found', 'info');
        }
    } catch (error) {
        showToast('Failed to load trades: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function viewAnalytics() {
    showLoading();
    try {
        const analyticsSection = $('analyticsSection');
        analyticsSection.style.display = 'block';
        
        const data = await apiRequest('/api/dashboard/trades');
        if (data.trades && data.trades.length > 0) {
            createCharts(data.trades);
            showToast('Analytics loaded successfully!', 'success');
        } else {
            showToast('No data available for analytics', 'info');
        }
    } catch (error) {
        showToast('Failed to load analytics: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// ========================================
// CHARTS
// ========================================
function createCharts(trades) {
    const closedTrades = trades.filter(t => t.trade_status === 'CLOSED');
    const pnlData = closedTrades.map(t => t.net_pnl || 0);
    const labels = closedTrades.map((t, i) => `Trade ${i + 1}`);
    
    // P&L Chart
    const pnlCtx = document.getElementById('pnlChart');
    if (pnlCtx) {
        if (state.charts.pnl) {
            state.charts.pnl.destroy();
        }
        state.charts.pnl = new Chart(pnlCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'P&L per Trade',
                    data: pnlData,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Distribution Chart
    const distCtx = document.getElementById('distributionChart');
    if (distCtx) {
        if (state.charts.distribution) {
            state.charts.distribution.destroy();
        }
        
        const winningTrades = closedTrades.filter(t => (t.net_pnl || 0) > 0);
        const losingTrades = closedTrades.filter(t => (t.net_pnl || 0) < 0);
        const breakEvenTrades = closedTrades.filter(t => (t.net_pnl || 0) === 0);
        
        state.charts.distribution = new Chart(distCtx, {
            type: 'doughnut',
            data: {
                labels: ['Winning Trades', 'Losing Trades', 'Break Even'],
                datasets: [{
                    data: [winningTrades.length, losingTrades.length, breakEvenTrades.length],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function closeTrades() {
    const tradesSection = $('tradesSection');
    if (tradesSection) tradesSection.style.display = 'none';
}

// ========================================
// BACKTEST RESULTS
// ========================================
function showBacktestResults(data) {
    const backtestResults = $('backtestResults');
    backtestResults.style.display = 'block';
    
    const header = document.querySelector('#backtestResults .card-header h3');
    if (header) {
        header.innerHTML = '<i class="fas fa-chart-line"></i> Backtest Results';
    }
    
    const summary = $('backtestSummary');
    if (data.summary && summary) {
        const s = data.summary;
        summary.innerHTML = `
            <div class="summary-item">
                <span class="label">Total Trades</span>
                <span class="value">${s.total_trades || 0}</span>
            </div>
            <div class="summary-item">
                <span class="label">Win Rate</span>
                <span class="value">${s.win_rate || 0}%</span>
            </div>
            <div class="summary-item">
                <span class="label">Net Profit</span>
                <span class="value ${(s.net_profit || 0) >= 0 ? 'positive' : 'negative'}">
                    ${formatCurrency(s.net_profit || 0)}
                </span>
            </div>
            <div class="summary-item">
                <span class="label">Avg Profit</span>
                <span class="value ${(s.avg_profit || 0) >= 0 ? 'positive' : 'negative'}">
                    ${formatCurrency(s.avg_profit || 0)}
                </span>
            </div>
            <div class="summary-item">
                <span class="label">Max Profit</span>
                <span class="value positive">${formatCurrency(s.max_profit || 0)}</span>
            </div>
            <div class="summary-item">
                <span class="label">Max Loss</span>
                <span class="value negative">${formatCurrency(s.max_loss || 0)}</span>
            </div>
        `;
    }
    
    if (data.trades && data.trades.length > 0) {
        showTradesTable(data.trades);
    }
}

function showTradesTable(trades) {
    const tradesTable = $('tradesTable');
    if (!tradesTable) return;
    
    if (!trades || trades.length === 0) {
        tradesTable.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No trades found</p>';
        return;
    }
    
    let html = `
        <table class="trades-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Symbol</th>
                    <th>Entry Time</th>
                    <th>Entry Price</th>
                    <th>Exit Time</th>
                    <th>Exit Price</th>
                    <th>P&L</th>
                    <th>Status</th>
                    <th>Exit Reason</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    const displayTrades = trades.slice(0, 50);
    displayTrades.forEach(trade => {
        const pnl = trade.net_pnl || 0;
        const pnlClass = pnl >= 0 ? 'positive' : 'negative';
        
        html += `
            <tr>
                <td><small>${(trade.trade_id || '').substring(0, 8)}</small></td>
                <td>${trade.symbol || 'NIFTY'}</td>
                <td>${formatDate(trade.entry_time)}</td>
                <td>${formatCurrency(trade.entry_price)}</td>
                <td>${trade.exit_time ? formatDate(trade.exit_time) : '-'}</td>
                <td>${trade.exit_price ? formatCurrency(trade.exit_price) : '-'}</td>
                <td class="${pnlClass}">${formatCurrency(pnl)}</td>
                <td><span class="status-${(trade.trade_status || 'OPEN').toLowerCase()}">${trade.trade_status || 'OPEN'}</span></td>
                <td><small>${trade.exit_reason || '-'}</small></td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        ${trades.length > 50 ? `<p style="margin-top: 12px; color: #6c757d; font-size: 13px;">Showing 50 of ${trades.length} trades</p>` : ''}
    `;
    
    tradesTable.innerHTML = html;
}

function showAllTradesTable(trades) {
    const tradesTable = $('allTradesTable');
    if (!tradesTable) return;
    
    if (!trades || trades.length === 0) {
        tradesTable.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No trades found</p>';
        return;
    }
    
    let html = `
        <table class="trades-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Symbol</th>
                    <th>Strategy</th>
                    <th>Entry Time</th>
                    <th>Entry Price</th>
                    <th>Exit Time</th>
                    <th>Exit Price</th>
                    <th>P&L</th>
                    <th>Status</th>
                    <th>Exit Reason</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    trades.forEach(trade => {
        const pnl = trade.net_pnl || 0;
        const pnlClass = pnl >= 0 ? 'positive' : 'negative';
        
        html += `
            <tr>
                <td><small>${(trade.trade_id || '').substring(0, 8)}</small></td>
                <td>${trade.symbol || 'NIFTY'}</td>
                <td>${trade.strategy_name || '--'}</td>
                <td>${formatDate(trade.entry_time)}</td>
                <td>${formatCurrency(trade.entry_price)}</td>
                <td>${trade.exit_time ? formatDate(trade.exit_time) : '-'}</td>
                <td>${trade.exit_price ? formatCurrency(trade.exit_price) : '-'}</td>
                <td class="${pnlClass}">${formatCurrency(pnl)}</td>
                <td><span class="status-${(trade.trade_status || 'OPEN').toLowerCase()}">${trade.trade_status || 'OPEN'}</span></td>
                <td><small>${trade.exit_reason || '-'}</small></td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        <p style="margin-top: 12px; color: #6c757d; font-size: 13px;">Total: ${trades.length} trades</p>
    `;
    
    tradesTable.innerHTML = html;
}

function closeBacktest() {
    const backtestResults = $('backtestResults');
    if (backtestResults) backtestResults.style.display = 'none';
}

// ========================================
// LOGOUT
// ========================================
async function handleLogout() {
    if (!confirm('Are you sure you want to logout?')) return;
    
    showLoading();
    try {
        await apiRequest('/auth/logout', { method: 'POST' });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        state.token = null;
        state.user = null;
        state.sessionExpiry = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('sessionExpiry');
        
        if (state.sessionTimer) {
            clearInterval(state.sessionTimer);
            state.sessionTimer = null;
        }
        
        if (state.charts.pnl) {
            state.charts.pnl.destroy();
            state.charts.pnl = null;
        }
        if (state.charts.distribution) {
            state.charts.distribution.destroy();
            state.charts.distribution = null;
        }
        
        showPage('loginPage');
        showLoginStatus('info', 'Logged out successfully');
        hideLoading();
        showToast('Logged out successfully', 'info');
    }
}

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Trading System...');
    
    const loginBtn = document.getElementById('loginButton');
    if (loginBtn) {
        loginBtn.addEventListener('click', handleLogin);
    }
    
    const logoutBtn = document.getElementById('logoutButton');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
        console.log('Found OAuth code, handling callback...');
        handleCallback();
        return;
    }
    
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    const expiryStr = localStorage.getItem('sessionExpiry');
    
    if (token && userStr && expiryStr) {
        const expiry = parseInt(expiryStr);
        if (expiry > Date.now()) {
            state.token = token;
            state.user = JSON.parse(userStr);
            state.sessionExpiry = expiry;
            console.log('Restoring session for user:', state.user);
            loadDashboard().then(() => {
                showPage('dashboardPage');
                startSessionTimer();
                showToast('Welcome back!', 'info');
            });
            return;
        }
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionExpiry');
    showPage('loginPage');
    console.log('Showing login page');
});

// Make functions globally accessible
window.downloadData = downloadData;
window.runStrategy = runStrategy;
window.runBacktest = runBacktest;
window.viewTrades = viewTrades;
window.viewAnalytics = viewAnalytics;
window.closeBacktest = closeBacktest;
window.closeTrades = closeTrades;

console.log('App.js initialization complete');