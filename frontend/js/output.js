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
 * Display the recipe in an iframe
 */
function displayRecipe() {
    recipeFrameEl.srcdoc = currentRecipeHTML;
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
