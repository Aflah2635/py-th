// Cyberpunk Glitch Animation Handler

class GlitchAnimationHandler {
    constructor() {
        this.overlay = null;
        this.audioContext = null;
        this.oscillator = null;
        this.gainNode = null;
        this.setupAudio();
    }

    setupAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.gainNode = this.audioContext.createGain();
            this.gainNode.connect(this.audioContext.destination);
            this.gainNode.gain.value = 0.1; // Set initial volume
        } catch (e) {
            console.warn('Audio context not supported');
        }
    }

    createGlitchOverlay(rank) {
        // Create overlay container
        this.overlay = document.createElement('div');
        this.overlay.className = `glitch-overlay rank-${rank}`;
        
        // Create content container
        const content = document.createElement('div');
        content.className = 'glitch-content';

        // Set rank-specific content
        const titles = {
            1: '🏆 YOU ARE #1 – GLORY UNLOCKED',
            2: '🥈 2nd Place – NEON EDGE FINISH',
            3: '🥉 3rd Place – CYBER SURVIVOR',
            4: '4th Place – DIGITAL RUNNER'
        };

        // Add title
        const title = document.createElement('div');
        title.className = 'glitch-title';
        title.textContent = titles[rank] || 'CYBER FINISH';
        content.appendChild(title);

        // Add rank display
        const rankDisplay = document.createElement('div');
        rankDisplay.className = 'glitch-rank';
        rankDisplay.textContent = `RANK #${rank}`;
        content.appendChild(rankDisplay);

        // Add scanlines
        const scanlines = document.createElement('div');
        scanlines.className = 'scanlines';

        // Append elements
        this.overlay.appendChild(content);
        this.overlay.appendChild(scanlines);
        document.body.appendChild(this.overlay);
    }

    playGlitchSound() {
        if (!this.audioContext) return;

        try {
            // Create and configure oscillator
            this.oscillator = this.audioContext.createOscillator();
            this.oscillator.type = 'sawtooth';
            this.oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime);

            // Connect oscillator to gain node
            this.oscillator.connect(this.gainNode);

            // Start oscillator
            this.oscillator.start();

            // Create glitch effect
            this.oscillator.frequency.linearRampToValueAtTime(
                880,
                this.audioContext.currentTime + 0.1
            );

            // Stop after short duration
            setTimeout(() => {
                this.oscillator.stop();
                this.oscillator.disconnect();
            }, 150);
        } catch (e) {
            console.warn('Error playing glitch sound:', e);
        }
    }

    async showAnimation(rank) {
        if (rank > 4) return false; // Only show for top 4

        this.createGlitchOverlay(rank);
        await this.playGlitchSound();

        // Add overlay to DOM and force reflow
        document.body.appendChild(this.overlay);
        this.overlay.offsetHeight;

        // Activate overlay with enhanced timing
        requestAnimationFrame(() => {
            this.overlay.classList.add('active');
        });

        // Return promise that resolves when animation completes
        return new Promise(resolve => {
            setTimeout(() => {
                if (this.overlay) {
                    this.overlay.classList.remove('active');
                    // Wait for fade out transition
                    setTimeout(() => {
                        this.overlay.remove();
                        resolve();
                    }, 300);
                } else {
                    resolve();
                }
            }, 3000); // Animation duration
        });
    }
}

// Initialize handler
const glitchAnimation = new GlitchAnimationHandler();

// Export for use in other modules
window.glitchAnimation = glitchAnimation;