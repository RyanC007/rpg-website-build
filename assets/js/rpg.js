/* ============================================================
   RPG SHARED JAVASCRIPT
   Ready, Plan, Grow! — readyplangrow.com
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── MOBILE NAV TOGGLE ── */
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      toggle.setAttribute('aria-expanded', isOpen);
    });
    // Close nav when a link is clicked
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
      });
    });
  }

  /* ── FAQ ACCORDION ── */
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    const question = item.querySelector('.faq-question');
    if (question) {
      question.addEventListener('click', function () {
        const isOpen = item.classList.contains('open');
        // Close all others
        faqItems.forEach(function (i) { i.classList.remove('open'); });
        // Toggle current
        if (!isOpen) { item.classList.add('open'); }
      });
    }
  });

  /* ── ACTIVE NAV LINK ── */
  const currentPath = window.location.pathname;
  const navAnchors = document.querySelectorAll('.nav-links a');
  navAnchors.forEach(function (a) {
    const href = a.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      a.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      a.classList.add('active');
    }
  });

  /* ── SMOOTH SCROLL FOR ANCHOR LINKS ── */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
