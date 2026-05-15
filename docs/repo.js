async function loadRepoApps() {

  const params =
    new URLSearchParams(window.location.search);

  const repo =
    params.get("repo");

  if (!repo) {
    return;
  }

  document.getElementById("repo-title")
    .textContent = repo;

  const data = await fetch(
    `./json/${repo}.json`
  ).then(r => r.json());

  const container =
    document.getElementById("apps");

  const base =
    window.location.origin +
    window.location.pathname
      .replace("repo.html", "");

  for (const app of data) {

    const configUrl =
      `${base}discoverium/${app.discoverium_file}`;

    let obtainiumUrl = "#";

    try {

      const configJson =
        await fetch(configUrl)
          .then(r => r.json());

      const encoded =
        encodeURIComponent(
          JSON.stringify(configJson)
        );

      obtainiumUrl =
        `obtainium://app/${encoded}`;

    } catch (e) {

      console.error(e);
    }

    container.innerHTML += `
      <div class="card">

        <h2>${app.app_name}</h2>

        <p>${app.package_id}</p>

        <div class="buttons">

          <a href="${app.play_store_url}" target="_blank">
            Play Store
          </a>

          <a href="${app.download_url}" target="_blank">
            APK
          </a>

          <a href="${configUrl}" target="_blank">
            JSON
          </a>

          <a href="${obtainiumUrl}">
            Add to Obtainium
          </a>

        </div>

      </div>
    `;
  }
}

loadRepoApps();