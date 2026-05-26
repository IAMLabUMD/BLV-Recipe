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

    // Handle quit button click
    quitButton.addEventListener('click', async () => {
        isAborted = true;
        quitButton.disabled = true;
        quitButton.textContent = 'Quitting...';

        // Abort the fetch request
        if (abortController) {
            abortController.abort();
        }

        // Tell the backend to cancel the task (don't await, just fire it off)
        fetch('/cancel', { method: 'POST' }).catch(err => {
            console.log("Cancel endpoint failed (this is okay):", err.message);
        });

        // Redirect immediately without waiting
        window.location.href = 'index.html';
    });

    try {
        abortController = new AbortController();
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: recipeUrl }),
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
                        const percent = Math.round((data.step / data.total) * 100);
                        if (progressFill) progressFill.style.width = `${percent}%`;
                        if (loadingMessage) loadingMessage.textContent = `${percent}% complete. ${data.message}`;
                    }

                    if (currentEvent === 'cancelled') {
                        // User cancelled the process
                        window.location.href = 'index.html';
                        return;
                    }

                    if (currentEvent === 'complete') {
                        let htmlContent = data.html;
                        if (htmlContent.startsWith('```html')) {
                            htmlContent = htmlContent.replace(/^```html\n/, '').replace(/\n```$/, '');
                        }
                        sessionStorage.setItem('recipeHTML', htmlContent);
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
        // Don't show error if user intentionally aborted
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