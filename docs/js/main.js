async function initialLoad() {
  buildDropdownMenu();
  loadPage(loadSelectedTeam() || "Bed Bath & Bijan");
}

function buildDropdownMenu() {
  loadTeams().then(teams => {
    var menu = document.getElementById("dropdown-menu");
    menu.innerHTML = "";

    for (const team of teams) {
      var a = document.createElement("a");
      a.classList.add("dropdown-item")
      a.href = `javascript:loadPage("${team}")`;
      a.innerText = team;

      var li = document.createElement("li");
      li.classList.add("px-1");
      li.append(a);

      menu.append(li);
    }
  });
};

function loadPage(teamName) {
  updateSelectedTeam(teamName);
  updateCharts(teamName);
  updateRoster(teamName);
  updateResults(teamName);
}

async function updateSelectedTeam(teamName) {
  var emoji = await loadEmoji(teamName);
  replaceContent("selected-team", `${teamName} ${emoji}`);
  saveSelectedTeam(teamName);
}

async function updateCharts(teamName) {

  getPositionalBreakdown(teamName).then(data => {
    const chartData = {
      labels: POSITIONS,
      datasets: [{
        data: data,
        backgroundColor: LIGHT_PINK,
        borderColor: PINK,
        pointBackgroundColor: PINK,
        pointBorderColor: WHITE
      }]
    };

    const chartOptions = {
      events: [],
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        r: {
          ticks: {
            display: false,
          },
          suggestedMin: 0.0,
          suggestedMax: 1.0
        }
      },
      responsive: false
    };

    updateChart("radar", "roster-strength-chart", "#roster-strength-container", chartData, chartOptions);
  });

  getRosterMakeup(teamName).then(data => {
    const chartData = {
      labels: ["Draft", "Trade", "Add"],
      datasets: [{
        label: teamName,
        data: data,
        backgroundColor: [RED, GREEN, BLUE]
      }]
    };

    const chartOptions = { responsive: false };

    updateChart("pie", "team-makeup-chart", "#team-makeup-container", chartData, chartOptions);
  });

  getWeeklyPoints(teamName).then(data => {
    const chartData = {
      labels: [...Array(14).keys()].map(week => `Week ${week + 1}`),
      datasets: [
        { label: "Team Points", data: data[0], borderColor: PINK },
        { label: "Avg. Points", data: data[1] }
      ]
    };

    const chartOptions = { maintainAspectRatio: false };

    updateChart("line", "weekly-points-chart", "#weekly-points-container", chartData, chartOptions);
  });
}

function updateChart(chartType, chartId, containerId, data, options) {
  document.getElementById(chartId).remove();
  var canvas = document.createElement("canvas");
  canvas.setAttribute("id", chartId);
  canvas.height = 300;

  document.querySelector(containerId).append(canvas);

  new Chart(chartId, { type: chartType, data: data, options: options });
}

async function loadTeams() {
  return await loadFile("./data/teams.json")
    .then(json => json.teams);
}

async function loadEmoji(teamName) {
  return await loadFile("./data/teams.json")
    .then(json => json.translations[teamName] || "");
}

async function getPositionalBreakdown(teamName) {
  return await loadFile("./data/yearly.json")
    .then(json => json.teams[teamName]);

}

async function getRosterMakeup(teamName) {
  return await loadFile("./data/yearly.json")
    .then(json => json.team_makeup[teamName]);
}

async function getRosters(teamName) {
  return await loadFile("./data/positional.json")
    .then(json => json[teamName]);
}

async function getResults(teamName) {
  return await loadFile("./data/yearly.json")
    .then(json => json.results[teamName]);
}

async function getWeeklyPoints(teamName) {
  return await loadFile("./data/yearly.json")
    .then(json => [json.weekly_points[teamName], json.weekly_points.Average]);
}

function buildHeaderRow(position, data) {
  var name = document.createElement("th");
  name.append(`${position} (${data[position].length})`);

  var points = document.createElement("th");
  points.append("Total");

  var starts = document.createElement("th");
  starts.append("Starts");

  var average = document.createElement("th");
  average.append("Average");

  var row = document.createElement("tr");
  row.append(name, points, starts, average);
  return row;
}

function buildPlayerRow(player) {
  var name = document.createElement("td");
  name.classList.add("text-start");
  name.append(player[0]);

  var points = document.createElement("td");
  points.append(player[2]);

  var starts = document.createElement("td");
  starts.append(player[3]);

  var average = document.createElement("td");
  average.append(player[4]);

  var row = document.createElement("tr");
  row.append(name, points, starts, average);
  return row;
}

function addPositionalPlayers(position, data, tbody) {
  tbody.append(buildHeaderRow(position, data));

  for (const player of data[position]) {
    tbody.append(buildPlayerRow(player));
  }
}

function updateRoster(teamName) {
  getRosters(teamName)
    .then(data => {
      var tbody = document.createElement("tbody");

      POSITIONS.forEach(position =>
        addPositionalPlayers(position, data, tbody));

      replaceContent("roster-table", tbody);
    });
}

function buildResultRow(category, value) {
  var categoryCell = document.createElement("td");
  categoryCell.classList.add("text-end");
  categoryCell.append(`${category}:`);

  var valueCell = document.createElement("td");
  valueCell.classList.add("text-center");
  valueCell.append(value);

  var row = document.createElement("tr");
  row.append(categoryCell, valueCell);
  return row;
}

function addResultRow(category, value, tbody) {
  tbody.append(buildResultRow(category, value));
}

function updateResults(teamName) {
  getResults(teamName)
    .then(data => {
      var tbody = document.createElement("tbody");

      [
        ["Record", data.record],
        ["All-Play", data.all_play],
        ["Points for", data.points_for],
      ].forEach(result => addResultRow(result[0], result[1], tbody));

      replaceContent("results-table", tbody);
    });
}