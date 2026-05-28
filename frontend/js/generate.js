document.addEventListener('DOMContentLoaded', () => {

    const submitBtn = document.getElementById('submitBtn');

    if (!submitBtn) return;

    const recipeUrlInput = document.getElementById('recipeUrl');
    const errorMessage = document.getElementById('errorMessage');
    const floatingLabel = document.querySelector('.floating-label');

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