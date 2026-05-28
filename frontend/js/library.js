/**
 * Recipe Library Page
 * Loads and displays recipes from the Supabase archive
 */

const API_BASE_URL = "https://spokenspoon.onrender.com";

const loadingMessageEl = document.getElementById("loadingMessage");
const emptyStateEl = document.getElementById("emptyState");
const recipeGridEl = document.getElementById("recipeGrid");

/**
 * Create a recipe card element
 */
function createRecipeCard(recipe) {
  const card = document.createElement("article");
  card.className = "recipe-card";

  const title = document.createElement("h2");
  title.className = "recipe-card-title";
  title.textContent = recipe.recipe_title || "Untitled Recipe";
  card.appendChild(title);

  const meta = document.createElement("p");
  meta.className = "recipe-card-meta";
  const createdDate = new Date(recipe.created_at).toLocaleDateString();
  meta.textContent = `Created: ${createdDate}`;
  card.appendChild(meta);

  const buttonsContainer = document.createElement("div");
  buttonsContainer.className = "recipe-card-buttons";

  // Button: Open original recipe
  const openOriginalBtn = document.createElement("a");
  openOriginalBtn.href = recipe.recipe_url;
  openOriginalBtn.target = "_blank";
  openOriginalBtn.rel = "noopener noreferrer";
  openOriginalBtn.className = "btn-open-original";
  openOriginalBtn.innerHTML = '<i class="ph ph-link-external"></i> View Original';
  buttonsContainer.appendChild(openOriginalBtn);

  // Button: View accessible recipe
  const viewAccessibleBtn = document.createElement("a");
  viewAccessibleBtn.href = `output.html?id=${recipe.id}`;
  viewAccessibleBtn.className = "btn-view-accessible";
  viewAccessibleBtn.innerHTML = '<i class="ph ph-book"></i> Read Accessible Recipe';
  buttonsContainer.appendChild(viewAccessibleBtn);

  // Button: Download accessible recipe
  const downloadBtn = document.createElement("button");
  downloadBtn.className = "btn-download";
  downloadBtn.innerHTML = '<i class="ph ph-download"></i> Download HTML';
  downloadBtn.addEventListener("click", () => downloadRecipe(recipe));
  buttonsContainer.appendChild(downloadBtn);

  card.appendChild(buttonsContainer);

  return card;
}

/**
 * Download the accessible recipe as an HTML file
 */
function downloadRecipe(recipe) {
  if (!recipe.id) {
    console.error("Cannot download: Recipe ID missing");
    return;
  }

  fetch(`${API_BASE_URL}/recipes/${recipe.id}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to fetch recipe: ${response.statusText}`);
      }
      return response.json();
    })
    .then((fullRecipe) => {
      const blob = new Blob([fullRecipe.output_html], { type: "text/html" });
      const url = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = `${recipe.recipe_title || "recipe"}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    })
    .catch((error) => {
      console.error("Download error:", error);
      alert("Failed to download recipe. Please try again.");
    });
}

/**
 * Load and display recipes from the API
 */
async function loadRecipes() {
  try {
    const response = await fetch(`${API_BASE_URL}/recipes`);

    if (!response.ok) {
      throw new Error(`Failed to fetch recipes: ${response.statusText}`);
    }

    const recipes = await response.json();

    loadingMessageEl.hidden = true;

    if (!recipes || recipes.length === 0) {
      emptyStateEl.hidden = false;
      recipeGridEl.innerHTML = "";
    } else {
      emptyStateEl.hidden = true;
      recipeGridEl.innerHTML = "";

      recipes.forEach((recipe) => {
        const card = createRecipeCard(recipe);
        recipeGridEl.appendChild(card);
      });
    }
  } catch (error) {
    console.error("Error loading recipes:", error);
    loadingMessageEl.hidden = true;
    recipeGridEl.innerHTML = `
      <div class="recipe-load-error">
        <p>Failed to load recipes. Please try refreshing the page.</p>
      </div>
    `;
  }
}

document.addEventListener("DOMContentLoaded", loadRecipes);
