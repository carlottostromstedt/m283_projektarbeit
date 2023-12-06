document.addEventListener("DOMContentLoaded", function(){

    const form = document.forms.signUp;
    const passwordError = document.querySelector(".password-error")
    const passwordField = form.elements.password;
    const passwordConfirmationField = form.elements.password_confirmation;  
    
    form.addEventListener("submit", (event) => {
        // if the email field is valid, we let the form submit
        console.log(passwordField.value)
        console.log(passwordConfirmationField.value)
        if (passwordField.value != passwordConfirmationField.value) {
            event.preventDefault();
            showPasswordError();
            passwordField.value = "";
            passwordConfirmationField.value = "";
        } else if(!email.validity.valid){
            event.preventDefault();
        }
    });

    function showPasswordError(){
        passwordError.textContent = "Entered password needs to match confirmation."
        passwordError.className = "error active";
    }
})
