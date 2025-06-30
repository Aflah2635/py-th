// WebSocket connection for real-time updates
let leaderboardSocket = null;

// Sorting state
let currentSort = {
    column: 'score',
    direction: 'desc'
};

// Initialize the leaderboard
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sorting controls
    document.querySelectorAll('.sort-control').forEach(button => {
        button.addEventListener('click', function() {
            const column = this.dataset.column;
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'desc' ? 'asc' : 'desc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'desc';
            }
            
            // Update active state
            document.querySelectorAll('.sort-control').forEach(btn => {
                btn.classList.remove('active', 'asc', 'desc');
            });
            this.classList.add('active', currentSort.direction);
            
            // Request updated data
            if (leaderboardSocket && leaderboardSocket.readyState === WebSocket.OPEN) {
                leaderboardSocket.send(JSON.stringify({
                    type: 'sort_request',
                    column: currentSort.column,
                    direction: currentSort.direction
                }));
            }
        });
    });

    // Initialize visibility toggle for admin
    const visibilityToggle = document.getElementById('visibility-toggle');
    if (visibilityToggle) {
        visibilityToggle.addEventListener('change', function() {
            if (leaderboardSocket && leaderboardSocket.readyState === WebSocket.OPEN) {
                leaderboardSocket.send(JSON.stringify({
                    type: 'visibility_toggle',
                    visible: this.checked
                }));
            }
        });
    }

    // Connect WebSocket
    connectWebSocket();
});

// Connect to WebSocket
function connectWebSocket() {
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsScheme}://${window.location.host}/ws/game/leaderboard/`;
    
    leaderboardSocket = new WebSocket(wsUrl);
    
    leaderboardSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'leaderboard_update') {
            updateLeaderboard(data.leaderboard);
        }
    };

    leaderboardSocket.onclose = function() {
        console.log('WebSocket disconnected. Attempting to reconnect...');
        setTimeout(connectWebSocket, 1000);
    };
}

// Sort leaderboard data
function sortLeaderboard(data, column) {
    return data.sort((a, b) => {
        let comparison = 0;
        switch (column) {
            case 'score':
                comparison = b.score - a.score;
                break;
            case 'accuracy':
                const aAcc = calculateAccuracy(a);
                const bAcc = calculateAccuracy(b);
                comparison = bAcc - aAcc;
                break;
            case 'progress':
                comparison = (b.completed_questions / b.total_questions) - 
                            (a.completed_questions / a.total_questions);
                break;
            case 'time':
                if (!a.finish_time) return 1;
                if (!b.finish_time) return -1;
                comparison = new Date(a.finish_time) - new Date(a.finish_time);
                break;
        }
        return currentSort.direction === 'desc' ? comparison : -comparison;
    });
}

// Calculate accuracy percentage
function calculateAccuracy(player) {
    if (!player.total_attempts) return 0;
    return Math.round((player.correct_attempts / player.total_attempts) * 100);
}

// Format duration for display
function formatDuration(duration) {
    const parts = duration.split(':');
    if (parts.length === 3) {
        const [hours, minutes, seconds] = parts;
        if (hours !== '00') {
            return `${parseInt(hours)}h ${parseInt(minutes)}m ${parseInt(seconds)}s`;
        }
        return `${parseInt(minutes)}m ${parseInt(seconds)}s`;
    }
    return duration;
}

// Update leaderboard display with animation
function updateLeaderboard(data) {
    const container = document.getElementById('leaderboard-container');
    const sortedData = sortLeaderboard(data, currentSort.column);
    
    // Store current positions for animation
    const currentEntries = container.querySelectorAll('.leaderboard-entry');
    const currentPositions = new Map();
    currentEntries.forEach(entry => {
        const playerId = entry.dataset.playerId;
        currentPositions.set(playerId, entry.getBoundingClientRect().top);
    });

    // Update DOM
    container.innerHTML = sortedData.map((player, index) => {
        const rank = index + 1;
        return `
            <div class="leaderboard-entry rank-${rank}" data-player-id="${player.user.id}">
                <div class="rank-info">
                    <div class="rank-badge">${rank}</div>
                    <div class="player-info">
                        <div class="username">
                            ${rank <= 3 ? `<div class="crown rank-${rank}"></div>` : ''}
                            ${player.user.username}
                        </div>
                        ${player.finish_time ? '<div class="status">Mission Complete</div>' : ''}
                    </div>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Score</span>
                        <span class="stat-value">${player.score} pts</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Progress</span>
                        <span class="stat-value">${player.completed_questions.count}/${player.total_questions}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Hints Used</span>
                        <span class="stat-value">${player.total_hints_used}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Accuracy</span>
                        <span class="stat-value">${calculateAccuracy(player)}%</span>
                    </div>
                    ${player.finish_time ? `
                    <div class="stat-item col-span-2">
                        <span class="stat-label">Time</span>
                        <span class="stat-value">${formatDuration(player.finish_time)}</span>
                    </div>
                    ` : ''}
                </div>
                ${player.is_staff ? `
                <button class="view-stats-btn" onclick="viewFullStats(${player.user.id})">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                </button>
                ` : ''}
            </div>
        `;
    }).join('');

    // Animate position changes
    const newEntries = container.querySelectorAll('.leaderboard-entry');
    newEntries.forEach(entry => {
        const playerId = entry.dataset.playerId;
        const oldPosition = currentPositions.get(playerId);
        if (oldPosition) {
            const newPosition = entry.getBoundingClientRect().top;
            const distance = oldPosition - newPosition;
            
            if (distance) {
                // Trigger animation
                entry.style.transform = `translateY(${distance}px)`;
                entry.style.transition = 'none';
                
                requestAnimationFrame(() => {
                    entry.style.transition = 'transform 0.5s ease-out';
                    entry.style.transform = 'translateY(0)';
                });
            }
        } else {
            // New entry animation
            entry.style.opacity = '0';
            entry.style.transform = 'translateX(-20px)';
            
            requestAnimationFrame(() => {
                entry.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                entry.style.opacity = '1';
                entry.style.transform = 'translateX(0)';
            });
        }
    });
}

// View full stats modal (for admin)
function viewFullStats(userId) {
    if (leaderboardSocket && leaderboardSocket.readyState === WebSocket.OPEN) {
        leaderboardSocket.send(JSON.stringify({
            type: 'stats_request',
            user_id: userId
        }));
    }
}


// Helper functions
function getCrownIcon(rank) {
    const colors = {
        1: '#FFD700',
        2: '#C0C0C0',
        3: '#CD7F32'
    };
    return `<svg class="crown-icon" fill="${colors[rank]}" viewBox="0 0 24 24" width="24" height="24">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>`;
}

function formatDuration(duration) {
    return duration.split('.')[0]; // Remove milliseconds
}

function calculateAccuracy(player) {
    if (!player.total_attempts) return 0;
    return Math.round((player.correct_attempts / player.total_attempts) * 100);
}

// Initialize sorting controls
function initializeSortControls() {
    const controls = document.querySelectorAll('.sort-control');
    controls.forEach(control => {
        control.addEventListener('click', () => {
            const column = control.dataset.column;
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'desc' ? 'asc' : 'desc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'desc';
            }
            
            // Update sort indicators
            controls.forEach(c => c.classList.remove('sort-asc', 'sort-desc'));
            control.classList.add(`sort-${currentSort.direction}`);
            
            // Request updated data
            if (leaderboardSocket && leaderboardSocket.readyState === WebSocket.OPEN) {
                leaderboardSocket.send(JSON.stringify({
                    type: 'request_update',
                    sort: currentSort
                }));
            }
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    initializeSortControls();
});