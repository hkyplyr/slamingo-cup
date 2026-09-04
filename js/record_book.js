// record_book.js — record book view: league record categories, each
// showing every ranked entry (not just the top one). Wrapped in an
// IIFE for the same reason as standings.js — see that file's header.

const RecordBookView = (() => {
  let entries = [];

  function fmtNum(v) {
    if (v === null || v === undefined) return '—';
    return v.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function renderCategory(category) {
    const rows = category.entries
      .map(
        (entry) => `
          <tr>
            <td class="col-rank">${entry.rank}</td>
            <td class="col-name">${entry.manager}${
              entry.footer ? ` <span class="record-footer">${entry.footer}</span>` : ''
            }</td>
            <td class="col-value">${fmtNum(entry.value)}</td>
          </tr>`
      )
      .join('');

    return `
      <div class="record-card">
        <table>
          <thead>
            <tr><th colspan="3">${category.name}</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }

  // --- Head-to-head matrix ---------------------------------------------
  // Source data stores each unordered pair once (see data/head_to_head.json).
  // Everything else -- the mirrored matrix, the diagonal, and each
  // manager's Total column -- is derived here so there's exactly one
  // number on record for any given pair, not two that could disagree.

  function buildLookup(matchups) {
    const map = {};
    matchups.forEach((m) => {
      map[`${m.a}|${m.b}`] = m;
    });
    return map;
  }

  // Returns { wins, losses, ties } from row's perspective against col,
  // regardless of which side of the pair was stored as "a" vs "b".
  // Returns null if they haven't played (rendered as "—", same as the
  // diagonal, and excluded from that row's Total).
  function getRecord(lookup, row, col) {
    const direct = lookup[`${row}|${col}`];
    if (direct) return { wins: direct.a_wins, losses: direct.b_wins, ties: direct.ties };
    const reverse = lookup[`${col}|${row}`];
    if (reverse) return { wins: reverse.b_wins, losses: reverse.a_wins, ties: reverse.ties };
    return null;
  }

  function fmtRecord(rec) {
    return rec.ties > 0 ? `${rec.wins}-${rec.losses}-${rec.ties}` : `${rec.wins}-${rec.losses}`;
  }

  function renderHeadToHead(data) {
    const { managers, matchups } = data;
    const lookup = buildLookup(matchups);

    const headerCells = managers.map((m) => `<th>${m}</th>`).join('');

    const bodyRows = managers
      .map((rowMgr) => {
        const cells = managers
          .map((colMgr) => {
            if (rowMgr === colMgr) return `<td class="h2h-diag">—</td>`;
            const rec = getRecord(lookup, rowMgr, colMgr);
            if (!rec) return `<td class="h2h-empty">—</td>`;
            const cls = rec.wins > rec.losses ? 'h2h-win' : rec.wins < rec.losses ? 'h2h-loss' : 'h2h-tie';
            return `<td class="${cls}">${fmtRecord(rec)}</td>`;
          })
          .join('');

        return `
          <tr>
            <th scope="row">${rowMgr}</th>
            ${cells}
          </tr>`;
      })
      .join('');

    return `
      <div class="h2h-wrap">
        <table class="h2h-table">
          <thead>
            <tr>
              <th class="h2h-corner">Manager</th>
              ${headerCells}
            </tr>
          </thead>
          <tbody>${bodyRows}</tbody>
        </table>
      </div>`;
  }

  function render(recordData, headToHeadData) {
    const wrapper = document.getElementById('record-book-wrap');
    const categoriesHtml = `<div class="record-grid">${recordData.map(renderCategory).join('')}</div>`;
    const h2hHtml = headToHeadData ? renderHeadToHead(headToHeadData) : '';
    wrapper.innerHTML = categoriesHtml + h2hHtml;
  }

  async function init() {
    const [recordData, headToHeadData] = await Promise.all([
      DataStore.loadRecordBook(),
      DataStore.loadHeadToHead(),
    ]);
    entries = recordData;
    render(entries, headToHeadData);
  }

  return { init };
})();