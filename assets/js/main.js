// CollabHive — shared interactions
(function () {
  'use strict';

  const WA_NUMBER = '918178022572'; // +91 81780 22572

  // Mobile nav toggle
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav-toggle');
  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
    });
  }

  // WhatsApp lead forms: compose a pre-filled message and open wa.me
  document.querySelectorAll('form[data-wa-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var lines = [];
      form.querySelectorAll('[name]').forEach(function (field) {
        var val = (field.value || '').trim();
        if (val) {
          var label = field.getAttribute('data-label') || field.name;
          lines.push(label + ': ' + val);
        }
      });
      if (!lines.length) {
        fieldHighlight(form);
        return;
      }
      var prefix = form.getAttribute('data-wa-form') || '';
      var message = prefix + '\n\n' + lines.join('\n');
      var url = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(message);
      window.open(url, '_blank');
      form.reset();
    });
  });

  function fieldHighlight(form) {
    form.querySelectorAll('input, textarea').forEach(function (f) {
      f.style.borderColor = 'hsl(0, 70%, 55%)';
      setTimeout(function () { f.style.borderColor = ''; }, 1600);
    });
  }

  // Set active nav link based on current path
  var path = (location.pathname.split('/').pop() || 'index.html');
  document.querySelectorAll('.nav-links a').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href === path) link.classList.add('active');
  });
})();
