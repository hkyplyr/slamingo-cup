async function initialLoad() {
  const selectedTeam = document.cookie.replace('selectedTeam=', '');
  
  buildDropdownMenu();
  loadPage(selectedTeam || 'Bishop Sycamore');
}

async function buildDropdownMenu() {
  loadTeams().then(teams => {
    var menu = document.getElementById("dropdown-menu");
    menu.innerHTML = '';

    for (const team of teams) {
      var a = document.createElement("a");
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
  var selectedTeam = document.getElementById('selected-team');
  var emoji = await loadEmoji(teamName);
  selectedTeam.innerHTML = `${teamName} ${emoji}`
  document.cookie = 'selectedTeam=' + teamName;
}

async function updateCharts(teamName) {
  const BLUE = 'rgb(54, 162, 235)';
  const GREEN = 'rgb(75, 192, 192)';
  const LIGHT_PINK = 'rgba(255, 101, 194, 0.2)';
  const PINK = 'rgb(255, 101, 194)';
  const RED = 'rgb(255, 99, 132)';
  const WHITE = '#FFFFFF';

  getPositionalBreakdown(teamName).then(data => {
    const chartData = {
      labels: ['QB', 'RB', 'WR', 'TE', 'K', 'DEF'],
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

    updateChart('radar', '#chart-container', chartData, chartOptions);
  });

  getRosterMakeup(teamName).then(data => {
    const chartData = {
      labels: ['Draft', 'Trade', 'Add'],
      datasets: [{
        label: teamName,
        data: data,
        backgroundColor: [RED, GREEN, BLUE]
      }]
    };

    const chartOptions = { responsive: false };

    updateChart('pie', '#makeup-chart', chartData, chartOptions);
  });

  getWeeklyPoints(teamName).then(data => {
    const chartData = {
      labels: [...Array(14).keys()].map(week => `Week ${week + 1}`),
      datasets: [
        { label: 'Team Points', data: data[0], borderColor: PINK },
        { label: "Avg. Points", data: data[1] }
      ]
    };

    const chartOptions = { maintainAspectRatio: false };

    updateChart('line', '#weekly-chart', chartData, chartOptions);
  });
}

function updateChart(chartId, containerId, data, options) {
  document.getElementById(chartId).remove();
  var canvas = document.createElement('canvas');
  canvas.setAttribute('id', chartId);
  canvas.height = 300;

  document.querySelector(containerId).append(canvas);

  new Chart(chartId, { type: chartId, data: data, options: options });
}








async function loadFile(fileName) {
  return await fetch(fileName).then(res => res.json());
}

async function loadTeams() {
  return await loadFile('./data/teams.json')
    .then(json => json.teams);
}

async function loadEmoji(teamName) {
  return await loadFile('./data/teams.json')
    .then(json => json.translations[teamName] || '');
}


async function getPositionalBreakdown(teamName) {
  return await loadFile('./data/yearly.json')
    .then(json => json.teams[teamName]);

}

async function getRosterMakeup(teamName) {
  return await loadFile('./data/yearly.json')
    .then(json => json.team_makeup[teamName]);
}

async function getRosters(teamName) {
  return await loadFile('./data/positional.json')
    .then(json => json[teamName]);
}

async function getResults(teamName) {
  return await loadFile('./data/yearly.json')
    .then(json => json.results[teamName]);
}

async function getWeeklyPoints(teamName) {
  return await loadFile('./data/yearly.json')
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

  var row = document.createElement('tr');
  row.append(name, points, starts, average);
  return row;
}

function buildPlayerRow(player) {
  var name = document.createElement("td");
  name.classList.add("text-left");
  name.append(player[0]);

  var points = document.createElement("td");
  points.append(player[2]);

  var starts = document.createElement("td");
  starts.append(player[3]);

  var average = document.createElement("td");
  average.append(player[4]);

  var row = document.createElement('tr');
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
  const positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF'];
  getRosters(teamName)
    .then(data => {
      var tbody = document.getElementById("roster-tbody");
      tbody.innerHTML = "";

      positions.forEach(position =>
        addPositionalPlayers(position, data, tbody));
    })
}

function buildResultRow(category, value, rank) {
  var categoryCell = document.createElement("td");
  categoryCell.classList.add("text-right");
  categoryCell.append(`${category}:`);

  var valueCell = document.createElement("td");
  valueCell.classList.add("text-center");
  valueCell.append(value);

  var rankCell = document.createElement("td");
  rankCell.classList.add("text-left");
  rankCell.append(rank);

  var row = document.createElement("tr");
  row.append(categoryCell, valueCell, rankCell);
  return row;
}

function updateResults(teamName) {
  getResults(teamName)
    .then(data => {
      var tbody = document.getElementById("results-tbody");
      tbody.innerHTML = "";

      tbody.append(buildResultRow('Finish', data.finish, ''));
      tbody.append(buildResultRow('Record', `${data.record} (${data.record_avg})`, data.record_rk));
      tbody.append(buildResultRow('All-Play', `${data.all_play} (${data.all_play_avg})`, data.all_play_rk));
      tbody.append(buildResultRow('Points for', `${data.pf} (${data.pf_avg})`, data.pf_rk));
      tbody.append(buildResultRow('Points against', `${data.pa} (${data.pa_avg})`, data.pa_rk));
    });
}