/**
 * Accessible Burger Menu
 * Handles mobile navigation with keyboard support and screen reader accessibility
 */

class BurgerMenu {
  constructor() {
    this.burgerBtn = document.getElementById('burgerMenuBtn');
    this.navLinks = document.querySelector('.navbar-links');
    this.nav = document.querySelector('nav');
    this.isOpen = false;

    if (!this.burgerBtn || !this.navLinks) {
      console.warn('Burger menu elements not found');
      return;
    }

    this.init();
  }

  init() {
    // Click handler for burger button
    this.burgerBtn.addEventListener('click', () => this.toggleMenu());

    // Close menu when a link is clicked
    const links = this.navLinks.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('click', () => this.closeMenu());
    });

    // Close menu on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.closeMenu();
        this.burgerBtn.focus();
      }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (this.isOpen && !this.nav.contains(e.target)) {
        this.closeMenu();
      }
    });
  }

  toggleMenu() {
    if (this.isOpen) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }

  openMenu() {
    this.isOpen = true;
    this.navLinks.classList.add('open');
    this.burgerBtn.setAttribute('aria-expanded', 'true');
    this.burgerBtn.classList.add('active');

    // Trap focus within the menu (optional but improves accessibility)
    this.setupFocusTrap();
  }

  closeMenu() {
    this.isOpen = false;
    this.navLinks.classList.remove('open');
    this.burgerBtn.setAttribute('aria-expanded', 'false');
    this.burgerBtn.classList.remove('active');
  }

  setupFocusTrap() {
    const focusableElements = this.navLinks.querySelectorAll('a');
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    this.navLinks.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    });
  }
}

// Initialize the burger menu when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new BurgerMenu();
  });
} else {
  new BurgerMenu();
}
