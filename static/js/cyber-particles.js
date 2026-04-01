/* ===================================
   Cyber Particles Animation System
   Dark Web Leak Monitor
   Advanced Canvas-Based Particle System
   =================================== */

class CyberParticleSystem {
    constructor(options = {}) {
        // Configuration with defaults
        this.config = {
            canvasId: options.canvasId || 'cyberCanvas',
            particleCount: options.particleCount || 80,
            particleColor: options.particleColor || '#00ff9c',
            lineColor: options.lineColor || 'rgba(0, 255, 156, 0.15)',
            backgroundColor: options.backgroundColor || '#020b0f',
            maxLineDistance: options.maxLineDistance || 120,
            particleMinSize: options.particleMinSize || 1,
            particleMaxSize: options.particleMaxSize || 3,
            baseSpeed: options.baseSpeed || 0.3,
            navbarAttractionStrength: options.navbarAttractionStrength || 0.02,
            mouseRadius: options.mouseRadius || 150,
            mouseRepelStrength: options.mouseRepelStrength || 0.8,
            gridSize: options.gridSize || 50,
            gridColor: options.gridColor || 'rgba(0, 255, 156, 0.04)',
            glowIntensity: options.glowIntensity || 15,
            enableGrid: options.enableGrid !== false,
            enableLines: options.enableLines !== false,
            enableMouseInteraction: options.enableMouseInteraction !== false,
            enableNavbarAttraction: options.enableNavbarAttraction !== false,
            enableParallax: options.enableParallax !== false
        };

        this.canvas = null;
        this.ctx = null;
        this.particles = [];
        this.mouse = { x: null, y: null, radius: this.config.mouseRadius };
        this.navbarY = 60; // Navbar height
        this.scrollY = 0;
        this.animationId = null;
        this.isRunning = false;
        this.lastTime = 0;
        this.fps = 60;
        this.fpsInterval = 1000 / this.fps;

        this.init();
    }

    init() {
        this.createCanvas();
        this.setupEventListeners();
        this.createParticles();
        this.start();
    }

    createCanvas() {
        // Check if canvas already exists
        this.canvas = document.getElementById(this.config.canvasId);
        
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.id = this.config.canvasId;
            this.canvas.classList.add('cyber-canvas');
            
            // Insert canvas into cyber-background container
            const container = document.querySelector('.cyber-background');
            if (container) {
                container.insertBefore(this.canvas, container.firstChild);
            } else {
                document.body.insertBefore(this.canvas, document.body.firstChild);
            }
        }

