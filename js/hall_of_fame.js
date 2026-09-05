// hall_of_fame.js — hall of fame view: nested tabs, each showing 4
// position tables (QB/RB/WR/TE). Wrapped in an IIFE for the same
// collision-avoidance reason as standings.js / record_book.js.

const HallOfFameView = (() => {
  const POSITIONS = ['QB', 'RB', 'WR', 'TE'];

  const TABS = [
    { key: 'top_seasons', label: 'Top Player Seasons', contextLabel: 'Season' },
    { key: 'top_weeks', label: 'Top Player Weeks', contextLabel: 'Week' },
    { key: 'all_time', label: 'All-Time Players', contextLabel: 'Games / Seasons' },
  ];

  let data = null;
  let activeTab = 'top_seasons';

  function fmtNum(v) {
    if (v === null || v === undefined) return '—';
    return v.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  }

  // All-time rows show career longevity instead of a single season/week.
  function fmtContext(tabKey, entry) {
    if (tabKey === 'all_time') return `${entry.games_played} GP`;
    if (tabKey === 'top_weeks') return `Week ${entry.week}, ${entry.season}` ?? '—';
    return entry.season ?? '—';
  }

  function renderPlayerRow(entry, index, tabKey) {
    let managers = [];
    let fullManagers = [];
    if (Array.isArray(entry.managers)) {
        if (entry.managers.length <= 2) {
            managers = entry.managers.join(', ');
        } else {
            const [first, second] = entry.managers;
            const remainingCount = entry.managers.length - 2
            managers = `${first}, ${second} +${remainingCount}`
        }
        fullManagers = entry.managers.join(',');
    } else {
        managers = entry.managers
        fullManagers = entry.managers
    }

    const context = fmtContext(tabKey, entry);
    // onerror removes the broken image instead of showing a broken-image
    // icon -- falls back to just the player name with no thumbnail.
    const imgTag = entry.player_id
      ? `<img class="player-thumb" src="https://sleepercdn.com/content/nfl/players/thumb/${entry.player_id}.jpg" alt="" onerror="this.remove()">`
      : '';
    return `
      <tr>
        <td class="col-rank">${index + 1}</td>
        <td class="col-name">
          ${imgTag}
          <span class="hof-player-info">
            <span class="hof-player-name">${entry.player}</span>
            <span class="record-footer" title=${fullManagers}>${context} · ${managers}</span>
          </span>
        </td>
        <td class="col-value">${fmtNum(entry.points)}</td>
      </tr>`;
  }

  function renderPositionCard(position, entries, tabKey) {
    const rows = entries.length
      ? entries.map((e, i) => renderPlayerRow(e, i, tabKey)).join('')
      : `<tr><td colspan="3" class="hof-empty">No entries yet</td></tr>`;

    return `
      <div class="record-card hof-card">
        <table>
          <thead>
            <tr>
              <th colspan="2">${position}</th>
              <th>Points</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }

  function renderTabs() {
    return `
      <div class="filter-toggle hof-tabs">
        ${TABS.map(
          (t) =>
            `<button data-tab="${t.key}" class="${t.key === activeTab ? 'is-active' : ''}">${t.label}</button>`
        ).join('')}
      </div>`;
  }

  function renderTables() {
    const positionsData = data[activeTab] || {};
    return `<div class="record-grid">${POSITIONS.map((pos) =>
      renderPositionCard(pos, positionsData[pos] || [], activeTab)
    ).join('')}</div>`;
  }

  function render() {
    const wrapper = document.getElementById('hall-of-fame-wrap');
    wrapper.innerHTML = renderTabs() + renderTables();
    wrapper.querySelectorAll('.hof-tabs button').forEach((btn) => {
      btn.addEventListener('click', () => {
        activeTab = btn.dataset.tab;
        render();
      });
    });
  }

  async function init() {
    data = await DataStore.loadHallOfFame();
    render();
  }

  return { init };
})();