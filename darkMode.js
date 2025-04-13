const toggleDarkMode = () => {
  const body = document.body;
  body.classList.toggle('dark-mode');
};

document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode); 