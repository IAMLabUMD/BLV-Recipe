/**
 * Recipe Library Page
 * Loads and displays recipes from the Supabase archive
 */

const API_BASE_URL = "https://spokenspoon.onrender.com";

const loadingMessageEl = document.getElementById("loadingMessage");
const emptyStateEl = document.getElementById("emptyState");
const recipeGridEl = document.getElementById("recipeGrid");
const featuredRecipeGridEl = document.getElementById("featuredRecipeGrid");


const FEATURED_RECIPES = [
  {
    id: "shrimp-scampi",
    title: "Shrimp Scampi",
    imageUrl: "./public/images/example-recipes/shrimp-scampi.jpg",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:Garlic_Shrimp_Scampi_Pasta",
    blindKitchenUrl: "https://theblindkitchen.com/shrimp-scampi/"
  },
  {
    id: "key-lime-pie",
    title: "Key Lime Pie",
    imageUrl: "./public/images/example-recipes/key-lime-pie.jpg",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:Key_Lime_Meringue_Pie",
    blindKitchenUrl: "https://theblindkitchen.com/key-lime-pie/"
  },
  {
    id: "english-breakfast",
    title: "English Breakfast",
    imageUrl: "./public/images/example-recipes/english-breakfast.jpg",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:English_Breakfast",
    blindKitchenUrl: "https://theblindkitchen.com/english-breakfast/"
  },
  {
    id: "green-bean-casserole",
    title: "Green Bean Casserole",
    imageUrl: "./public/images/example-recipes/green-bean-casserole.jpg",
    originalRecipeUrl: "https://en.wikibooks.org/wiki/Cookbook:Green_Bean_Casserole",
    blindKitchenUrl: "https://theblindkitchen.com/traditional-green-bean-casserole/"
  }
];

/**
 * Create a featured recipe card element
 */
function createFeaturedRecipeCard(recipe) {
  const card = document.createElement("article");
  card.className = "recipe-card featured-recipe-card";

  // Image container
  const imageContainer = document.createElement("div");
  imageContainer.className = "featured-recipe-image";
  const image = document.createElement("img");
  image.src = recipe.imageUrl;
  image.alt = recipe.title;
  imageContainer.appendChild(image);
  card.appendChild(imageContainer);

  const contentContainer = document.createElement("div");
  contentContainer.className = "featured-recipe-content";
  card.appendChild(contentContainer);

  const headerContainer = document.createElement("div");
  headerContainer.className = "recipe-card-header";
  contentContainer.appendChild(headerContainer);

  const headerContent = document.createElement("div");
  headerContent.className = "recipe-card-header-content";
  headerContainer.appendChild(headerContent);

  const title = document.createElement("h3");
  title.className = "recipe-card-title";
  title.textContent = recipe.title;
  headerContent.appendChild(title);

  const buttonsContainer = document.createElement("div");
  buttonsContainer.className = "recipe-card-buttons";

  // Button: View adapted recipe
  const viewAdaptedBtn = document.createElement("a");
  viewAdaptedBtn.href = `recipe.html?example=${recipe.id}`;
  viewAdaptedBtn.className = "btn-view-adapted";
  viewAdaptedBtn.setAttribute("aria-label", `View ${recipe.title} on Spoken Spoon`);
  viewAdaptedBtn.innerHTML = '<i class="ph ph-book-open-text"></i> View on Spoken Spoon';
  buttonsContainer.appendChild(viewAdaptedBtn);

  // Button: Open The Blind Kitchen
  const openBlindKitchenBtn = document.createElement("a");
  openBlindKitchenBtn.href = recipe.blindKitchenUrl;
  openBlindKitchenBtn.target = "_blank";
  openBlindKitchenBtn.rel = "noopener noreferrer";
  openBlindKitchenBtn.className = "btn-open-original";
  openBlindKitchenBtn.setAttribute("aria-label", `View ${recipe.title} on The Blind Kitchen`);
  openBlindKitchenBtn.innerHTML = '<i class="ph ph-arrow-square-out"></i> View on The Blind Kitchen';
  buttonsContainer.appendChild(openBlindKitchenBtn);

  contentContainer.appendChild(buttonsContainer);

  return card;
}

/**
 * Render featured recipes
 */
function renderFeaturedRecipes() {
  featuredRecipeGridEl.innerHTML = "";
  FEATURED_RECIPES.forEach((recipe) => {
    const card = createFeaturedRecipeCard(recipe);
    featuredRecipeGridEl.appendChild(card);
  });
}


function createRecipeCard(recipe) {
  const card = document.createElement("article");
  card.className = "recipe-card";

  const headerContainer = document.createElement("div");
  headerContainer.className = "recipe-card-header";
  card.appendChild(headerContainer);

  const headerContent = document.createElement("div");
  headerContent.className = "recipe-card-header-content";
  headerContainer.appendChild(headerContent);

  const title = document.createElement("h2");
  title.className = "recipe-card-title";
  title.textContent = recipe.recipe_title || "Untitled Recipe";
  headerContent.appendChild(title);

  const meta = document.createElement("p");
  meta.className = "recipe-card-meta";
  const createdDate = new Date(recipe.created_at).toLocaleDateString();
  meta.textContent = `Created: ${createdDate}`;
  headerContent.appendChild(meta);

  // Button: Download accessible recipe (icon button in top right)
  const downloadBtn = document.createElement("button");
  downloadBtn.className = "btn-download-icon";
  downloadBtn.setAttribute("aria-label", `Download ${recipe.recipe_title || "recipe"}`);
  downloadBtn.innerHTML = '<i class="ph ph-download-simple"></i>';
  downloadBtn.addEventListener("click", () => downloadRecipe(recipe));
  headerContainer.appendChild(downloadBtn);

  const buttonsContainer = document.createElement("div");
  buttonsContainer.className = "recipe-card-buttons";

  // Button: View adapted recipe
  const viewAdaptedBtn = document.createElement("a");
  viewAdaptedBtn.href = `recipe.html?id=${recipe.id}`;
  viewAdaptedBtn.className = "btn-view-adapted";
  viewAdaptedBtn.setAttribute("aria-label", `View ${recipe.recipe_title || "recipe"} on Spoken Spoon`);
  viewAdaptedBtn.innerHTML = '<i class="ph ph-book-open-text"></i> View on Spoken Spoon';
  buttonsContainer.appendChild(viewAdaptedBtn);

  // Button: Open original recipe
  const openOriginalBtn = document.createElement("a");
  openOriginalBtn.href = recipe.recipe_url;
  openOriginalBtn.target = "_blank";
  openOriginalBtn.rel = "noopener noreferrer";
  openOriginalBtn.className = "btn-open-original";
  openOriginalBtn.setAttribute("aria-label", `View ${recipe.recipe_title || "recipe"} original recipe`);
  openOriginalBtn.innerHTML = '<i class="ph ph-arrow-square-out"></i> View Original Recipe';
  buttonsContainer.appendChild(openOriginalBtn);

  card.appendChild(buttonsContainer);

  return card;
}

/**
 * Download the adapted recipe as an HTML file
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

document.addEventListener("DOMContentLoaded", () => {
  renderFeaturedRecipes();
  loadRecipes();
});
