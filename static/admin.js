// Admin Panel JavaScript Functions

// Create new API key
async function createApiKey() {
    const ownerName = document.getElementById('ownerName').value;
    const dailyLimit = document.getElementById('dailyLimit').value;
    const expiryDays = document.getElementById('expiryDays').value;
    
    if (!ownerName.trim()) {
        alert('Please enter owner name');
        return;
    }
    
    try {
        const response = await fetch('/admin/create_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                owner_name: ownerName,
                daily_limit: parseInt(dailyLimit),
                expiry_days: parseInt(expiryDays)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success message with API key
            alert(`API Key created successfully!\n\nAPI Key: ${data.api_key}\n\nPlease copy this key now, it won't be shown again.`);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createKeyModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('createKeyForm').reset();
            
            // Reload page to show new key
            window.location.reload();
        } else {
            alert('Error creating API key: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error occurred');
    }
}

// Delete API key
async function deleteApiKey(apiKey) {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/admin/delete_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                api_key: apiKey
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('API key deleted successfully');
            window.location.reload();
        } else {
            alert('Error deleting API key: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error occurred');
    }
}

// Copy API key to clipboard
async function copyApiKey(apiKey) {
    try {
        await navigator.clipboard.writeText(apiKey);
        
        // Show temporary success message
        const button = event.target.closest('button');
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-primary');
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-primary');
        }, 2000);
        
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = apiKey;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        alert('API key copied to clipboard');
    }
}

// Initialize usage analytics chart
function initializeUsageChart() {
    const ctx = document.getElementById('usageChart');
    if (!ctx) return;
    
    // Sample data for the chart
    const chartData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'API Requests',
            data: [120, 190, 300, 500, 200, 300, 450],
            backgroundColor: 'rgba(29, 185, 84, 0.1)',
            borderColor: '#1DB954',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };
    
    const config = {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#FFFFFF'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#FFFFFF'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#FFFFFF'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// Auto-refresh stats every 30 seconds
function autoRefreshStats() {
    setInterval(async () => {
        try {
            const response = await fetch('/admin/stats');
            if (response.ok) {
                const data = await response.json();
                
                // Update stats cards
                document.getElementById('totalKeys').textContent = data.total_keys || 0;
                document.getElementById('totalRequests').textContent = data.total_requests || 0;
                document.getElementById('activeUsers').textContent = data.active_users || 0;
                document.getElementById('revenue').textContent = `₹${data.revenue || 0}`;
            }
        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    }, 30000);
}

// Initialize all admin functions when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize usage chart
    initializeUsageChart();
    
    // Start auto-refresh
    autoRefreshStats();
    
    // Add event listeners for form submissions
    const createKeyForm = document.getElementById('createKeyForm');
    if (createKeyForm) {
        createKeyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createApiKey();
        });
    }
    
    // Add tooltips to buttons
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Search functionality for API keys table
function searchApiKeys() {
    const searchInput = document.getElementById('searchInput');
    const table = document.getElementById('apiKeysTable');
    const rows = table.getElementsByTagName('tr');
    
    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let match = false;
            
            for (let j = 0; j < cells.length; j++) {
                if (cells[j].textContent.toLowerCase().indexOf(filter) > -1) {
                    match = true;
                    break;
                }
            }
            
            row.style.display = match ? '' : 'none';
        }
    });
}

// Export API keys data to CSV
function exportApiKeys() {
    const table = document.getElementById('apiKeysTable');
    const rows = table.getElementsByTagName('tr');
    let csvContent = '';
    
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName(i === 0 ? 'th' : 'td');
        const rowData = [];
        
        for (let j = 0; j < cells.length - 1; j++) { // Exclude actions column
            rowData.push(cells[j].textContent.trim());
        }
        
        csvContent += rowData.join(',') + '\n';
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'api_keys_export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Real-time usage monitoring
function startRealtimeMonitoring() {
    const statusIndicator = document.getElementById('statusIndicator');
    
    setInterval(async () => {
        try {
            const response = await fetch('/admin/health');
            if (response.ok) {
                statusIndicator.className = 'status-indicator online';
                statusIndicator.textContent = 'Online';
            } else {
                statusIndicator.className = 'status-indicator offline';
                statusIndicator.textContent = 'Offline';
            }
        } catch (error) {
            statusIndicator.className = 'status-indicator offline';
            statusIndicator.textContent = 'Error';
        }
    }, 5000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+K to open create key modal
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('createKeyModal'));
        modal.show();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

// Theme toggle functionality
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Load saved theme
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', loadTheme);
