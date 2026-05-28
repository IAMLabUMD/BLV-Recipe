const API_BASE_URL = 'https://spokenspoon.onrender.com';

document.addEventListener('DOMContentLoaded', () => {
    const recipeHTML = sessionStorage.getItem('recipeHTML');
    const recipeRecordId = sessionStorage.getItem('recipeRecordId');

    if (!recipeHTML || recipeHTML.trim() === '') {
        window.location.href = 'index.html';
        return;
    }

    const recipeDisplay = document.getElementById('recipeDisplay');

    const iframe = document.createElement('iframe');
    iframe.style.width = '100%';
    iframe.style.height = '600px';
    iframe.style.border = 'none';
    iframe.title = 'Recipe content';

    iframe.srcdoc = recipeHTML;

    recipeDisplay.appendChild(iframe);

    const downloadBtn = document.getElementById('downloadBtn');

    downloadBtn.addEventListener('click', async () => {
        const blob = new Blob([recipeHTML], { type: 'text/html' });

        const anchor = document.createElement('a');
        anchor.href = URL.createObjectURL(blob);
        anchor.download = 'accessible-recipe.html';
        anchor.click();

        URL.revokeObjectURL(anchor.href);

        if (recipeRecordId) {
            try {
                await fetch(
                    `${API_BASE_URL}/mark-downloaded/${recipeRecordId}`,
                    {
                        method: 'POST'
                    }
                );
            } catch (err) {
                console.log("Failed to mark download:", err);
            }
        }
    });

    sessionStorage.removeItem('recipeHTML');
    sessionStorage.removeItem('recipeRecordId');
});
