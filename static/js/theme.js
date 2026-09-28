// Apply the saved theme before the first paint, as on the original storefront.
document.documentElement.classList.toggle('dark', (localStorage.getItem('audia-theme') || 'dark') === 'dark');
