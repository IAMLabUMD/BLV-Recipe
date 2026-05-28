/**
 * Recipe Display Page
 * Loads and displays a single accessible recipe from the library
 */

const API_BASE_URL = "https://spokenspoon.onrender.com";

const recipeTitleEl = document.getElementById("recipeTitle");
const loadingMessageEl = document.getElementById("loadingMessage");
const recipeActionsEl = document.getElementById("recipeActions");
const recipeDisplayEl = document.getElementById("recipeDisplay");
const recipeFrameEl = document.getElementById("recipeFrame");
const originalRecipeLinkEl = document.getElementById("originalRecipeLink");
const downloadBtnEl = document.getElementById("downloadBtn");
const errorMessageEl = document.getElementById("errorMessage");
const errorDetailsEl = document.getElementById("errorDetails");

let currentRecipe = null;

/**
 * Extract recipe ID from URL query parameter
 */
function getRecipeIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

/**
 * Download the accessible recipe as an HTML file
 */
function downloadRecipe(recipe) {
  if (!recipe || !recipe.output_html) {
    console.error("Cannot download: Recipe HTML missing");
    return;
  }

  const blob = new Blob([recipe.output_html], { type: "text/html" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = `${recipe.recipe_title || "recipe"}.html`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Show error message to user
 */
function showError(message) {
  loadingMessageEl.hidden = true;
  recipeActionsEl.hidden = true;
  recipeDisplayEl.hidden = true;
  errorMessageEl.hidden = false;
  errorDetailsEl.textContent = message;
}

/**
 * Load and display a single recipe
 */
async function loadRecipe() {
  const recipeId = getRecipeIdFromUrl();

  if (!recipeId) {
    showError("No recipe ID provided. Please select a recipe from the library.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Recipe not found.");
      }
      throw new Error(`Failed to fetch recipe: ${response.statusText}`);
    }

    currentRecipe = await response.json();

    loadingMessageEl.hidden = true;

    recipeTitleEl.textContent = currentRecipe.recipe_title || "Untitled Recipe";
    document.title = `${currentRecipe.recipe_title || "Recipe"} - Spoken Spoon`;

    if (currentRecipe.recipe_url) {
      originalRecipeLinkEl.href = currentRecipe.recipe_url;
      originalRecipeLinkEl.hidden = false;
    }

    if (currentRecipe.output_html) {
      let htmlContent = currentRecipe.output_html;
      if (htmlContent.startsWith('```html')) {
        htmlContent = currentRecipe.output_html.replace(/^```html\n/, '').replace(/\n```$/, '');
      }
      recipeFrameEl.srcdoc = htmlContent;
    }

    recipeDisplayEl.hidden = false;
    recipeActionsEl.hidden = false;
  } catch (error) {
    console.error("Error loading recipe:", error);
    showError(error.message);
  }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
  downloadBtnEl.addEventListener("click", () => {
    downloadRecipe(currentRecipe);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadRecipe();
});
