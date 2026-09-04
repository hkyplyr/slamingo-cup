// app.js — single-page router. Shows/hides view sections instead of
// navigating to a new HTML file, so the banner/fonts/CSS never get
// torn down and rebuilt (that teardown was the source of the flicker
// on the old multi-page version). Each view's init() — and therefore
// its data fetch — only runs the first time that view is actually
// shown, not on initial page load, so switching views is instant but
// nothing is fetched before it's needed.

const Router = (() => {
  const views = {
    standings: { started: false, init: () => StandingsView.init() },
    'record-book': { started: false, init: () => RecordBookView.init() },
  };

  function currentViewFromHash() {
    const hash = location.hash.replace('#', '');
    return views[hash] ? hash : 'standings';
  }

  function activate(name) {
    Object.keys(views).forEach((key) => {
      const isActive = key === name;
      document.getElementById(`view-${key}`).hidden = !isActive;
      document
        .querySelector(`.site-nav a[data-view="${key}"]`)
        .classList.toggle('is-active', isActive);
    });

    const view = views[name];
    if (!view.started) {
      view.started = true;
      view.init();
    }
  }

  function init() {
    window.addEventListener('hashchange', () => activate(currentViewFromHash()));
    activate(currentViewFromHash());
  }

  return { init };
})();

Router.init();