const BACKEND_URL = '/generate';

document.addEventListener('DOMContentLoaded', async () => {
    console.log("loading.js started");
    const errorMessage = document.getElementById('errorMessage');
    const recipeUrl = sessionStorage.getItem('pendingRecipeURL');
    console.log("pendingRecipeURL:", recipeUrl);

    if (!recipeUrl) {
        window.location.href = 'index.html';
        return;
    }

    sessionStorage.removeItem('pendingRecipeURL');

    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: recipeUrl })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        let htmlContent = data.html;

        if (htmlContent.startsWith('```html')) {
            htmlContent = htmlContent.replace(/^```html\n/, '').replace(/\n```$/, '');
        }

        sessionStorage.setItem('recipeHTML', htmlContent);
        window.location.href = 'output.html';

    } catch (error) {
        console.log("fetch failed:", error.message);
        if (errorMessage) {
            errorMessage.hidden = false;
            errorMessage.innerHTML = `Something went wrong: ${error.message}. <a href="index.html">Try again</a>`;
        }
    }
});