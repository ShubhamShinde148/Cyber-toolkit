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

    // --- Animation Modes ---

    setMode(mode) {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        this.config.mode = mode || 'particles';
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Reset or initialize mode-specific data
        if (this.config.mode === 'matrix') {
            this.initMatrix();
        } else if (this.config.mode === 'hex') {
            this.initHex();
        } else if (this.config.mode === 'secure') {
            this.initSecureNode();
        }
        
        this.lastTime = performance.now();
        this.animate(performance.now());
    }

    initMatrix() {
        const fontSize = 16;
        const columns = Math.ceil(this.width / fontSize);
        this.matrixDrops = [];
        for (let i = 0; i < columns; i++) {
            this.matrixDrops[i] = Math.random() * -100;
        }
        this.matrixChars = "0101010101ABCDEFHIJKLMNOPQRSTUVWXYZ$#@%&*";
    }

    drawMatrix(deltaTime) {
        const timeScale = deltaTime / 16.67;
        const fontSize = 16;
        
        // Semitransparent clear for trail effect
        this.ctx.fillStyle = 'rgba(2, 11, 15, 0.15)';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.ctx.fillStyle = this.config.particleColor;
        this.ctx.font = fontSize + "px 'JetBrains Mono'";
        
        for (let i = 0; i < this.matrixDrops.length; i++) {
            const text = this.matrixChars.charAt(Math.floor(Math.random() * this.matrixChars.length));
            const x = i * fontSize;
            const y = this.matrixDrops[i] * fontSize;
            
            // Draw character
            this.ctx.fillText(text, x, y);
            
            // Increment drop Y
            if (y > this.height && Math.random() > 0.975) {
                this.matrixDrops[i] = 0;
            } else {
                this.matrixDrops[i] += 0.5 * timeScale;
            }
        }
    }

    initHex() {
        this.hexSize = 40;
        this.hexGlowPhase = 0;
    }

    drawHexGrid(deltaTime) {
        const timeScale = deltaTime / 16.67;
        this.hexGlowPhase += 0.02 * timeScale;
        
        this.ctx.fillStyle = this.config.backgroundColor;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        const a = this.hexSize / 2;
        const b = (Math.sqrt(3) * this.hexSize) / 2;
        const width = this.width;
        const height = this.height;
        
        this.ctx.strokeStyle = this.config.gridColor;
        this.ctx.lineWidth = 1;

        for (let y = 0; y < height + this.hexSize; y += b) {
            let xOffset = (Math.floor(y / b) % 2 === 0) ? 0 : this.hexSize * 0.75;
            for (let x = -this.hexSize; x < width + this.hexSize; x += this.hexSize * 1.5) {
                this.drawHexagon(x + xOffset, y);
            }
        }
        
        // Add moving pulse
        const pulseX = (Math.sin(this.hexGlowPhase * 0.5) * 0.5 + 0.5) * width;
        const pulseY = (Math.cos(this.hexGlowPhase * 0.3) * 0.5 + 0.5) * height;
        
        const gradient = this.ctx.createRadialGradient(pulseX, pulseY, 0, pulseX, pulseY, 300);
        gradient.addColorStop(0, this.config.lineColor);
        gradient.addColorStop(1, 'transparent');
        
        this.ctx.fillStyle = gradient;
        this.ctx.globalCompositeOperation = 'screen';
        this.ctx.fillRect(0, 0, width, height);
        this.ctx.globalCompositeOperation = 'source-over';
    }

    drawHexagon(x, y) {
        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = (Math.PI / 3) * i;
            this.ctx.lineTo(x + this.hexSize * Math.cos(angle), y + this.hexSize * Math.sin(angle));
        }
        this.ctx.closePath();
        this.ctx.stroke();
    }

    drawDarkGrid() {
        this.ctx.fillStyle = this.config.backgroundColor;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.drawGrid(); // Existing grid logic
        this.drawNavbarGlow();
        
        // Add moving horizon line for "vaporwave" cyber feel
        const time = Date.now() * 0.001;
        const horizonY = (time * 50) % this.height;
        
        this.ctx.strokeStyle = 'rgba(0, 255, 156, 0.1)';
        this.ctx.beginPath();
        this.ctx.moveTo(0, horizonY);
        this.ctx.lineTo(this.width, horizonY);
        this.ctx.stroke();
    }

    // --- Secure Node Mode ---
    initSecureNode() {
        this.particles.forEach((p, i) => {
            p.isSecure = i % 5 === 0; // Every 5th node is a secure lock node
            p.ip = this.generateIP();
            p.labelTimer = Math.random() * 100;
        });
    }

    generateIP() {
        return `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
    }

    drawSecureNode(deltaTime) {
        const timeScale = deltaTime / 16.67;
        
        // Background
        this.ctx.fillStyle = this.config.backgroundColor;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Blurred background effect (simulated with large faint circles)
        const time = Date.now() * 0.0005;
        for (let i = 0; i < 3; i++) {
            const bx = (Math.sin(time + i) * 0.5 + 0.5) * this.width;
            const by = (Math.cos(time * 0.7 + i) * 0.5 + 0.5) * this.height;
            const grad = this.ctx.createRadialGradient(bx, by, 0, bx, by, 400);
            grad.addColorStop(0, 'rgba(0, 255, 156, 0.03)');
            grad.addColorStop(1, 'transparent');
            this.ctx.fillStyle = grad;
            this.ctx.fillRect(bx - 400, by - 400, 800, 800);
        }

        // Draw Mesh Lines (Density increased)
        this.ctx.lineWidth = 0.5;
        for (let i = 0; i < this.particles.length; i++) {
            const p1 = this.particles[i];
            this.updateParticle(p1, deltaTime);

            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 180) { // Larger connection radius
                    const opacity = (1 - dist / 180) * 0.2;
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            }
        }

        // Draw Nodes
        this.particles.forEach(p => {
            // Draw node point
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.isSecure ? 15 : 2, 0, Math.PI * 2);
            this.ctx.fillStyle = p.isSecure ? 'rgba(255, 255, 255, 0.1)' : this.config.particleColor;
            this.ctx.fill();
            
            if (p.isSecure) {
                // Circle border
                this.ctx.strokeStyle = '#ffffff';
                this.ctx.lineWidth = 1.5;
                this.ctx.stroke();

                // Lock Icon (FontAwesome)
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = '900 14px "Font Awesome 6 Free"';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText('\uf023', p.x, p.y);
                
                // IP Address Label
                p.labelTimer += 0.05 * timeScale;
                const labelOpacity = Math.sin(p.labelTimer) * 0.3 + 0.4;
                this.ctx.fillStyle = `rgba(255, 255, 255, ${labelOpacity})`;
                this.ctx.font = '10px "JetBrains Mono"';
                this.ctx.fillText(p.ip, p.x, p.y + 25);
            }
        });
    }

    animate(currentTime) {
        if (!this.isRunning) return;

        this.animationId = requestAnimationFrame((time) => this.animate(time));

        const deltaTime = currentTime - this.lastTime;
        if (deltaTime < this.fpsInterval) return;
        this.lastTime = currentTime - (deltaTime % this.fpsInterval);

        // Routing based on mode
        switch (this.config.mode) {
            case 'matrix':
                this.drawMatrix(deltaTime);
                break;
            case 'hex':
                this.drawHexGrid(deltaTime);
                break;
            case 'grid':
                this.drawDarkGrid();
                break;
            case 'secure':
                this.drawSecureNode(deltaTime);
                break;
            default: // particles
                this.ctx.fillStyle = this.config.backgroundColor;
                this.ctx.fillRect(0, 0, this.width, this.height);
                this.drawGrid();
                this.drawNavbarGlow();
                this.drawDataStreams();
                this.drawLines();
                this.particles.forEach(particle => {
                    this.updateParticle(particle, deltaTime);
                    this.drawParticle(particle);
                });
        }
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
