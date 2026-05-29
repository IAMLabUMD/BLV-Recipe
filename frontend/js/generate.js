document.addEventListener('DOMContentLoaded', () => {

    const recipeForm = document.getElementById('recipeForm');
    const recipeUrlInput = document.getElementById('recipeUrl');
    const errorMessage = document.getElementById('errorMessage');
    const floatingLabel = document.querySelector('.floating-label');

    if (!recipeForm || !recipeUrlInput) return;

    if (floatingLabel && recipeUrlInput) {
        const updateLabelPosition = () => {
            if (recipeUrlInput.value || document.activeElement === recipeUrlInput) {
                floatingLabel.classList.add('active');
            } else {
                floatingLabel.classList.remove('active');
            }
        };

        recipeUrlInput.addEventListener('input', updateLabelPosition);
        recipeUrlInput.addEventListener('focus', updateLabelPosition);
        recipeUrlInput.addEventListener('blur', updateLabelPosition);
    }

    recipeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        errorMessage.textContent = '';
        errorMessage.hidden = true;

        const recipeUrl = recipeUrlInput.value.trim();
        if (!recipeUrl) {
            errorMessage.textContent = 'Please enter a valid recipe URL.';
            errorMessage.hidden = false;
            return;
        }

        sessionStorage.setItem('pendingRecipeURL', recipeUrl);
        window.location.href = 'loading.html';
    });
});