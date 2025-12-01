/* Lightweight enhancements for the Kiosker docs site */

document.addEventListener('DOMContentLoaded', () => {
  addCopyButtons();
  addKeyboardShortcuts();
});

function addCopyButtons() {
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach(block => {
    const pre = block.parentElement;
    if (pre.querySelector('.copy-button')) return;

    const button = document.createElement('button');
    button.className = 'copy-button md-button';
    button.textContent = 'Copy';
    button.addEventListener('click', () => {
      navigator.clipboard.writeText(block.textContent).then(() => {
        button.textContent = 'Copied!';
        setTimeout(() => (button.textContent = 'Copy'), 1600);
      });
    });

    pre.style.position = 'relative';
    pre.appendChild(button);
  });
}

function addKeyboardShortcuts() {
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
      const searchInput = document.querySelector('[data-md-component="search-query"]');
      if (searchInput) {
        event.preventDefault();
        searchInput.focus();
      }
    }
  });
}
