(function () {
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ambient = document.querySelector('.ambient');
  if (!ambient) return;

  if (!prefersReduced) {
    for (let i = 0; i < 22; i++) {
      const spark = document.createElement('span');
      spark.className = 'spark';
      spark.style.left = Math.random() * 100 + 'vw';
      spark.style.top = Math.random() * 100 + 'vh';
      spark.style.animationDelay = (-Math.random() * 3) + 's';
      spark.style.animationDuration = (2.3 + Math.random() * 2.8) + 's';
      ambient.appendChild(spark);
    }

    for (let i = 0; i < 8; i++) {
      const confetti = document.createElement('span');
      confetti.style.position = 'fixed';
      confetti.style.zIndex = '-1';
      confetti.style.left = Math.random() * 100 + 'vw';
      confetti.style.top = '-8vh';
      confetti.style.width = (5 + Math.random() * 5) + 'px';
      confetti.style.height = (10 + Math.random() * 8) + 'px';
      confetti.style.borderRadius = '3px';
      confetti.style.background = `hsl(${Math.floor(Math.random() * 360)}, 90%, 70%)`;
      confetti.style.opacity = '.55';
      confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
      confetti.style.animation = `floatConfetti ${10 + Math.random() * 10}s linear ${-Math.random() * 15}s infinite`;
      ambient.appendChild(confetti);
    }
  }

  document.querySelectorAll('[data-password-toggle]').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = document.getElementById(this.dataset.passwordToggle);
      if (!input) return;
      const visible = input.type === 'text';
      input.type = visible ? 'password' : 'text';
      this.textContent = visible ? 'Show' : 'Hide';
    });
  });

  document.querySelectorAll('[data-auto-focus]').forEach(input => {
    input.addEventListener('focus', function () { this.removeAttribute('readonly'); }, { once: true });
  });
})();
