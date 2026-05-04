// 👁 Password Eye Toggle (SAFE & INDEPENDENT)
console.log("password-toggle.js loaded");

document.addEventListener("click", function (e) {
    const toggle = e.target.closest(".toggle-password");
    if (!toggle) return;

    const input = document.getElementById(toggle.dataset.target);
    if (!input) return;

    const eyeOpen = toggle.querySelector(".eye-open");
    const eyeClosed = toggle.querySelector(".eye-closed");

    if (input.type === "password") {
        input.type = "text";
        eyeOpen?.classList.remove("hidden");
        eyeClosed?.classList.add("hidden");
    } else {
        input.type = "password";
        eyeOpen?.classList.add("hidden");
        eyeClosed?.classList.remove("hidden");
    }
});
