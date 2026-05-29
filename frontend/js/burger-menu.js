/**
 * Accessible Burger Menu
 * Handles mobile navigation menu toggle with keyboard support
 */

document.addEventListener('DOMContentLoaded', function () {
  const burgerBtn = document.getElementById('burgerMenuBtn');
  const navbarMenu = document.getElementById('navbarMenu');
  const menuBackdrop = document.getElementById('menuBackdrop');

  if (!burgerBtn || !navbarMenu || !menuBackdrop) {
    console.error('Burger menu elements not found');
    return;
  }

  // Get all nav links
  const navLinks = navbarMenu.querySelectorAll('a');

  /**
   * Check if we're on mobile by checking if burger button is displayed
   */
  function isMobileMenu() {
    return window.getComputedStyle(burgerBtn).display !== 'none';
  }

  /**
   * Hide/show links from tab order based on menu state
   */
  function updateTabindexForMobile() {
    if (!isMobileMenu()) {
      // Desktop: always ensure links are tabbable (remove tabindex) and visible
      navLinks.forEach(link => {
        link.removeAttribute('tabindex');
      });
      navbarMenu.removeAttribute('aria-hidden');
      return;
    }

    // Mobile: check if menu is open
    const isMenuOpen = navbarMenu.classList.contains('open');
    navLinks.forEach(link => {
      if (isMenuOpen) {
        // Menu open: make links tabbable
        link.removeAttribute('tabindex');
      } else {
        // Menu closed: hide from tab order
        link.setAttribute('tabindex', '-1');
      }
    });

    // Update aria-hidden based on menu state
    navbarMenu.setAttribute('aria-hidden', !isMenuOpen);
  }

  // Initialize tabindex and aria-hidden on load
  updateTabindexForMobile();

  /**
   * Toggle the mobile menu visibility
   */
  function toggleMenu() {
    const isOpen = burgerBtn.getAttribute('aria-expanded') === 'true';
    burgerBtn.setAttribute('aria-expanded', !isOpen);
    burgerBtn.classList.toggle('active');
    navbarMenu.classList.toggle('open');
    menuBackdrop.classList.toggle('open');

    // Update icon
    const icon = burgerBtn.querySelector('i');
    if (!isOpen) {
      // Menu is now open - show close icon
      icon.classList.remove('ph-list');
      icon.classList.add('ph-x');
    } else {
      // Menu is now closed - show list icon
      icon.classList.remove('ph-x');
      icon.classList.add('ph-list');
    }

    if (!isOpen) {
      // Menu is now open
      // Set focus to first link for better accessibility
      const firstLink = navbarMenu.querySelector('a');
      if (firstLink) {
        firstLink.focus();
      }
    }

    // Update tabindex and aria-hidden based on new menu state
    updateTabindexForMobile();
  }

  /**
   * Close the menu
   */
  function closeMenu() {
    burgerBtn.setAttribute('aria-expanded', 'false');
    burgerBtn.classList.remove('active');
    navbarMenu.classList.remove('open');
    menuBackdrop.classList.remove('open');

    // Reset icon to list
    const icon = burgerBtn.querySelector('i');
    icon.classList.remove('ph-x');
    icon.classList.add('ph-list');

    // Update tabindex and aria-hidden based on menu state
    updateTabindexForMobile();

    burgerBtn.focus();
  }

  // Toggle menu on burger button click
  burgerBtn.addEventListener('click', toggleMenu);

  // Close menu when a link is clicked
  navLinks.forEach(link => {
    link.addEventListener('click', closeMenu);
  });

  /**
   * Handle keyboard events for accessibility
   */
  function handleKeyboardInMenu(event) {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeMenu();
      return;
    }

    // Handle Tab key to manage focus within menu
    if (event.key === 'Tab' && navbarMenu.classList.contains('open')) {
      const focusableElements = navbarMenu.querySelectorAll(
        'a, button, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement;

      // If Shift+Tab on first element, wrap to last
      if (event.shiftKey && activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
      // If Tab on last element, wrap to first
      else if (!event.shiftKey && activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }

  // Add keyboard event listener
  document.addEventListener('keydown', handleKeyboardInMenu);

  // Close menu when clicking on backdrop
  menuBackdrop.addEventListener('click', closeMenu);

  // Close menu when clicking outside
  document.addEventListener('click', function (event) {
    const isClickInsideNav = burgerBtn.contains(event.target) || navbarMenu.contains(event.target);
    if (!isClickInsideNav && navbarMenu.classList.contains('open')) {
      closeMenu();
    }
  });

  // Update tabindex when window is resized (mobile <-> desktop)
  window.addEventListener('resize', updateTabindexForMobile);
});
