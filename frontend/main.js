let currentTag = null;

document.addEventListener("DOMContentLoaded", function () {

  const themeSwitcher = document.getElementById("theme-switcher-grid");
  const themeSwitch = document.getElementById("theme-switch");
  const filterSelect = document.getElementById("filter-select");
  const tableBody = document.querySelector("#articles-table tbody");
  const canvasCtx = document.getElementById("sentiment-chart").getContext("2d");
  const tagsList = document.getElementById("tags-list");

  let allArticles = [];
  let chart;

  const currentTheme = localStorage.getItem("theme") || "light";

  chart = new Chart(canvasCtx, {
    type: "pie",
    data: {
      labels: ["Позитивні", "Нейтральні", "Негативні"],
      datasets: [
        {
          data: [0, 0, 0],
          backgroundColor: ["#4caf50", "#ffca28", "#f44336"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "top" } },
    },
  });

  applyTheme(currentTheme);

  if (themeSwitcher) {
    themeSwitcher.addEventListener("click", () => toggleTheme());
  }
  if (themeSwitch) {
    themeSwitch.addEventListener("change", () => toggleTheme());
  }

  function toggleTheme() {
    const isDarkMode = document.body.classList.toggle("dark-mode");
    const newTheme = isDarkMode ? "dark" : "light";
    applyTheme(newTheme);
    localStorage.setItem("theme", newTheme);
  }

  function applyTheme(theme) {
    const isDark = theme === "dark";
    document.body.classList.toggle("dark-mode", isDark);
    document.body.style.backgroundColor = isDark
      ? "var(--bg-color-dark)"
      : "var(--bg-color-light)";

    if (themeSwitcher) {
      themeSwitcher.classList.toggle("night-theme", isDark);
    }
    if (themeSwitch) {
      themeSwitch.checked = isDark;
    }

    if (chart) {
      chart.options.plugins.legend.labels.color = isDark ? "#e0e0e0" : "#333";
      chart.update();
    }
  }

  async function loadData() {
    try {
      await fetch(`${API_BASE}/fetch/${STUDENT_ID}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });

      const res = await fetch(`${API_BASE}/analyze/${STUDENT_ID}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();

      allArticles = data.articles.map((a) => ({
        ...a,
        date: a.published ? new Date(a.published) : new Date(),
        tags: a.tags || [],
      }));

      renderTags(data.tags || []);
      render();
    } catch (err) {
      console.error("Ошибка при загрузке данных:", err);
    }
  }

function renderTags(tags) {
    tagsList.innerHTML = (tags || [])
      .map(
        (tag) =>
          `<li><a href="#" class="tag-link" data-tag="${tag.tag}">${tag.tag} (${tag.count})</a></li>`
      )
      .join("");

const tagLinks = document.querySelectorAll(".tag-link");
    tagLinks.forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        const tag = event.target.getAttribute("data-tag");

        if (currentTag === tag) {
          currentTag = null;
          render();
        } else {
          currentTag = tag;
          render({ tagFilter: tag });
        }
      });
    });
  }


  function render(filterOptions = {}) {
    const { sentimentFilter = "all", tagFilter = null } = filterOptions;

    const filtered = allArticles.filter((article) => {
      const matchesSentiment =
        sentimentFilter === "all" || article.sentiment === sentimentFilter;
      const matchesTag =
        !tagFilter || (article.tags && article.tags.includes(tagFilter));
      return matchesSentiment && matchesTag;
    });

    tableBody.innerHTML = filtered
      .sort((a, b) => b.date - a.date)
      .map(
        (article) =>
          `<tr>
             <td>${article.date.toLocaleString()}</td>
             <td>${article.sentiment}</td>
             <td><a href="${article.link}" target="_blank">${article.title}</a></td>
          </tr>`
      )
      .join("");

    updateChart(filtered);
  }

  function filterByTag(tag) {
    render({ tagFilter: tag });
  }

  function updateChart(filteredArticles) {
    const counts = { positive: 0, neutral: 0, negative: 0 };
    filteredArticles.forEach((article) => counts[article.sentiment]++);

    chart.data.datasets[0].data = [
      counts.positive,
      counts.neutral,
      counts.negative,
    ];
    chart.update();
  }

function render(queryFilter = {}) {
    const { sentimentFilter = "all", tagFilter = null } = queryFilter;

    const filtered = allArticles.filter((article) => {
      const matchesSentiment =
        sentimentFilter === "all" || article.sentiment === sentimentFilter;
      const matchesTag =
        !tagFilter || (article.tags && article.tags.includes(tagFilter.toLowerCase()));
      return matchesSentiment && matchesTag;
    });

    tableBody.innerHTML = filtered
      .sort((a, b) => b.date - a.date)
      .map(
        (article) =>
          `<tr>
             <td>${article.date.toLocaleString()}</td>
             <td>${article.sentiment}</td>
             <td><a href="${article.link}" target="_blank">${article.title}</a></td>
          </tr>`
      )
      .join("");

    updateChart(filtered);
  }

  filterSelect.addEventListener("change", () => {
    render({ sentimentFilter: filterSelect.value });
  });

  loadData();
});