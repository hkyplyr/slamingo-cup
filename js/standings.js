// standings.js — landing page: all-time career standings & results.

const COLUMNS = [
  { key: 'name', label: 'Manager', sortable: true, align: 'left' },
  { key: 'record', label: 'Record', sortable: true, sortField: 'win_pct' },
  { key: 'points_for', label: 'PF', sortable: true },
  { key: 'points_against', label: 'PA', sortable: true },
  { key: 'all_play_record', label: 'All-Play', sortable: true, sortField: 'all_play_win_pct' },
  { key: 'luck_pct', label: 'Luck%', sortable: true },
  { key: 'playoff_appearances', label: 'Playoffs', sortable: true, sortField: 'playoff_pct' },
  { key: 'avg_finish', label: 'Avg Finish', sortable: true },
];

// Maps a column's data-key to the field it should actually sort by,
// for columns whose displayed value (a formatted string) isn't what
// should drive the ordering.
const SORT_FIELD_OVERRIDES = COLUMNS.reduce((acc, c) => {
  if (c.sortField) acc[c.key] = c.sortField;
  return acc;
}, {});

let allManagers = [];
let filter = 'active'; // 'all' | 'active' | 'inactive'
let sortKey = 'record';
let sortDir = 'desc';

function enrich(m) {
  return {
    ...m,
    record: DataStore.record(m),
    all_play_record: DataStore.allPlayRecord(m),
    win_pct: DataStore.winPct(m),
    all_play_win_pct: DataStore.allPlayWinPct(m),
    luck_pct: DataStore.luckPct(m),
    playoff_pct: DataStore.playoffPct(m),
  };
}

function fmtPct(v) {
  return `${(v * 100).toFixed(1)}%`;
}

function fmtLuck(v) {
  const pct = (v * 100).toFixed(1);
  return v > 0 ? `+${pct}%` : `${pct}%`;
}

function fmtNum(v) {
  if (v === null || v === undefined) return '—';
  return v.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

function fmtFixed(v, digits = 1) {
  if (v === null || v === undefined) return '—';
  return v.toFixed(digits);
}

function fmtRecordWithPct(recordStr, pct) {
  return `${recordStr} (${fmtPct(pct)})`;
}

function fmtNameBadges(m) {
  const trophies = '🏆'.repeat(m.titles || 0);
  const poops = '💩'.repeat(m.last_place_finishes || 0);
  const badges = [trophies, poops].filter(Boolean).join(' ');
  return badges ? ` <span class="name-badges" title="${m.titles || 0} title(s), ${m.last_place_finishes || 0} last-place finish(es)">${badges}</span>` : '';
}

function getFiltered() {
  let rows = allManagers.filter((m) => {
    if (filter === 'active') return m.active;
    if (filter === 'inactive') return !m.active;
    return true;
  });
  rows.sort((a, b) => {
    const field = SORT_FIELD_OVERRIDES[sortKey] || sortKey;
    const av = a[field];
    const bv = b[field];
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    if (typeof av === 'string') {
      return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
    }
    return sortDir === 'asc' ? av - bv : bv - av;
  });
  return rows;
}

function render() {
  const rows = getFiltered();
  const tbody = document.getElementById('standings-body');
  tbody.innerHTML = rows
    .map((m, i) => {
      const luckClass = m.luck_pct > 0 ? 'luck-pos' : m.luck_pct < 0 ? 'luck-neg' : '';
      const inactiveClass = m.active ? '' : 'is-inactive';
      return `
        <tr class="${inactiveClass}">
          <td class="col-name">${m.name}${fmtNameBadges(m)}</td>
          <td>${fmtRecordWithPct(m.record, m.win_pct)}</td>
          <td>${fmtNum(m.points_for)}</td>
          <td>${fmtNum(m.points_against)}</td>
          <td>${fmtRecordWithPct(m.all_play_record, m.all_play_win_pct)}</td>
          <td class="${luckClass}">${fmtLuck(m.luck_pct)}</td>
          <td>${fmtPct(m.playoff_pct)}</td>
          <td>${fmtFixed(m.avg_finish)}</td>
        </tr>`;
    })
    .join('');

  document.querySelectorAll('#standings-head th').forEach((th) => {
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.key === sortKey) {
      th.classList.add(sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
    }
  });
}

function buildHead() {
  const thead = document.getElementById('standings-head');
  thead.innerHTML = COLUMNS.map((c) => {
    const alignClass = c.align === 'left' ? 'col-left' : '';
    const clickable = c.sortable ? 'sortable' : '';
    return `<th class="${alignClass} ${clickable}" data-key="${c.key}">${c.label}</th>`;
  }).join('');

  thead.querySelectorAll('th.sortable').forEach((th) => {
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      if (sortKey === key) {
        sortDir = sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey = key;
        sortDir = 'desc';
      }
      render();
    });
  });
}

function buildToggle() {
  document.querySelectorAll('.filter-toggle button').forEach((btn) => {
    btn.addEventListener('click', () => {
      filter = btn.dataset.filter;
      document
        .querySelectorAll('.filter-toggle button')
        .forEach((b) => b.classList.toggle('is-active', b === btn));
      render();
    });
  });
}

async function init() {
  const data = await DataStore.loadCareerStats();
  allManagers = data.managers.map(enrich);
  buildHead();
  buildToggle();
  render();
}

init();