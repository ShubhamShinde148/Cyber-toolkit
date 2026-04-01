/**
 * Certificate Page - Animations, QR Code, Export
 */
document.addEventListener('DOMContentLoaded', function () {

    /* ---- Score Ring Animation ---- */
    const ring = document.querySelector('.ring-fill');
    if (ring) {
        const pct = parseFloat(ring.dataset.percent) || 0;
        const r = 50;
        const C = 2 * Math.PI * r;
        ring.style.strokeDasharray = C;
        ring.style.strokeDashoffset = C;
        setTimeout(() => { ring.style.strokeDashoffset = C - (pct / 100) * C; }, 400);
    }

    /* ---- QR Code Generation ---- */
    const qrEl = document.getElementById('certQR');
    if (qrEl && typeof QRCode !== 'undefined') {
        const url = qrEl.dataset.url;
        new QRCode(qrEl, {
            text: url,
            width: 64,
            height: 64,
            colorDark: '#050A0F',
            colorLight: '#ffffff',
        });
    }

    /* ---- Send Certificate via Email ---- */
    const emailBtn = document.getElementById('sendEmail');
    if (emailBtn) {
        emailBtn.addEventListener('click', async () => {
            const certId = emailBtn.dataset.id;
            let userEmail = emailBtn.dataset.email;

            if (!userEmail || userEmail === 'None' || userEmail === '') {
                userEmail = prompt("Please enter your email address:");
                if (!userEmail) return;
                emailBtn.dataset.email = userEmail;
            }

            emailBtn.disabled = true;
            emailBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            try {
                const response = await fetch('/api/certificate/send-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        certificate_id: certId,
                        email: userEmail
                    })
                });

                const result = await response.json();
                if (result.success) {
                    if (typeof showToast === 'function') showToast('Certificate sent successfully!', 'success');
                    else alert('Success: Certificate has been sent to ' + userEmail);
                } else {
                    throw new Error(result.error || 'Failed to send email');
                }
            } catch (e) {
                console.error('Email error:', e);
                if (typeof showToast === 'function') showToast(e.message, 'error');
                else alert('Error: ' + e.message);
            }

            emailBtn.disabled = false;
            emailBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Mail';
        });
    }

    /* ---- Download as PDF (html2canvas + jsPDF) ---- */
    const pdfBtn = document.getElementById('downloadPDF');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', async () => {
            pdfBtn.disabled = true;
            pdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            try {
                const card = document.querySelector('.cert-card');
                const canvas = await html2canvas(card, {
                    backgroundColor: '#050A0F',
                    scale: 2,
                    useCORS: true,
                    logging: false
                });
                const { jsPDF } = window.jspdf;
                const imgW = canvas.width;
                const imgH = canvas.height;
                const pdfW = imgW * 0.264583;
                const pdfH = imgH * 0.264583;
                const pdf = new jsPDF({ orientation: pdfW > pdfH ? 'l' : 'p', unit: 'mm', format: [pdfW, pdfH] });
                pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, pdfW, pdfH);
                const name = document.getElementById('certUserName')?.textContent?.trim() || 'certificate';
                pdf.save(`cybersecurity_certificate_${name.replace(/\s+/g, '_')}.pdf`);
            } catch (e) {
                if (typeof showToast === 'function') showToast('PDF generation failed', 'error');
                else alert('PDF generation failed');
            }
            pdfBtn.disabled = false;
            pdfBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Download PDF';
        });
    }

    /* ---- Download as PNG ---- */
    const pngBtn = document.getElementById('downloadPNG');
    if (pngBtn) {
        pngBtn.addEventListener('click', async () => {
            pngBtn.disabled = true;
            pngBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            try {
                const card = document.querySelector('.cert-card');
                const canvas = await html2canvas(card, {
                    backgroundColor: '#050A0F',
                    scale: 2,
                    useCORS: true,
                    logging: false
                });
                const link = document.createElement('a');
                link.download = `cybersecurity_certificate_${(document.getElementById('certUserName')?.textContent?.trim() || 'cert').replace(/\s+/g, '_')}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();
            } catch (e) {
                if (typeof showToast === 'function') showToast('PNG generation failed', 'error');
                else alert('PNG generation failed');
            }
            pngBtn.disabled = false;
            pngBtn.innerHTML = '<i class="fas fa-image"></i> Download PNG';
        });
    }

    /* ---- Share Certificate ---- */
    const shareBtn = document.getElementById('shareCert');
    if (shareBtn) {
        shareBtn.addEventListener('click', async () => {
            const url = shareBtn.dataset.url || window.location.href;
            if (navigator.share) {
                try {
                    await navigator.share({ title: 'Cybersecurity Awareness Certificate', text: 'I earned my Cybersecurity Awareness Certificate from Dark Web Monitor!', url: url });
                } catch (_) { /* user cancelled */ }
            } else {
                await navigator.clipboard.writeText(url);
                if (typeof showToast === 'function') showToast('Certificate link copied!', 'success');
                else alert('Certificate link copied!');
            }
        });
    }

    /* ---- Number Counter Animation ---- */
    document.querySelectorAll('[data-count-to]').forEach(el => {
        const target = parseInt(el.dataset.countTo);
        const suffix = el.dataset.countSuffix || '';
        let current = 0;
        const duration = 1200;
        const start = performance.now();
        function tick(now) {
            const p = Math.min((now - start) / duration, 1);
            current = Math.floor(target * p);
            el.textContent = current + suffix;
            if (p < 1) requestAnimationFrame(tick);
            else el.textContent = target + suffix;
        }
        requestAnimationFrame(tick);
    });
});
