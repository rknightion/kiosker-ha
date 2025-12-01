/* Minimal SEO helpers for Kiosker documentation */

document.addEventListener('DOMContentLoaded', () => {
  ensureCanonical();
  ensureMeta('robots', 'index, follow');
  ensureMeta('language', 'en');
});

function ensureCanonical() {
  if (!document.querySelector('link[rel="canonical"]')) {
    const link = document.createElement('link');
    link.rel = 'canonical';
    link.href = window.location.href;
    document.head.appendChild(link);
  }
}

function ensureMeta(name, content) {
  if (!document.querySelector(`meta[name="${name}"]`)) {
    const meta = document.createElement('meta');
    meta.name = name;
    meta.content = content;
    document.head.appendChild(meta);
  }
}
