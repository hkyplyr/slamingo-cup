// data.js — shared data access for the almanac site.
// Fetches JSON once per page load and caches it in memory.
// Also holds the derived-stat formulas so every page computes
// Win%, All-Play Win%, and Luck% the same way.

const DataStore = (() => {
  const cache = {};

  async function load(path) {
    if (cache[path]) return cache[path];
    const res = await fetch(path);
    if (!res.ok) {
      throw new Error(`Failed to load ${path}: ${res.status}`);
    }
    const json = await res.json();
    cache[path] = json;
    return json;
  }

  function loadCareerStats() {
    return load('data/career_stats.json');
  }

  function loadRecordBook() {
    // Fixed: was '../data/record_book.json', which only worked when this
    // page lived one folder down (record-book/index.html). Now that
    // standings and record book share one root-level page, this needs
    // to be root-relative like loadCareerStats() already is.
    return load('data/record_book.json');
  }

  function loadHeadToHead() {
    return load('data/head_to_head.json');
  }

  // --- Derived stats -------------------------------------------------
  // Stored data holds raw counts only (wins/losses/ties, all-play
  // record, etc). Percentages are computed here so there is exactly
  // one place to change the formula.

  function winPct(m) {
    const games = m.wins + m.losses + m.ties;
    if (games === 0) return 0;
    return (m.wins + 0.5 * m.ties) / games;
  }

  function allPlayWinPct(m) {
    const games = m.all_play_wins + m.all_play_losses + m.all_play_ties;
    if (games === 0) return 0;
    return (m.all_play_wins + 0.5 * m.all_play_ties) / games;
  }

  // Default luck formula: gap between how you did against your actual
  // schedule vs. against the whole league every week. Positive means
  // your schedule helped you; negative means it hurt you.
  function luckPct(m) {
    return winPct(m) - allPlayWinPct(m);
  }

  function playoffPct(m) {
    return m.playoff_appearances / m.seasons;
  }

  function record(m) {
    return `${m.wins}-${m.losses}-${m.ties}`;
  }

  function allPlayRecord(m) {
    return `${m.all_play_wins}-${m.all_play_losses}-${m.all_play_ties}`;
  }

  return {
    loadCareerStats,
    loadRecordBook,
    loadHeadToHead,
    winPct,
    allPlayWinPct,
    luckPct,
    record,
    allPlayRecord,
    playoffPct,
  };
})();