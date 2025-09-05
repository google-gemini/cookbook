// static/main.js
document.addEventListener('DOMContentLoaded', () => {
    // --- API Interaction Logic ---
    const handleFormSubmit = async (event, formId, apiUrl, inputId, resultId) => {
        event.preventDefault();
        const inputElement = document.getElementById(inputId);
        const resultElement = document.getElementById(resultId);
        const submitButton = document.querySelector(`#${formId} button`);

        const payload = {
            prompt: inputElement.value
        };

        resultElement.textContent = 'Generating... The gears of domination are turning...';
        submitButton.disabled = true;

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            resultElement.textContent = data.result;

        } catch (error) {
            console.error('Error:', error);
            resultElement.textContent = 'An error occurred. The system faltered. Try again.';
        } finally {
            submitButton.disabled = false;
        }
    };

    document.getElementById('insta-essay-form').addEventListener('submit', (e) =>
        handleFormSubmit(e, 'insta-essay-form', '/api/insta-essay', 'essay-prompt', 'insta-essay-result')
    );

    document.getElementById('lit-review-form').addEventListener('submit', (e) =>
        handleFormSubmit(e, 'lit-review-form', '/api/lit-review', 'review-topic', 'lit-review-result')
    );

    document.getElementById('exam-cram-form').addEventListener('submit', (e) =>
        handleFormSubmit(e, 'exam-cram-form', '/api/exam-cram', 'exam-notes', 'exam-cram-result')
    );

    document.getElementById('presentation-bot-form').addEventListener('submit', (e) =>
        handleFormSubmit(e, 'presentation-bot-form', '/api/presentation-bot', 'presentation-topic', 'presentation-bot-result')
    );


    // --- Urgency Engine Logic ---
    const countdownElement = document.getElementById('countdown-timer');
    let timeLeft = 23 * 3600 + 59 * 60 + 59; // 23:59:59 in seconds

    setInterval(() => {
        if (timeLeft <= 0) {
            countdownElement.textContent = "00:00:00";
            return;
        }
        timeLeft--;
        const hours = Math.floor(timeLeft / 3600);
        const minutes = Math.floor((timeLeft % 3600) / 60);
        const seconds = timeLeft % 60;
        countdownElement.textContent =
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);

    const socialProofElement = document.getElementById('social-proof');
    const socialProofs = [
        "Sarah from Stanford just finished her thesis with us.",
        "Mike from MIT just crammed for his quantum physics exam.",
        "Chloe from Oxford just generated a presentation in 5 minutes.",
        "David from Harvard just aced his history essay.",
        "Emily from Yale just synthesized a literature review effortlessly."
    ];
    let proofIndex = 0;

    setInterval(() => {
        proofIndex = (proofIndex + 1) % socialProofs.length;
        socialProofElement.style.opacity = 0;
        setTimeout(() => {
            socialProofElement.textContent = socialProofs[proofIndex];
            socialProofElement.style.opacity = 1;
        }, 500); // fade in time
    }, 5000); // Change every 5 seconds
});
