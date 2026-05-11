// static/password-validation.js
// Reusable password validation for both registration and password reset

const passwordRules = {
  minLength: 8,
  maxLength: 128,
  hasUppercase: /[A-Z]/,
  hasLowercase: /[a-z]/,
  hasNumber: /\d/,
  hasSpecial: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/,
  noSpaces: /\s/,
  commonPasswords: [
    'password', '12345678', 'qwerty123', 'admin123', 
    'welcome123', 'password123', 'abc123456'
  ]
};

function validatePassword(password) {
  const errors = [];
  const pwd = password.trim();

  if (!pwd) {
    errors.push('Password is required.');
    return errors;
  }

  // 1. Minimum length
  if (pwd.length < passwordRules.minLength) {
    errors.push(`Password must be at least ${passwordRules.minLength} characters.`);
  }

  // 2. Maximum length
  if (pwd.length > passwordRules.maxLength) {
    errors.push(`Password cannot exceed ${passwordRules.maxLength} characters.`);
  }

  // 3. At least one uppercase letter
  if (!passwordRules.hasUppercase.test(pwd)) {
    errors.push('Password must contain at least one uppercase letter (A-Z).');
  }

  // 4. At least one lowercase letter
  if (!passwordRules.hasLowercase.test(pwd)) {
    errors.push('Password must contain at least one lowercase letter (a-z).');
  }

  // 5. At least one number
  if (!passwordRules.hasNumber.test(pwd)) {
    errors.push('Password must contain at least one number (0-9).');
  }

  // 6. At least one special character
  if (!passwordRules.hasSpecial.test(pwd)) {
    errors.push('Password must contain at least one special character (!@#$%^&* etc).');
  }

  // 7. No spaces allowed
  if (passwordRules.noSpaces.test(pwd)) {
    errors.push('Password cannot contain spaces.');
  }

  // 8. Not a common password
  if (passwordRules.commonPasswords.includes(pwd.toLowerCase())) {
    errors.push('Password is too common. Please choose a stronger password.');
  }

  // 9. No repeated characters (4+ in a row)
  if (/(.)\1{3,}/.test(pwd)) {
    errors.push('Password cannot have 4 or more repeated characters in a row.');
  }

  // 10. No sequential characters
  const isSequential = /(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789)/i;
  if (isSequential.test(pwd.toLowerCase())) {
    errors.push('Password cannot contain sequential characters (like "123" or "abc").');
  }

  return errors;
}

// For reset password page validation
document.addEventListener("DOMContentLoaded", function () {
  const resetForm = document.querySelector("form");
  const passwordInput = document.getElementById("password-input");
  const confirmPasswordInput = document.getElementById("confirm-password-input");
  const errorBox = document.getElementById("form-errors");

  // Only run on reset password page
  if (!passwordInput || !confirmPasswordInput || !errorBox) {
    return;
  }

  resetForm.addEventListener("submit", function (e) {
    let errors = [];

    // Clear previous error states
    const groups = document.querySelectorAll(".password-wrapper");
    groups.forEach(g => g.classList.remove("incorrect"));

    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    // Validate password strength
    const passwordErrors = validatePassword(password);
    if (passwordErrors.length > 0) {
      errors.push(...passwordErrors);
      passwordInput.parentElement.classList.add("incorrect");
    }

    // Validate confirm password
    if (!confirmPassword) {
      errors.push("Confirm password is required.");
      confirmPasswordInput.parentElement.classList.add("incorrect");
    }

    // Check if passwords match
    if (password && confirmPassword && password !== confirmPassword) {
      errors.push("Passwords do not match.");
      passwordInput.parentElement.classList.add("incorrect");
      confirmPasswordInput.parentElement.classList.add("incorrect");
    }

    // Display errors
    if (errors.length > 0) {
      e.preventDefault();
      let html = "<ul>";
      errors.forEach(err => {
        html += `<li>${err}</li>`;
      });
      html += "</ul>";
      errorBox.innerHTML = html;
      errorBox.style.display = "block";
      errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    // Clear errors if everything is valid
    errorBox.innerHTML = "";
    errorBox.style.display = "none";
  });
});