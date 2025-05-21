/**
 * This file handles user input validation for the registration form.
 */

document.addEventListener('DOMContentLoaded', () => {
    const username = document.querySelector('#id_username');
    const usernameRules = document.getElementById('username-rules');
    const userLen = document.getElementById('user-len');

    const pwd1 = document.querySelector('#id_password1');
    const pwd2 = document.querySelector('#id_password2');
    const matchMsg = document.querySelector('#match'); 

    const pwdRules = document.getElementById('password-rules');
    const len = document.getElementById('len');
    const upper = document.getElementById('upper');
    const num = document.getElementById('num');

    username?.addEventListener('input', () => {
        if (usernameRules.classList.contains('d-none')) {
            usernameRules.classList.remove('d-none');
        }
        
        const val = username.value;
        userLen.classList.toggle('text-success', val.length >= 4);
        userLen.classList.toggle('text-danger', val.length < 4);
        });

    pwd1?.addEventListener('input', () => {
        const val = pwd1.value;

        if (pwdRules.classList.contains('d-none')) {
        pwdRules.classList.remove('d-none');
        }

        len.classList.toggle('text-success', val.length >= 8);
        len.classList.toggle('text-danger', val.length < 8);

        upper.classList.toggle('text-success', /[A-Z]/.test(val));
        upper.classList.toggle('text-danger', !/[A-Z]/.test(val));

        num.classList.toggle('text-success', /\d/.test(val));
        num.classList.toggle('text-danger', !/\d/.test(val));
    });

    pwd2?.addEventListener('input', () => {
        const mismatch = pwd2.value !== pwd1.value;
        pwd2.setCustomValidity(mismatch ? 'Passwords do not match' : '');

        if (matchMsg) {
        matchMsg.classList.toggle('d-none', !mismatch);
        }
    });
});
  