window.addEventListener('scroll', function() {
  const navbar = document.getElementById('navbar');
  const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

  if (scrollPosition > 0) {
    navbar.classList.add('navbar-scrolled');
  } else {
    navbar.classList.remove('navbar-scrolled');
  }
});