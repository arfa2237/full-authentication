// static/form.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  const firstName = document.getElementById("first-name-input");
  const lastName = document.getElementById("last-name-input");
  const username = document.getElementById("username-input");
  const email = document.getElementById("email-input");
  const password = document.getElementById("password-input");

  const errorBox = document.getElementById("form-errors");

  function markIncorrect(groupId) {
    const group = document.getElementById(groupId);
    if (group) group.classList.add("incorrect");
  }

  function clearIncorrect(groupId) {
    const group = document.getElementById(groupId);
    if (group) group.classList.remove("incorrect");
  }

  function renderErrors(errors) {
    let html = "<ul>";
    errors.forEach(err => {
      html += `<li>${err}</li>`;
    });
    html += "</ul>";
    errorBox.innerHTML = html;
    errorBox.style.display = "block";   
    errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  //  Password Strength 
 
  function getStrength(pwd) {
    let score = 0;
    if (pwd.length >= 8)  score++;
    if (pwd.length >= 12) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[a-z]/.test(pwd)) score++;
    if (/\d/.test(pwd))    score++;
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(pwd)) score++;
    if (score <= 2) return { label: 'Weak',   color: '#f06272', width: '25%' };
    if (score <= 4) return { label: 'Fair',   color: '#ffb74d', width: '55%' };
    if (score <= 5) return { label: 'Good',   color: '#64b5f6', width: '75%' };
    return              { label: 'Strong', color: '#43a047', width: '100%' };
  }
  // Inject meter HTML right after the password field's parent element
  const meter = document.createElement('div');
  meter.id = 'pwd-strength-meter';
  meter.style.cssText = 'margin-top:6px;display:none;';
  meter.innerHTML = `
    <div style="height:4px;background:#e8ecf7;border-radius:4px;overflow:hidden;">
      <div id="pwd-strength-bar" style="height:100%;width:0;border-radius:4px;transition:width 0.3s,background 0.3s;"></div>
    </div>
    <span id="pwd-strength-label" style="font-size:10px;font-weight:600;color:#6b7db3;margin-top:3px;display:block;"></span>
  `;
  password.parentElement.insertAdjacentElement('afterend', meter);
 
  const strengthMeter = document.getElementById('pwd-strength-meter');
  const strengthBar   = document.getElementById('pwd-strength-bar');
  const strengthLabel = document.getElementById('pwd-strength-label');
 
  password.addEventListener('input', function () {
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
  });
 
  

  form.addEventListener("submit", function (e) {
    let errors = [];

    // Clear previous error states
    ["first-name-group","last-name-group","username-group","email-group","password-group"]
      .forEach(clearIncorrect);

    // First & Last name: only letters
    const nameRegex = /^[A-Za-z\s]+$/;
    if (!nameRegex.test(firstName.value.trim())) {
      errors.push("First name can contain only letters (A–Z). Numbers and symbols are not allowed.");
      markIncorrect("first-name-group");
    }

    if (!nameRegex.test(lastName.value.trim())) {
      errors.push("Last name can contain only letters (A–Z). Numbers and symbols are not allowed.");

      markIncorrect("last-name-group");
    }

    // Username: letters, numbers, dot, underscore (min 4)
    const usernameRegex = /^[a-zA-Z0-9._]{4,}$/;
    if (!usernameRegex.test(username.value.trim())) {
      errors.push("Username must be at least 4 characters long and can contain only letters, numbers, dots (.), and underscores (_).");
    }

    // Email: valid format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value.trim())) {
      errors.push("Enter a valid email address (e.g., name@gmail.com).");
      markIncorrect("email-group");
    }

// Password rules
// Check password
const password1 = password.value.trim();
if (!password1) {
    errors.push('Password is required.');
    const passwordInput = document.getElementById('password-input');
    if (passwordInput) passwordInput.parentElement.classList.add('incorrect');
} else {
    const passwordInput = document.getElementById('password-input');
    let hasPasswordError = false;
    
    // 1. Minimum length
    if (password1.length < 8) {
        errors.push('Password must be at least 8 characters.');
        hasPasswordError = true;
    }
    
    // 2. Maximum length (optional but good for security)
    if (password1.length > 128) {
        errors.push('Password cannot exceed 128 characters.');
        hasPasswordError = true;
    }
    
    // 3. At least one uppercase letter
    if (!/[A-Z]/.test(password1)) {
        errors.push('Password must contain at least one uppercase letter (A-Z).');
        hasPasswordError = true;
    }
    
    // 4. At least one lowercase letter
    if (!/[a-z]/.test(password1)) {
        errors.push('Password must contain at least one lowercase letter (a-z).');
        hasPasswordError = true;
    }
    
    // 5. At least one number
    if (!/\d/.test(password1)) {
        errors.push('Password must contain at least one number (0-9).');
        hasPasswordError = true;
    }
    
    // 6. At least one special character
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(password1)) {
        errors.push('Password must contain at least one special character (!@#$%^&* etc).');
        hasPasswordError = true;
    }
    
    // 7. No spaces allowed
    if (/\s/.test(password1)) {
        errors.push('Password cannot contain spaces.');
        hasPasswordError = true;
    }
    
    // 8. Common password check (optional)
    const commonPasswords = [
        'password', '12345678', 'qwerty123', 'admin123', 
        'welcome123', 'password123', 'abc123456'
    ];
    if (commonPasswords.includes(password1.toLowerCase())) {
        errors.push('Password is too common. Please choose a stronger password.');
        hasPasswordError = true;
    }
    
    // 9. Check for repeated characters (like "aaaaaaa")
    if (/(.)\1{3,}/.test(password1)) {
        errors.push('Password cannot have 4 or more repeated characters in a row.');
        hasPasswordError = true;
    }
    
    // 10. Check for sequential characters (like "123456" or "abcdef")
    const isSequential = /(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789)/i;
    if (isSequential.test(password1.toLowerCase())) {
        errors.push('Password cannot contain sequential characters (like "123" or "abc").');
        hasPasswordError = true;
    }
    
    // Apply or remove styling
    if (passwordInput) {
        if (hasPasswordError) {
            passwordInput.parentElement.classList.add('incorrect');
        } else {
            passwordInput.parentElement.classList.remove('incorrect');
        }
    }
}

    if (errors.length > 0) {
      e.preventDefault();
      renderErrors(errors);
      return;
    }

    // Clear errors if everything is valid
    errorBox.innerHTML = "";
    errorBox.style.display = "none";   
  });
});
