document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('signin-form');
    const emailField = document.getElementById('floatingInput');
    const passwordField = document.getElementById('floatingPassword');
    const showPasswordCheck = document.getElementById('showPasswordCheck');

    // Function to check if a field is empty
    function checkIfEmpty(field) {
        if (field.value.trim() === '') {
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    }

    // Real-time validation
    emailField.addEventListener('input', () => checkIfEmpty(emailField));
    passwordField.addEventListener('input', () => checkIfEmpty(passwordField));

    // Validation on form submit
    form.addEventListener('submit', (event) => {
        let valid = true;
        if (emailField.value.trim() === '') {
            emailField.classList.add('is-invalid');
            valid = false;
        }
        if (passwordField.value.trim() === '') {
            passwordField.classList.add('is-invalid');
            valid = false;
        }
        if (!valid) {
            event.preventDefault();
        }
    });

    // Toggle password visibility
    showPasswordCheck.addEventListener('change', function () {
        const type = this.checked ? 'text' : 'password';
        passwordField.setAttribute('type', type);
    });
});