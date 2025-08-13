(function () {
  const root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
  const savedTheme = localStorage.getItem('theme');

  function applyTheme(theme) {
    const normalized = theme === 'light' || theme === 'dark' ? theme : 'auto';
    root.setAttribute('data-theme', normalized);
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) {
      metaTheme.setAttribute('content', normalized === 'light' ? '#0ea5e9' : '#38bdf8');
    }
  }

  function getEffectiveTheme() {
    const current = root.getAttribute('data-theme');
    if (current === 'light' || current === 'dark') return current;
    return prefersDark.matches ? 'dark' : 'light';
  }

  applyTheme(savedTheme || 'auto');

  prefersDark.addEventListener('change', () => {
    if (!savedTheme || savedTheme === 'auto') applyTheme('auto');
  });

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const effective = getEffectiveTheme();
      const next = effective === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      applyTheme(next);
    });
  }

  const menuToggle = document.getElementById('menu-toggle');
  const header = document.querySelector('.site-header');
  if (menuToggle && header) {
    menuToggle.addEventListener('click', () => {
      const expanded = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!expanded));
      header.setAttribute('data-nav-open', String(!expanded));
    });
  }

  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();