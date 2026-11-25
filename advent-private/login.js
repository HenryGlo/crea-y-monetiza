(() => {
  const form = document.getElementById('access'), email = document.getElementById('email');
  const otp = document.getElementById('otp'), codeField = document.getElementById('code-field');
  const submit = document.getElementById('submit'), message = document.getElementById('message');
  const restart = document.getElementById('restart');
  let checking = false, busy = false;
  restart.addEventListener('click', () => {
    if (busy) return;
    checking = false; email.readOnly = false; otp.required = false; otp.value = '';
    codeField.hidden = true; restart.hidden = true; message.textContent = '';
    submit.textContent = 'Enviarme el código'; email.focus();
  });
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (busy) return;
    busy = true; submit.disabled = true; message.textContent = checking ? 'Comprobando tu código…' : 'Preparando tu acceso…';
    try {
      const response = await fetch('/calendario/api', {method:'POST', credentials:'same-origin',
        headers:{'Content-Type':'application/json'}, body:JSON.stringify({action: checking ? 'verify' : 'request', email:email.value.trim(), otp:otp.value.trim()})});
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.message || 'No pudimos completar el acceso. Intenta de nuevo en un minuto.');
      if (checking) { location.replace('/calendario/alumnas/'); return; }
      checking = true; email.readOnly = true; codeField.hidden = false; otp.required = true;
      restart.hidden = false; submit.textContent = 'Entrar a mis regalos';
      message.textContent = 'Si tu correo está en la lista de alumnas, recibirás el código. Puede tardar unos instantes.';
      otp.focus();
    } catch (error) { message.textContent = error.message; }
    finally { busy = false; submit.disabled = false; }
  });
})();
