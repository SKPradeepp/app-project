document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});
setTimeout(() => document.querySelectorAll('.flash').forEach(item => item.classList.add('fade')), 5500);
