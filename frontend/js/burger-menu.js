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

    burgerBtn.focus();
  }

  // Toggle menu on burger button click
  burgerBtn.addEventListener('click', toggleMenu);

  // Close menu when a link is clicked
  const navLinks = navbarMenu.querySelectorAll('a');
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
});
