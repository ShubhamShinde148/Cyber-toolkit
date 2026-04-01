/**
 * Learning Mode – client-side logic
 * Handles: progress tracking, topic card clicks, modal rendering,
 *          daily topic, AI Q&A, and mark-complete flow.
 */
(function () {
    'use strict';

    // ===== Local-storage progress =====
    const STORAGE_KEY = 'lm_completed_topics';

    function getCompleted() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; }
        catch { return []; }
    }
    function saveCompleted(arr) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
    }
    function isCompleted(topicId) {
        return getCompleted().includes(topicId);
    }
    function markTopicCompleted(topicId) {
        const arr = getCompleted();
        if (!arr.includes(topicId)) { arr.push(topicId); saveCompleted(arr); }
    }

    // ===== DOM refs =====
    const totalCountEl      = document.getElementById('totalCount');
    const completedCountEl  = document.getElementById('completedCount');
    const progressFill      = document.getElementById('progressFill');
    const currentLevelBadge = document.getElementById('currentLevelBadge');
    const dailyTopicBody    = document.getElementById('dailyTopicBody');
    const refreshDailyBtn   = document.getElementById('refreshDailyBtn');

    const topicModal        = document.getElementById('topicModal');
    const modalTopicTitle   = document.getElementById('modalTopicTitle');
    const modalBody         = document.getElementById('modalBody');
    const modalClose        = document.getElementById('modalClose');
    const markCompleteBtn   = document.getElementById('markCompleteBtn');

    const aiAskModal        = document.getElementById('aiAskModal');
    const aiAskClose        = document.getElementById('aiAskClose');
    const aiQuestionInput   = document.getElementById('aiQuestionInput');
    const aiAskSubmit       = document.getElementById('aiAskSubmit');
    const aiAnswerBox       = document.getElementById('aiAnswerBox');

    let activeTopic = null; // { id, level, title }

    // ===== Progress UI =====
    function refreshProgress() {
        const cards = document.querySelectorAll('.lm-topic-card');
        const total = cards.length;
        const completed = getCompleted();
        let count = 0;
        cards.forEach(c => {
            if (completed.includes(c.dataset.topicId)) {
                c.classList.add('completed');
                count++;
            } else {
                c.classList.remove('completed');
            }
        });
        if (totalCountEl) totalCountEl.textContent = total;
        if (completedCountEl) completedCountEl.textContent = count;
        const pct = total ? Math.round((count / total) * 100) : 0;
        if (progressFill) progressFill.style.width = pct + '%';

        // Current level badge
        if (currentLevelBadge) {
            if (count >= 13) currentLevelBadge.textContent = 'Advanced';
            else if (count >= 7) currentLevelBadge.textContent = 'Intermediate';
            else currentLevelBadge.textContent = 'Beginner';
        }
    }

    // ===== Daily Topic =====
    function loadDailyTopic() {
        dailyTopicBody.innerHTML = '<div class="lm-loader"><div class="spinner"></div> Loading daily topic…</div>';
        fetch('/api/learning/daily-topic', { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    dailyTopicBody.innerHTML = '<p style="color:#ff5252">' + escapeHtml(data.error) + '</p>';
                    return;
                }
                dailyTopicBody.innerHTML =
                    '<div class="lm-daily-title">' + escapeHtml(data.title || 'Cybersecurity Tip') + '</div>' +
                    '<div class="lm-daily-summary">' + escapeHtml(data.summary || '') + '</div>' +
                    (data.fun_fact ? '<div class="lm-daily-fact">💡 ' + escapeHtml(data.fun_fact) + '</div>' : '') +
                    (data.difficulty ? '<div class="lm-daily-diff"><span class="lm-badge lm-badge-' + escapeHtml(data.difficulty) + '">' + escapeHtml(data.difficulty) + '</span></div>' : '');
            })
            .catch(() => {
                dailyTopicBody.innerHTML = '<p style="color:#ff5252">Failed to load daily topic.</p>';
            });
    }

    if (refreshDailyBtn) refreshDailyBtn.addEventListener('click', loadDailyTopic);

    // ===== Topic Modal =====
    function openTopicModal(topicId, level, title) {
        activeTopic = { id: topicId, level: level, title: title };
        modalTopicTitle.textContent = title;
        modalBody.innerHTML = '<div class="lm-loader"><div class="spinner"></div> Generating AI content…</div>';
        topicModal.classList.add('active');
        markCompleteBtn.disabled = false;

        fetch('/api/learning/topic-content', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: title, difficulty: level })
        })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                modalBody.innerHTML = '<p style="color:#ff5252">' + escapeHtml(data.error) + '</p>';
                return;
            }
            renderTopicContent(data);
        })
        .catch(() => {
            modalBody.innerHTML = '<p style="color:#ff5252">Failed to generate content.</p>';
        });
    }

    function renderTopicContent(d) {
        let html = '';

        // Explanation
        html += '<div class="lm-section">' +
            '<div class="lm-section-title"><i class="fas fa-info-circle"></i> Explanation</div>' +
            '<div class="lm-explanation">' + escapeHtml(d.explanation || '') + '</div></div>';

        // Tools
        if (d.tools && d.tools.length) {
            html += '<div class="lm-section"><div class="lm-section-title"><i class="fas fa-wrench"></i> Tools to Learn</div><ul class="lm-tools-list">';
            d.tools.forEach(t => { html += '<li>' + escapeHtml(t) + '</li>'; });
            html += '</ul></div>';
        }

        // Practice
        if (d.practice) {
            html += '<div class="lm-section"><div class="lm-section-title"><i class="fas fa-flask"></i> Practice Exercise</div>' +
                '<div class="lm-practice-box">' + escapeHtml(d.practice) + '</div></div>';
        }

        // Quick Notes
        if (d.quick_notes && d.quick_notes.length) {
            html += '<div class="lm-section"><div class="lm-section-title"><i class="fas fa-sticky-note"></i> Quick Notes</div><ul class="lm-notes-list">';
            d.quick_notes.forEach(n => { html += '<li>' + escapeHtml(n) + '</li>'; });
            html += '</ul></div>';
        }

        // Steps
        if (d.steps && d.steps.length) {
            html += '<div class="lm-section"><div class="lm-section-title"><i class="fas fa-list-ol"></i> Step-by-Step Guide</div><ul class="lm-steps-list">';
            d.steps.forEach(s => { html += '<li>' + escapeHtml(s) + '</li>'; });
            html += '</ul></div>';
        }

        // Ask AI button
        html += '<button class="btn btn-sm btn-outline lm-ask-btn" id="openAiAskBtn"><i class="fas fa-robot"></i> Ask AI about this topic</button>';

        modalBody.innerHTML = html;

        document.getElementById('openAiAskBtn').addEventListener('click', () => {
            aiAnswerBox.textContent = '';
            aiQuestionInput.value = '';
            aiAskModal.classList.add('active');
        });
    }

    function closeTopicModal() { topicModal.classList.remove('active'); activeTopic = null; }
    if (modalClose) modalClose.addEventListener('click', closeTopicModal);
    topicModal.addEventListener('click', e => { if (e.target === topicModal) closeTopicModal(); });

    // Mark complete
    if (markCompleteBtn) markCompleteBtn.addEventListener('click', () => {
        if (!activeTopic) return;
        markTopicCompleted(activeTopic.id);
        refreshProgress();
        closeTopicModal();
    });

    // ===== AI Ask Modal =====
    function closeAiAsk() { aiAskModal.classList.remove('active'); }
    if (aiAskClose) aiAskClose.addEventListener('click', closeAiAsk);
    aiAskModal.addEventListener('click', e => { if (e.target === aiAskModal) closeAiAsk(); });

    if (aiAskSubmit) aiAskSubmit.addEventListener('click', submitAiQuestion);
    if (aiQuestionInput) aiQuestionInput.addEventListener('keydown', e => { if (e.key === 'Enter') submitAiQuestion(); });

    function submitAiQuestion() {
        const q = aiQuestionInput.value.trim();
        if (!q || !activeTopic) return;
        aiAnswerBox.innerHTML = '<div class="lm-loader"><div class="spinner"></div> Thinking…</div>';
        aiAskSubmit.disabled = true;

        fetch('/api/learning/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: activeTopic.title, question: q })
        })
        .then(r => r.json())
        .then(data => {
            aiAskSubmit.disabled = false;
            if (data.error) {
                aiAnswerBox.innerHTML = '<p style="color:#ff5252">' + escapeHtml(data.error) + '</p>';
            } else {
                aiAnswerBox.textContent = data.answer || 'No answer received.';
            }
        })
        .catch(() => {
            aiAskSubmit.disabled = false;
            aiAnswerBox.innerHTML = '<p style="color:#ff5252">Request failed.</p>';
        });
    }

    // ===== Wire up Start Learning buttons =====
    document.querySelectorAll('.lm-start-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            openTopicModal(btn.dataset.topicId, btn.dataset.level, btn.dataset.title);
        });
    });

    // Also allow clicking the card itself
    document.querySelectorAll('.lm-topic-card').forEach(card => {
        card.addEventListener('click', e => {
            if (e.target.closest('.lm-start-btn')) return; // already handled
            openTopicModal(card.dataset.topicId, card.dataset.level, card.dataset.title);
        });
    });

    // ===== Utility =====
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // ===== Init =====
    refreshProgress();
    loadDailyTopic();
})();
