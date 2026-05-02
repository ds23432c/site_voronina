document.addEventListener('DOMContentLoaded', () => {
  const navbarCollapse = document.querySelector('.navbar-collapse');

  if (navbarCollapse && window.bootstrap) {
    navbarCollapse.querySelectorAll('.nav-link, .btn').forEach((link) => {
      link.addEventListener('click', () => {
        if (navbarCollapse.classList.contains('show')) {
          const collapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse, { toggle: false });
          collapse.hide();
        }
      });
    });
  }

  document.querySelectorAll('form').forEach((form) => {
    const invalidField = form.querySelector('.is-invalid, [aria-invalid="true"]');
    if (invalidField && typeof invalidField.focus === 'function') {
      invalidField.focus({ preventScroll: true });
    }
  });
});