const API_BASE_URL = 'https://spokenspoon.onrender.com';

let sessionId = localStorage.getItem("session_id");

if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("session_id", sessionId);
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log("loading.js started");
    const errorMessage = document.getElementById('errorMessage');
    const loadingMessage = document.getElementById('loadingMessage');
    const progressFill = document.getElementById('progressFill');
    const quitButton = document.getElementById('quitButton');
    const recipeUrl = sessionStorage.getItem('pendingRecipeURL');
    console.log("pendingRecipeURL:", recipeUrl);

    let abortController = null;
    let isAborted = false;

    if (!recipeUrl) {
        window.location.href = 'index.html';
        return;
    }

    sessionStorage.removeItem('pendingRecipeURL');
    sessionStorage.setItem('originalRecipeURL', recipeUrl);

    quitButton.addEventListener('click', async () => {
        isAborted = true;
        quitButton.disabled = true;
        quitButton.textContent = 'Quitting...';

        if (abortController) {
            abortController.abort();
        }

        fetch(`${API_BASE_URL}/cancel`, { method: 'POST' }).catch(err => {
            console.log("Cancel endpoint failed (this is okay):", err.message);
        });

        window.location.href = 'index.html';
    });

    try {
        abortController = new AbortController();
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: recipeUrl,
                session_id: sessionId
            }),
            signal: abortController.signal
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                // Track which event type the next data line belongs to
                if (line.startsWith('event: ')) {
                    currentEvent = line.slice(7).trim();
                }

                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));

                    if (currentEvent === 'progress') {
                        const stepPercentages = {
                            0: 0,
                            1: 5,
                            2: 10,
                            3: 20,
                            4: 40,
                            5: 60,
                            6: 70,
                            7: 80
                        };
                        const percent = stepPercentages[data.step - 1] || 100;
                        if (progressFill) progressFill.style.width = `${percent}%`;
                        if (loadingMessage) loadingMessage.textContent = `${percent}% complete. ${data.message}`;
                    }

                    if (currentEvent === 'cancelled') {
                        window.location.href = 'index.html';
                        return;
                    }

                    if (currentEvent === 'complete') {
                        let htmlContent = data.html;

                        if (htmlContent.startsWith('```html')) {
                            htmlContent = htmlContent.replace(/^```html\n/, '').replace(/\n```$/, '');
                        }

                        sessionStorage.setItem('recipeHTML', htmlContent);

                        if (data.record_id) {
                            sessionStorage.setItem('recipeRecordId', data.record_id);
                        }

                        window.location.href = 'output.html';
                        return;
                    }

                    if (currentEvent === 'error') {
                        throw new Error(data.message);
                    }

                    currentEvent = '';
                }
            }
        }

    } catch (error) {
        if (error.name === 'AbortError' || isAborted) {
            console.log("Request was aborted by user");
            return;
        }

        console.log("fetch failed:", error.message);
        if (errorMessage) {
            errorMessage.hidden = false;
            errorMessage.innerHTML = `Something went wrong: ${error.message}. <a href="index.html">Try again</a>`;
        }
    }
});