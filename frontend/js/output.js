/**
 * Output Display Page
 * Displays an adapted recipe from sessionStorage with download
 */

const API_BASE_URL = "https://spokenspoon.onrender.com";

const recipeTitleEl = document.getElementById("recipeTitle");
const recipeActionsEl = document.getElementById("recipeActions");
const recipeDisplayEl = document.getElementById("recipeDisplay");
const recipeFrameEl = document.getElementById("recipeFrame");
const originalRecipeLinkEl = document.getElementById("originalRecipeLink");
const downloadBtnEl = document.getElementById("downloadBtn");

let currentRecipeHTML = null;
let currentRecipeRecordId = null;

/**
 * Load recipe data from sessionStorage
 */
function loadRecipeFromStorage() {
    currentRecipeHTML = sessionStorage.getItem("recipeHTML");
    currentRecipeRecordId = sessionStorage.getItem("recipeRecordId");

    if (!currentRecipeHTML || currentRecipeHTML.trim() === "") {
        window.location.href = "index.html";
        return false;
    }

    return true;
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
 * Display the recipe in an iframe
 */
function displayRecipe() {
    // Inject font styles before displaying in iframe
    const styledHTML = injectFontStyles(currentRecipeHTML);
    recipeFrameEl.srcdoc = styledHTML;
    recipeDisplayEl.hidden = false;
}

/**
 * Mark recipe as downloaded via API
 */
async function markRecipeDownloaded() {
    if (!currentRecipeRecordId) {
        return;
    }

    try {
        await fetch(`${API_BASE_URL}/mark-downloaded/${currentRecipeRecordId}`, {
        method: "POST"
        });
    } catch (err) {
        console.error("Failed to mark download:", err);
    }
}

/**
 * Download the recipe as an HTML file
 */
async function downloadRecipe() {
    const blob = new Blob([currentRecipeHTML], { type: "text/html" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "accessible-recipe.html";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    await markRecipeDownloaded();
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    downloadBtnEl.addEventListener("click", () => {
        downloadRecipe();
    });
}

/**
 * Clean up sessionStorage
 */
function cleanupSessionStorage() {
    sessionStorage.removeItem("recipeHTML");
    sessionStorage.removeItem("recipeRecordId");
}

document.addEventListener("DOMContentLoaded", () => {
    if (!loadRecipeFromStorage()) {
        return;
    }

    displayRecipe();
    setupEventListeners();
    cleanupSessionStorage();
});