        this.ctx = this.canvas.getContext('2d');
        this.resize();
    }

    resize() {
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = window.innerWidth * dpr;
        this.canvas.height = window.innerHeight * dpr;
        this.canvas.style.width = window.innerWidth + 'px';
        this.canvas.style.height = window.innerHeight + 'px';
        this.ctx.scale(dpr, dpr);
        
        // Update actual dimensions for calculations
        this.width = window.innerWidth;
        this.height = window.innerHeight;
    }

    setupEventListeners() {
        // Resize handler with debouncing
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.resize();
                this.redistributeParticles();
            }, 100);
        });

        // Mouse movement
        if (this.config.enableMouseInteraction) {
            window.addEventListener('mousemove', (e) => {
                this.mouse.x = e.clientX;
                this.mouse.y = e.clientY;
            });

            window.addEventListener('mouseout', () => {
                this.mouse.x = null;
                this.mouse.y = null;
            });
        }

        // Scroll for parallax effect
        if (this.config.enableParallax) {
            window.addEventListener('scroll', () => {
                this.scrollY = window.scrollY;
            });
        }

        // Visibility change - pause when tab is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pause();
            } else {
                this.resume();
            }
        });
    }

    createParticles() {
        this.particles = [];
        
        for (let i = 0; i < this.config.particleCount; i++) {
            this.particles.push(this.createParticle());
        }
    }

    createParticle(x = null, y = null) {
        const size = Math.random() * (this.config.particleMaxSize - this.config.particleMinSize) + this.config.particleMinSize;
        
        return {
            x: x !== null ? x : Math.random() * this.width,
            y: y !== null ? y : Math.random() * this.height,
            size: size,
            baseSize: size,
            vx: (Math.random() - 0.5) * this.config.baseSpeed * 2,
            vy: (Math.random() - 0.5) * this.config.baseSpeed * 2,
            opacity: Math.random() * 0.5 + 0.5,
            pulsePhase: Math.random() * Math.PI * 2,
            pulseSpeed: Math.random() * 0.02 + 0.01,
            parallaxFactor: Math.random() * 0.3 + 0.1,
            glowIntensity: Math.random() * 0.5 + 0.5,
            hue: Math.random() * 20 - 10 // Slight color variation
        };
    }

    redistributeParticles() {
        this.particles.forEach(particle => {
            if (particle.x > this.width) particle.x = Math.random() * this.width;
            if (particle.y > this.height) particle.y = Math.random() * this.height;
        });
    }

    updateParticle(particle, deltaTime) {
        const timeScale = deltaTime / 16.67; // Normalize to 60fps

        // Pulse effect
        particle.pulsePhase += particle.pulseSpeed * timeScale;
        particle.size = particle.baseSize * (1 + Math.sin(particle.pulsePhase) * 0.3);
        particle.opacity = 0.5 + Math.sin(particle.pulsePhase) * 0.3;

        // Navbar attraction effect - particles slowly drift toward top
        if (this.config.enableNavbarAttraction) {
            const distanceToNav = particle.y - this.navbarY;
            if (distanceToNav > 0) {
                const attractionForce = this.config.navbarAttractionStrength * (1 - distanceToNav / this.height);
                particle.vy -= attractionForce * timeScale;
            }
        }

        // Mouse interaction (repel/attract based on proximity)
        if (this.config.enableMouseInteraction && this.mouse.x !== null && this.mouse.y !== null) {
            const dx = particle.x - this.mouse.x;
            const dy = particle.y - this.mouse.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.mouse.radius) {
                const force = (this.mouse.radius - distance) / this.mouse.radius;
                const angle = Math.atan2(dy, dx);
                particle.vx += Math.cos(angle) * force * this.config.mouseRepelStrength * timeScale;
                particle.vy += Math.sin(angle) * force * this.config.mouseRepelStrength * timeScale;
                
                // Increase glow when near mouse
                particle.glowIntensity = Math.min(1.5, particle.glowIntensity + 0.1);
            } else {
                particle.glowIntensity = Math.max(0.5, particle.glowIntensity - 0.02);
            }
        }

        // Apply velocity with damping
        particle.x += particle.vx * timeScale;
        particle.y += particle.vy * timeScale;
        
        // Damping
        particle.vx *= 0.99;
        particle.vy *= 0.99;

        // Ensure minimum movement
        if (Math.abs(particle.vx) < 0.1) {
            particle.vx = (Math.random() - 0.5) * this.config.baseSpeed;
        }
        if (Math.abs(particle.vy) < 0.1) {
            particle.vy = (Math.random() - 0.5) * this.config.baseSpeed;
        }

        // Boundary wrapping
        if (particle.x < -20) particle.x = this.width + 20;
        if (particle.x > this.width + 20) particle.x = -20;
        if (particle.y < -20) {
            // Respawn at bottom when reaching navbar
            particle.y = this.height + 20;
            particle.x = Math.random() * this.width;
        }
        if (particle.y > this.height + 20) particle.y = -20;
    }

    drawGrid() {
        if (!this.config.enableGrid) return;

        this.ctx.strokeStyle = this.config.gridColor;
        this.ctx.lineWidth = 1;

        // Apply parallax offset to grid
        const parallaxOffset = this.config.enableParallax ? this.scrollY * 0.1 : 0;

        // Vertical lines
        for (let x = 0; x <= this.width; x += this.config.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
            this.ctx.stroke();
        }

        // Horizontal lines with parallax
        for (let y = -this.config.gridSize; y <= this.height + this.config.gridSize; y += this.config.gridSize) {
            const adjustedY = (y + parallaxOffset) % (this.height + this.config.gridSize * 2);
            this.ctx.beginPath();
            this.ctx.moveTo(0, adjustedY);
            this.ctx.lineTo(this.width, adjustedY);
            this.ctx.stroke();
        }

        // Add perspective convergence lines (optional dramatic effect)
        this.drawPerspectiveGrid();
    }

    drawPerspectiveGrid() {
        const vanishingPointX = this.width / 2;
        const vanishingPointY = this.navbarY - 100;
        
        this.ctx.strokeStyle = 'rgba(0, 255, 156, 0.02)';
        this.ctx.lineWidth = 1;

        // Draw lines from bottom corners to vanishing point
        const numLines = 20;
        for (let i = 0; i <= numLines; i++) {
            const x = (this.width / numLines) * i;
            const gradient = this.ctx.createLinearGradient(x, this.height, vanishingPointX, vanishingPointY);
            gradient.addColorStop(0, 'rgba(0, 255, 156, 0.03)');
            gradient.addColorStop(1, 'rgba(0, 255, 156, 0)');
            
            this.ctx.strokeStyle = gradient;
            this.ctx.beginPath();
            this.ctx.moveTo(x, this.height);
            this.ctx.lineTo(vanishingPointX, vanishingPointY);
            this.ctx.stroke();
        }
    }

    drawParticle(particle) {
        const parallaxOffset = this.config.enableParallax ? this.scrollY * particle.parallaxFactor : 0;
        const drawX = particle.x;
        const drawY = particle.y + parallaxOffset;

        // Skip if particle is off-screen
        if (drawY < -50 || drawY > this.height + 50) return;

        // Create gradient for glow effect
        const gradient = this.ctx.createRadialGradient(
            drawX, drawY, 0,
            drawX, drawY, particle.size * this.config.glowIntensity * particle.glowIntensity
        );

        // Color with slight hue variation
        const baseHue = 156 + particle.hue;
        gradient.addColorStop(0, `hsla(${baseHue}, 100%, 60%, ${particle.opacity})`);
        gradient.addColorStop(0.3, `hsla(${baseHue}, 100%, 50%, ${particle.opacity * 0.5})`);
        gradient.addColorStop(1, `hsla(${baseHue}, 100%, 50%, 0)`);

        this.ctx.beginPath();
        this.ctx.arc(drawX, drawY, particle.size * this.config.glowIntensity * particle.glowIntensity, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();

        // Draw solid center
        this.ctx.beginPath();
        this.ctx.arc(drawX, drawY, particle.size, 0, Math.PI * 2);
        this.ctx.fillStyle = this.config.particleColor;
        this.ctx.fill();
    }

    drawLines() {
        if (!this.config.enableLines) return;

        const parallaxOffset = this.config.enableParallax ? this.scrollY * 0.1 : 0;

        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const p1 = this.particles[i];
                const p2 = this.particles[j];

                const dx = p1.x - p2.x;
                const dy = (p1.y + parallaxOffset * p1.parallaxFactor) - (p2.y + parallaxOffset * p2.parallaxFactor);
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.config.maxLineDistance) {
                    const opacity = (1 - distance / this.config.maxLineDistance) * 0.3;
                    
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(0, 255, 156, ${opacity})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.moveTo(p1.x, p1.y + parallaxOffset * p1.parallaxFactor);
                    this.ctx.lineTo(p2.x, p2.y + parallaxOffset * p2.parallaxFactor);
                    this.ctx.stroke();
                }
            }
        }

        // Draw lines between particles and mouse
        if (this.config.enableMouseInteraction && this.mouse.x !== null && this.mouse.y !== null) {
            this.particles.forEach(particle => {
                const dx = particle.x - this.mouse.x;
                const dy = (particle.y + parallaxOffset * particle.parallaxFactor) - this.mouse.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.mouse.radius) {
                    const opacity = (1 - distance / this.mouse.radius) * 0.4;
                    
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(0, 212, 255, ${opacity})`; // Cyan for mouse lines
                    this.ctx.lineWidth = 0.8;
                    this.ctx.moveTo(particle.x, particle.y + parallaxOffset * particle.parallaxFactor);
                    this.ctx.lineTo(this.mouse.x, this.mouse.y);
                    this.ctx.stroke();
                }
            });
        }
    }

    drawNavbarGlow() {
        // Create gradient representing particles reaching the navbar
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.navbarY + 50);
        gradient.addColorStop(0, 'rgba(0, 255, 156, 0.1)');
        gradient.addColorStop(0.5, 'rgba(0, 255, 156, 0.03)');
        gradient.addColorStop(1, 'rgba(0, 255, 156, 0)');

        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.width, this.navbarY + 50);

        // Accent glow at navbar line
        const lineGradient = this.ctx.createRadialGradient(
            this.width / 2, this.navbarY / 2, 0,
            this.width / 2, this.navbarY / 2, this.width / 2
        );
        lineGradient.addColorStop(0, 'rgba(0, 255, 156, 0.05)');
        lineGradient.addColorStop(1, 'rgba(0, 255, 156, 0)');

        this.ctx.fillStyle = lineGradient;
        this.ctx.fillRect(0, 0, this.width, this.navbarY);
    }

    drawDataStreams() {
        // Occasional data "packets" traveling to navbar
        const time = Date.now() * 0.001;
        const streamCount = 5;

        for (let i = 0; i < streamCount; i++) {
            const phase = (time + i * 1.5) % 4;
            if (phase < 3) {
                const progress = phase / 3;
                const startX = (this.width / (streamCount + 1)) * (i + 1);
                const startY = this.height;
                const endY = this.navbarY;
                
                const currentY = startY - (startY - endY) * this.easeInOutCubic(progress);
                const opacity = Math.sin(progress * Math.PI) * 0.3;

                // Draw packet
                const gradient = this.ctx.createRadialGradient(
                    startX, currentY, 0,
                    startX, currentY, 8
                );
                gradient.addColorStop(0, `rgba(0, 255, 156, ${opacity})`);
                gradient.addColorStop(1, 'rgba(0, 255, 156, 0)');

                this.ctx.beginPath();
                this.ctx.arc(startX, currentY, 4, 0, Math.PI * 2);
                this.ctx.fillStyle = gradient;
                this.ctx.fill();

                // Trail
                this.ctx.beginPath();
                this.ctx.strokeStyle = `rgba(0, 255, 156, ${opacity * 0.5})`;
                this.ctx.lineWidth = 1;
                this.ctx.moveTo(startX, currentY);
                this.ctx.lineTo(startX, currentY + 30);
                this.ctx.stroke();
            }
        }
    }

    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    animate(currentTime) {
        if (!this.isRunning) return;

        this.animationId = requestAnimationFrame((time) => this.animate(time));

        const deltaTime = currentTime - this.lastTime;
        
        // Limit frame rate for performance
        if (deltaTime < this.fpsInterval) return;
        
        this.lastTime = currentTime - (deltaTime % this.fpsInterval);

        // Clear canvas
        this.ctx.fillStyle = this.config.backgroundColor;
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Draw layers
        this.drawGrid();
        this.drawNavbarGlow();
        this.drawDataStreams();
        this.drawLines();
        
        // Update and draw particles
        this.particles.forEach(particle => {
            this.updateParticle(particle, deltaTime);
            this.drawParticle(particle);
        });
    }

    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.lastTime = performance.now();
        this.animate(performance.now());
    }

    pause() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    resume() {
        if (!this.isRunning) {
            this.start();
        }
    }

    destroy() {
        this.pause();
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }

    // API Methods for external control
    setParticleCount(count) {
        this.config.particleCount = count;
        this.createParticles();
    }

    setMouseRadius(radius) {
        this.mouse.radius = radius;
        this.config.mouseRadius = radius;
    }

    setNavbarAttraction(strength) {
        this.config.navbarAttractionStrength = strength;
    }

    toggleGrid(enabled) {
        this.config.enableGrid = enabled;
    }

    toggleLines(enabled) {
        this.config.enableLines = enabled;
    }

    toggleParallax(enabled) {
        this.config.enableParallax = enabled;
    }
}

// Initialize the particle system when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we should initialize (avoid on pages that shouldn't have it)
    const cyberBackground = document.querySelector('.cyber-background');
    
    if (cyberBackground) {
        // Initialize with custom settings
        window.cyberParticles = new CyberParticleSystem({
            particleCount: 80,
            particleColor: '#00ff9c',
            backgroundColor: '#020b0f',
            maxLineDistance: 120,
            particleMinSize: 1,
            particleMaxSize: 3,
            baseSpeed: 0.3,
            navbarAttractionStrength: 0.015,
            mouseRadius: 150,
            mouseRepelStrength: 0.6,
            gridSize: 50,
            glowIntensity: 12,
            enableGrid: true,
            enableLines: true,
            enableMouseInteraction: true,
            enableNavbarAttraction: true,
            enableParallax: true
        });

        // Performance optimization: reduce effects on low-end devices
        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
            window.cyberParticles.setParticleCount(40);
            window.cyberParticles.toggleLines(false);
        }

        // Reduce particle count on mobile for better performance
        if (window.innerWidth < 768) {
            window.cyberParticles.setParticleCount(40);
            window.cyberParticles.config.maxLineDistance = 80;
        }
    }
});

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CyberParticleSystem;
}
