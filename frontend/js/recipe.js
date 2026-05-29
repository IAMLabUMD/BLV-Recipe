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
const blindKitchenLinkEl = document.getElementById("blindKitchenLink");
const downloadBtnEl = document.getElementById("downloadBtn");
const errorMessageEl = document.getElementById("errorMessage");
const errorDetailsEl = document.getElementById("errorDetails");

let currentRecipe = null;

// Example recipes mapping
const EXAMPLE_RECIPES = {
  "shrimp-scampi": {
    title: "Shrimp Scampi",
    file: "example-recipes/shrimp-scampi.html",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:Garlic_Shrimp_Scampi_Pasta",
    blindKitchenUrl: "https://theblindkitchen.com/shrimp-scampi/"
  },
  "key-lime-pie": {
    title: "Key Lime Pie",
    file: "example-recipes/key-lime-pie.html",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:Key_Lime_Meringue_Pie",
    blindKitchenUrl: "https://theblindkitchen.com/key-lime-pie/"
  },
  "english-breakfast": {
    title: "English Breakfast",
    file: "example-recipes/english-breakfast.html",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:English_Breakfast",
    blindKitchenUrl: "https://theblindkitchen.com/english-breakfast/"
  },
  "green-bean-casserole": {
    title: "Green Bean Casserole",
    file: "example-recipes/green-bean-casserole.html",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:Green_Bean_Casserole",
    blindKitchenUrl: "https://theblindkitchen.com/traditional-green-bean-casserole/"
  }
};

/**
 * Extract recipe parameters from URL
 */
function getRecipeParametersFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return {
    id: params.get("id"),
    example: params.get("example")
  };
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
 * Inject font-family CSS into HTML content for iframe display
 */
function injectFontStyles(htmlContent) {
  const fontStyle = `
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;500;600&display=swap');
      body {
        font-family: "Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
    </style>
  `;

  // Insert style tag after <head> opening tag
  const headMatch = htmlContent.match(/<head[^>]*>/i);
  if (headMatch) {
    const insertIndex = headMatch.index + headMatch[0].length;
    return htmlContent.slice(0, insertIndex) + fontStyle + htmlContent.slice(insertIndex);
  }

  return htmlContent;
}

/**
 * Load and display a single recipe
 */
async function loadRecipe() {
  const params = getRecipeParametersFromUrl();

  if (!params.id && !params.example) {
    showError("No recipe provided. Please select a recipe from the library.");
    return;
  }

  try {
    let recipe;

    if (params.example) {
      // Load example recipe from static file
      const exampleInfo = EXAMPLE_RECIPES[params.example];
      if (!exampleInfo) {
        throw new Error("Example recipe not found.");
      }

      const response = await fetch(exampleInfo.file);
      if (!response.ok) {
        throw new Error(`Failed to load example recipe: ${response.statusText}`);
      }

      const htmlContent = await response.text();
      recipe = {
        recipe_title: exampleInfo.title,
        output_html: htmlContent,
        recipe_url: exampleInfo.originalRecipeUrl,
        blindKitchenUrl: exampleInfo.blindKitchenUrl
      };
    } else {
      // Load database recipe
      const response = await fetch(`${API_BASE_URL}/recipes/${params.id}`);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Recipe not found.");
        }
        throw new Error(`Failed to fetch recipe: ${response.statusText}`);
      }

      recipe = await response.json();
    }

    currentRecipe = recipe;

    loadingMessageEl.hidden = true;

    recipeTitleEl.textContent = currentRecipe.recipe_title || "Untitled Recipe";
    document.title = `${currentRecipe.recipe_title || "Recipe"} - Spoken Spoon`;

    if (currentRecipe.recipe_url) {
      originalRecipeLinkEl.href = currentRecipe.recipe_url;
      originalRecipeLinkEl.hidden = false;
    }

    if (currentRecipe.blindKitchenUrl) {
      blindKitchenLinkEl.href = currentRecipe.blindKitchenUrl;
      blindKitchenLinkEl.hidden = false;
    }

    if (currentRecipe.output_html) {
      let htmlContent = currentRecipe.output_html;
      if (htmlContent.startsWith('```html')) {
        htmlContent = currentRecipe.output_html.replace(/^```html\n/, '').replace(/\n```$/, '');
      }
      // Inject font styles before displaying in iframe
      htmlContent = injectFontStyles(htmlContent);
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
