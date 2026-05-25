const BACKEND_URL = '/generate';

document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('submitBtn');

    // Only run on pages that have the submit button
    if (!submitBtn) return;

    const recipeUrlInput = document.getElementById('recipeUrl');
    const errorMessage = document.getElementById('errorMessage');

    submitBtn.addEventListener('click', () => {
        errorMessage.textContent = '';

        const recipeUrl = recipeUrlInput.value.trim();
        if (!recipeUrl) {
            errorMessage.textContent = 'Please enter a valid recipe URL.';
            return;
        }

        sessionStorage.setItem('pendingRecipeURL', recipeUrl);
        window.location.href = 'loading.html';
    });
});