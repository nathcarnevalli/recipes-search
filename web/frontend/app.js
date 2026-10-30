const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const sourceSelect = document.getElementById("source");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function renderRecipe(recipe) {
  const card = document.createElement("li");
  card.className = "card";

  const title = document.createElement("h2");
  const link = document.createElement("a");
  link.href = recipe.url;
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = recipe.title;
  title.appendChild(link);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = `Fuente: ${recipe.source} · Puntuación: ${recipe.score.toFixed(2)}`;

  const ingredients = document.createElement("ul");
  recipe.ingredients.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    ingredients.appendChild(li);
  });

  const snippet = document.createElement("p");
  snippet.textContent = recipe.snippet;

  card.append(title, meta, ingredients, snippet);
  return card;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const params = new URLSearchParams({ q: queryInput.value.trim() });
  if (sourceSelect.value) params.set("source", sourceSelect.value);

  resultsEl.replaceChildren();
  setStatus("Buscando...");

  try {
    const response = await fetch(`/api/search?${params}`);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(typeof body.detail === "string" ? body.detail : "Error en la búsqueda.");
    }

    const data = await response.json();
    if (data.total === 0) {
      setStatus("No se encontraron recetas.");
      return;
    }

    setStatus(`${data.total} recetas encontradas.`);
    data.results.forEach((recipe) => resultsEl.appendChild(renderRecipe(recipe)));
  } catch (error) {
    setStatus(error.message, true);
  }
});
