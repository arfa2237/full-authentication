/* info-theme.js — theme toggle for the standalone disease-info pages
   Uses the SAME class (dark-theme) and localStorage key (theme) as
   the main site, so the preference stays consistent across all pages. */
document.addEventListener('DOMContentLoaded', function () {
    var themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    var body = document.body;

    function setIcon(isDark) {
        themeToggle.textContent = isDark ? '☀️' : '🌙';
    }

    var currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        body.classList.add('dark-theme');
        setIcon(true);
    } else {
        setIcon(false);
    }

    themeToggle.addEventListener('click', function () {
        body.classList.toggle('dark-theme');
        var isDark = body.classList.contains('dark-theme');
        setIcon(isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
});