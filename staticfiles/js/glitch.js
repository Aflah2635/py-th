function showGlitchError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'glitch-effect text-neon-pink p-4 mb-4 border border-neon-pink rounded-lg';
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);
  setTimeout(() => errorDiv.remove(), 3000);
} 