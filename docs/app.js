async function loadRepos() {

  const repos = await fetch("./repos.json")
    .then(r => r.json());

  const container =
    document.getElementById("repos");

  repos.forEach(repo => {

    const card =
      document.createElement("a");

    card.className = "repo-card";

    card.href =
      `repo.html?repo=${encodeURIComponent(repo)}`;

    card.innerHTML = `
      <h2>${repo}</h2>
      <p>View apps</p>
    `;

    container.appendChild(card);
  });
}

loadRepos();