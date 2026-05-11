// staff-password-validation.js
// Password validation for Staff Registration page (TIG Gujranwala)

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

  if (pwd.length < passwordRules.minLength)
    errors.push(`Password must be at least ${passwordRules.minLength} characters.`);

  if (pwd.length > passwordRules.maxLength)
    errors.push(`Password cannot exceed ${passwordRules.maxLength} characters.`);

  if (!passwordRules.hasUppercase.test(pwd))
    errors.push('Password must contain at least one uppercase letter (A–Z).');

  if (!passwordRules.hasLowercase.test(pwd))
    errors.push('Password must contain at least one lowercase letter (a–z).');

  if (!passwordRules.hasNumber.test(pwd))
    errors.push('Password must contain at least one number (0–9).');

  if (!passwordRules.hasSpecial.test(pwd))
    errors.push('Password must contain at least one special character (!@#$%^&* etc).');

  if (passwordRules.noSpaces.test(pwd))
    errors.push('Password cannot contain spaces.');

  if (passwordRules.commonPasswords.includes(pwd.toLowerCase()))
    errors.push('Password is too common. Please choose a stronger one.');

  if (/(.)\1{3,}/.test(pwd))
    errors.push('Password cannot have 4 or more repeated characters in a row.');

  const isSequential = /(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789)/i;
  if (isSequential.test(pwd.toLowerCase()))
    errors.push('Password cannot contain sequential characters (like "123" or "abc").');

  return errors;
}

// ─── Strength meter helper ────────────────────────────────────────────────────
function getStrength(password) {
  let score = 0;
  if (password.length >= 8)  score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/\d/.test(password))    score++;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(password)) score++;
  if (score <= 2) return { label: 'Weak',   color: '#f06272', width: '25%' };
  if (score <= 4) return { label: 'Fair',   color: '#ffb74d', width: '55%' };
  if (score <= 5) return { label: 'Good',   color: '#64b5f6', width: '75%' };
  return              { label: 'Strong', color: '#43a047', width: '100%' };
}

// ─── Inject strength meter HTML just after the password input-wrap ────────────
function injectStrengthMeter(passwordWrap) {
  const meter = document.createElement('div');
  meter.id = 'pwd-strength-meter';
  meter.style.cssText = `
    margin-top: 6px;
    display: none;
  `;
  meter.innerHTML = `
    <div style="height:4px;background:#e8ecf7;border-radius:4px;overflow:hidden;">
      <div id="pwd-strength-bar" style="height:100%;width:0;border-radius:4px;transition:width 0.3s,background 0.3s;"></div>
    </div>
    <span id="pwd-strength-label" style="font-size:10px;font-weight:600;color:#6b7db3;margin-top:3px;display:block;"></span>
  `;
  passwordWrap.parentElement.appendChild(meter);
}

// ─── Main init ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  const form          = document.querySelector('form');
  const passwordInput = form.querySelector('input[name="password"]');

  if (!form || !passwordInput) return;   // guard: only run on this page

  // ── 1. Inject error box above the submit button ───────────────────────────
  const submitBtn = form.querySelector('.btn-register');
  const errorBox  = document.createElement('div');
  errorBox.id = 'pwd-error-box';
  errorBox.style.cssText = `
    display: none;
    background: #fff0f1;
    border: 1px solid #f06272;
    color: #c62828;
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 12px;
    margin-top: 14px;
    line-height: 1.7;
  `;
  submitBtn.parentElement.insertBefore(errorBox, submitBtn);

  // ── 2. Inject strength meter ──────────────────────────────────────────────
  const passwordWrap = passwordInput.closest('.input-wrap');
  injectStrengthMeter(passwordWrap);

  const strengthMeter = document.getElementById('pwd-strength-meter');
  const strengthBar   = document.getElementById('pwd-strength-bar');
  const strengthLabel = document.getElementById('pwd-strength-label');

  // ── 3. Live strength update while typing ──────────────────────────────────
  passwordInput.addEventListener('input', function () {
    const val = this.value;

    if (!val) {
      strengthMeter.style.display = 'none';
      return;
    }

    strengthMeter.style.display = 'block';
    const s = getStrength(val);
    strengthBar.style.width      = s.width;
    strengthBar.style.background = s.color;
    strengthLabel.style.color    = s.color;
    strengthLabel.textContent    = s.label;

    // Remove red border once user starts fixing
    passwordWrap.style.borderColor = '';
  });

  // ── 4. Validate on submit ─────────────────────────────────────────────────
  form.addEventListener('submit', function (e) {

    // Clear previous error state
    errorBox.style.display  = 'none';
    errorBox.innerHTML      = '';
    passwordWrap.style.borderColor = '';
    passwordWrap.style.boxShadow   = '';

    const errors = validatePassword(passwordInput.value);

    if (errors.length > 0) {
      e.preventDefault();   // block Django form submission

      // Highlight the password field (uses your --danger var)
      passwordWrap.style.borderColor = '#f06272';
      passwordWrap.style.boxShadow   = '0 0 0 3px rgba(240,98,114,0.15)';

      // Build error list
      let html = '<div style="display:flex;gap:8px;align-items:flex-start;">'
               + '<i class="fa-solid fa-circle-xmark" style="margin-top:2px;flex-shrink:0;"></i>'
               + '<ul style="margin:0;padding-left:16px;">';
      errors.forEach(err => { html += `<li>${err}</li>`; });
      html += '</ul></div>';

      errorBox.innerHTML      = html;
      errorBox.style.display  = 'block';
      errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });

  // ── 5. Clear error highlight when user focuses the field again ────────────
  passwordInput.addEventListener('focus', function () {
    passwordWrap.style.borderColor = '';
    passwordWrap.style.boxShadow   = '';
    if (errorBox.style.display !== 'none') {
      errorBox.style.display = 'none';
      errorBox.innerHTML     = '';
    }
  });

});