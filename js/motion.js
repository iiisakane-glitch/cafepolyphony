/* Gentle, one-time entrances. Content remains visible without this enhancement. */
(() => {
  'use strict';
  if (!window.matchMedia || !('IntersectionObserver' in window) ||
      !('animate' in Element.prototype)) return;

  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const active = new Map();
  let observer;

  function stop() {
    observer?.disconnect();
    active.forEach(animation => animation.cancel());
    active.clear();
  }

  function enter(element, delay = 0) {
    if (preference.matches || element.contains(document.activeElement)) return;
    const animation = element.animate([
      { opacity: 0, transform: 'translateY(22px)' },
      { opacity: 1, transform: 'translateY(0)' }
    ], {
      duration: 720,
      delay,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
      fill: 'backwards'
    });
    active.set(element, animation);
    animation.onfinish = animation.oncancel = () => active.delete(element);
  }

  // Honour a change in the OS preference immediately, including running animations.
  preference.addEventListener('change', event => { if (event.matches) stop(); });
  window.addEventListener('pagehide', stop);
  document.addEventListener('focusin', event => {
    active.forEach((animation, element) => {
      if (element.contains(event.target)) animation.cancel();
    });
  });
  if (preference.matches) return;

  // Only animate the opening on a fresh visit, preserving deep links and restored scroll.
  if (!location.hash && window.scrollY < 40) {
    document.querySelectorAll('.hero-copy > :not(.hero-location)').forEach((element, index) => {
      enter(element, index * 75);
    });
    const photo = document.querySelector('.hero-photos');
    if (photo) enter(photo, 140);
  }

  observer = new IntersectionObserver(entries => {
    let order = 0;
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      // Skip elements already passed when following anchors or restoring a page.
      if (entry.boundingClientRect.bottom > 0) enter(entry.target, Math.min(order++ * 80, 160));
    });
  }, { threshold: 0, rootMargin: '0px 0px -32px 0px' });

  document.querySelectorAll([
    '.section-top', '.lunch-overview', '.lunch-discovery', '.food-card',
    '.parfait-poster', '.parfait-copy', '.baked-photo', '.baked-copy',
    '.event-story > picture', '.event-story > div', '.concept-intro',
    '.staff-grid > article', '.access-info', '.access-visual',
    '.contact-band', '.sns-layout > div'
  ].join(',')).forEach(element => observer.observe(element));
})();
