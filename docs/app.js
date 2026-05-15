async function loadApps() {

  const repos = await fetch("./repos.json")
    .then(r => r.json());

  const container = document.getElementById("apps");

  for (const repo of repos) {

    const data = await fetch(`./json/${repo}.json`)
      .then(r => r.json());

    const section = document.createElement("div");

    section.className = "repo";

    section.innerHTML = `
      <h2>${repo}</h2>
    `;

    data.forEach(app => {

      const encoded = encodeURIComponent(JSON.stringify({
        id: app.package_id
      }));

      const obtainium = `obtainium://app/${encoded}`;

      section.innerHTML += `
        <div class="card">
          <h3>${app.app_name}</h3>

          <p>${app.package_id}</p>

          <div class="buttons">

            <a href="${app.play_store_url}" target="_blank">
              Play Store
            </a>

            <a href="${obtainium}">
              Add to Obtainium
            </a>

            <a href="${app.download_url}" target="_blank">
              APK
            </a>

          </div>
        </div>
      `;
    });

    container.appendChild(section);
  }
}

loadApps();