(() => {
  const menu = document.querySelector('#primary-nav');
  const button = document.querySelector('.menu-toggle');
  if (menu && button) {
    const close = () => { menu.classList.remove('is-open'); button.setAttribute('aria-expanded', 'false'); };
    button.addEventListener('click', () => {
      const open = menu.classList.toggle('is-open');
      button.setAttribute('aria-expanded', String(open));
    });
    menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', close));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape') close(); });
    document.addEventListener('click', (event) => {
      if (!menu.contains(event.target) && !button.contains(event.target)) close();
    });
  }
})();
