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