/* ═══════════════════════════════════════════════════════════
   KLARA OS — Patient / User Dashboard Logic
   ═══════════════════════════════════════════════════════════ */
(function() {
    'use strict';
    const form = document.getElementById('user-form');
    const input = document.getElementById('user-input');
    const submitBtn = document.getElementById('user-submit');
    const welcomeView = document.getElementById('welcome-view');
    const resultsView = document.getElementById('results-view');
    const backBtn = document.getElementById('back-btn');

    // Button states
    input.addEventListener('input', () => {
        submitBtn.disabled = input.value.trim() === '';
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // Loading and resetting state
        submitBtn.disabled = true;
        document.querySelector('.btn-go-label').hidden = true;
        document.querySelector('.btn-go-loader').hidden = false;
        document.getElementById('emergency-banner').hidden = true;

        try {
            const res = await fetch('/assess', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, region: document.getElementById('region-value').value })
            });

            if (!res.ok) throw new Error(`Server error`);
            const data = await res.json();

            // Populate view
            document.getElementById('result-pathway').innerText = data.routing_recommendation.primary_pathway;
            document.getElementById('result-reason').innerText = data.routing_recommendation.reason;
            
            const optionsList = document.getElementById('options-list');
            optionsList.innerHTML = data.routing_recommendation.options.map(o => `<li>${o}</li>`).join('');
            
            document.getElementById('summary-body').innerHTML = `
                <p><strong>Symptoms:</strong> ${data.structured_summary.symptoms}</p>
                <p><strong>Duration:</strong> ${data.structured_summary.duration}</p>
                <p><strong>Risk Level:</strong> ${data.structured_summary.risk}</p>
            `;

            if (data.risk_assessment.level === 'high') {
                const banner = document.getElementById('emergency-banner');
                banner.hidden = false;
                document.getElementById('emergency-text').innerText = 'Please seek immediate medical attention.';
            }

            // Swap views smoothly with staggered animations
            welcomeView.classList.add('view-fade-out');
            
            setTimeout(() => {
                welcomeView.classList.add('view-hidden');
                welcomeView.classList.remove('view-fade-out');
                
                // Reset animation classes on results so they play again
                resultsView.querySelectorAll('.animate-up').forEach(el => {
                    el.style.animation = 'none';
                    el.offsetHeight; // Trigger reflow
                    el.style.animation = null;
                });

                resultsView.classList.remove('view-hidden');
            }, 400); // 400ms matches CSS fadeOut duration
            
        } catch (e) {
            alert('Error processing request.');
            console.error(e);
        } finally {
            submitBtn.disabled = false;
            document.querySelector('.btn-go-label').hidden = false;
            document.querySelector('.btn-go-loader').hidden = true;
        }
    });

    backBtn.addEventListener('click', () => {
        resultsView.classList.add('view-fade-out');

        setTimeout(() => {
            resultsView.classList.add('view-hidden');
            resultsView.classList.remove('view-fade-out');

            // Reset welcome animations
            welcomeView.querySelectorAll('.animate-up').forEach(el => {
                el.style.animation = 'none';
                el.offsetHeight;
                el.style.animation = null;
            });

            welcomeView.classList.remove('view-hidden');
            input.value = '';
            submitBtn.disabled = true;
        }, 400);
    });
})();
