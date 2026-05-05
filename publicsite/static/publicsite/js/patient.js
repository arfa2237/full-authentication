let form = document.getElementById('form');
let user = document.getElementById('user');
let fname = document.getElementById('fname');
let dob = document.getElementById('dob');
let genderfield = document.getElementById('genderfield');
let gender = document.getElementsByName('gender');
let vcntype = document.getElementById('vcntype');
let phone = document.getElementById('phone');

form.addEventListener('submit', e => {
    e.preventDefault();

    let isValid = checkinputs();

    if(isValid) {
        alert("Form submitted successfully");
        form.reset();  //clear all fields
        window.location.reload();    //refresh page
    }
});

function checkinputs() {
    let uservalue = user.value.trim();
    let fnamevalue = fname.value.trim();
    let dobvalue = dob.value.trim();
    let vcntypevalue = vcntype.value.trim();
    let phonevalue = phone.value.trim();

    let valid = true;

    //user name validation..........
    if(uservalue === '') {
        setError(user, 'Patient name is required');
        valid = false;
    }
    else if (!/^[A-Za-z\s]+$/.test(uservalue)) {
    setError(user, 'Special characters and numbers are not allowed');
        valid = false;
    }
    else {
        setSuccess(user);
    }

    //father/guardian name validation.........
    if(fnamevalue === '') {
        setError(fname, 'This field is required');
        valid = false;
    }
    else if (!/^[A-Za-z\s]+$/.test(fnamevalue)) {
        setError(fname, 'Special characters and numbers are not allowed');
        valid = false;
    }
    else {
        setSuccess(fname);
    }

    //date of birth validation.................
    if(dobvalue === '') {
        setError(dob, 'This field is required ');
        valid = false;
    }
    else {
        setSuccess(dob);
    }

    //gender validation........................
    let genderselected = false;
    for(let i = 0; i < gender.length; i++) {
        if(gender[i].checked) {
            genderselected = true;
            break;
        }
    } 
    if(!genderselected) {
        setErrorRadio(genderfield, "Please select your gender");
        valid = false;
    }
    else {
        setSuccessRadio(genderfield);
    }

    //vaccine type validation...............
    if(vcntypevalue === '') {
        setError(vcntype, 'This field is required');
        valid = false;
    }
    else if (!/^[A-Za-z\s]+$/.test(vcntypevalue)) {
        setError(vcntype, 'Special characters and numbers are not allowed');
        valid = false;
    }
    else {
        setSuccess(vcntype);
    }

    //contact number validation...................
    if(phonevalue === '') {
        setError(phone, 'Contact number is required');
        valid = false;
    }
    else if (!/^\d+$/.test(phonevalue)) {
        setError(phone, 'Contact number must contain only digits');
        valid = false;
    }
    else if(phonevalue.length < 11 || phonevalue.length > 11) {
        setError(phone, 'Length must be 11 digits');
        valid = false;
    }
    else {
        setSuccess(phone);
    }

    return valid;
}

//Error handler for input fileds.......................................
function setError(input, message) {
    let field = input.parentElement;
    let errormsg = field.querySelector('.error');

    errormsg.innerText = message;
    field.classList.add('error');
    field.classList.remove('success');
}

function setSuccess(input) {
    let field = input.parentElement;
    let errormsg = field.querySelector('.error');

    errormsg.innerText = '';
    field.classList.add('success');
    field.classList.remove('error');
}

//Error handler for radio buttons.......................................
function setErrorRadio(field, message) {
    let errormsg = field.querySelector('.error');

    errormsg.innerText = message;
    field.classList.add('.error');
    field.classList.remove('.success');
}

function setSuccessRadio(field) {
    let errormsg = field.querySelector('.error');

    errormsg.innerText = "";
    field.classList.add('.success');
    field.classList.remove('.error');
}


