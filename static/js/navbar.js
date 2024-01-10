document.addEventListener("DOMContentLoaded", function(){
    // Get the navbar element
    const navbar = document.querySelector('.navbar');

    // Listen for the scroll event
    window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('opaque');
    } else {
        navbar.classList.remove('opaque');
    }
    });

})