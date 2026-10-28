(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#site-nav');
  if (menuButton && menu) {
    const closeMenu = () => {
      menu.classList.remove('is-open');
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Открыть меню');
    };
    menuButton.addEventListener('click', () => {
      const open = menuButton.getAttribute('aria-expanded') !== 'true';
      menu.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    });
    menu.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menu.classList.contains('is-open')) {
        closeMenu();
        menuButton.focus();
      }
    });
  }

  document.querySelectorAll('[data-print]').forEach((button) => {
    button.addEventListener('click', () => window.print());
  });

  const cards = [...document.querySelectorAll('[data-recipe-card]')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const search = document.querySelector('#recipe-search');
  const count = document.querySelector('[data-results-count]');
  const noResults = document.querySelector('[data-no-results]');
  if (!cards.length || !buttons.length || !search || !count || !noResults) return;

  const allowed = new Set(buttons.map((button) => button.dataset.filter));
  let active = new URLSearchParams(window.location.search).get('category') || 'all';
  if (!allowed.has(active)) active = 'all';

  const normalize = (text) => text.toLocaleLowerCase('ru').replaceAll('ё', 'е').trim();
  const recipeWord = (number) => {
    if (number % 10 === 1 && number % 100 !== 11) return 'рецепт';
    if ([2, 3, 4].includes(number % 10) && ![12, 13, 14].includes(number % 100)) return 'рецепта';
    return 'рецептов';
  };

  const render = () => {
    const query = normalize(search.value);
    let visible = 0;
    cards.forEach((card) => {
      const matchesCategory = active === 'all' || card.dataset.categories.split(' ').includes(active);
      const matchesSearch = !query || normalize(card.dataset.search).includes(query);
      card.hidden = !(matchesCategory && matchesSearch);
      if (!card.hidden) visible += 1;
    });
    buttons.forEach((button) => {
      const isActive = button.dataset.filter === active;
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-pressed', String(isActive));
    });
    count.textContent = `${visible} ${recipeWord(visible)}`;
    noResults.hidden = visible !== 0;
  };

  const setCategory = (category) => {
    active = allowed.has(category) ? category : 'all';
    const url = new URL(window.location.href);
    if (active === 'all') url.searchParams.delete('category');
    else url.searchParams.set('category', active);
    window.history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
    render();
  };

  buttons.forEach((button) => button.addEventListener('click', () => setCategory(button.dataset.filter)));
  search.addEventListener('input', render);
  document.querySelectorAll('[data-category-link]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      setCategory(link.dataset.categoryLink);
      document.querySelector('#recipes').scrollIntoView({ behavior: 'smooth' });
    });
  });
  document.querySelector('[data-clear-filters]')?.addEventListener('click', () => {
    search.value = '';
    setCategory('all');
    search.focus();
  });
  window.addEventListener('popstate', () => {
    const category = new URLSearchParams(window.location.search).get('category') || 'all';
    active = allowed.has(category) ? category : 'all';
    render();
  });
  render();
})();
