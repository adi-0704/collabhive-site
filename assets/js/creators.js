// CollabHive — creator directory renderer.
// Renders creator cards into [data-creators] containers from CH.data.list('creators').
// - <div data-creators data-limit="8"></div>   -> preview (first N)
// - <div data-creators data-directory></div>   -> full directory + search + niche filter
// - add data-bookable to either to attach a "Book" button (opens WhatsApp to owner)
(function () {
  'use strict';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
  }
  function initial(name) { return (name || '?').trim().charAt(0).toUpperCase(); }

  function card(c, bookable) {
    var html = '<div class="creator-card">' +
      '<div class="avatar">' + initial(c.name) + '</div>' +
      '<h3>' + esc(c.name) + '</h3>' +
      '<div class="handle">' + esc(c.handle) + '</div>' +
      '<span class="niche">' + esc(c.niche) + '</span>' +
      '<div class="meta"><b>' + esc(c.followers) + '</b> followers · ' + esc(c.city) + '</div>' +
      '<div class="meta" style="margin-top:4px;">' + esc(c.rate || 'Rate on request') + '</div>';
    if (bookable) {
      html += '<button type="button" class="btn btn-gold book-btn" data-handle="' + esc(c.handle) + '" data-name="' + esc(c.name) + '" data-niche="' + esc(c.niche) + '" data-city="' + esc(c.city) + '">Book this creator</button>';
    }
    html += '</div>';
    return html;
  }

  function render(list, el, bookable) {
    el.innerHTML = list.map(function (c) { return card(c, bookable); }).join('');
    if (!list.length) {
      el.innerHTML = '<p class="form-note" style="text-align:center;padding:24px;">No creators match. Check back soon or widen your filters.</p>';
    }
    if (bookable) {
      el.querySelectorAll('.book-btn').forEach(function (b) {
        b.addEventListener('click', function () {
          var brand = window.CH_BRAND || '';
          var msg = 'Hi CollabHive! I want to book ' + b.getAttribute('data-handle') +
            ' (' + b.getAttribute('data-niche') + ', ' + b.getAttribute('data-city') + ')';
          if (brand) msg += '.\nBrand: ' + brand;
          msg += '.\nPlease share availability & next steps.';
          if (window.CH && window.CH.data) {
            CH.data.add('bookings', {
              brand: brand || 'Unknown', creator: b.getAttribute('data-handle'),
              niche: b.getAttribute('data-niche'), city: b.getAttribute('data-city'), status: 'Pending'
            });
          }
          window.open((window.CH ? CH.wa : function (t) { return 'https://wa.me/918178022572?text=' + encodeURIComponent(t); })(msg), '_blank');
        });
      });
    }
  }

  var dataPromise = null;
  function load() {
    if (!dataPromise) {
      var p = (window.CH && window.CH.data)
        ? CH.data.list('creators')
        : fetch('data/creators.json').then(function (r) { return r.json(); });
      dataPromise = p.catch(function () { return []; });
    }
    return dataPromise;
  }

  function wireDirectory(container) {
    var input = document.querySelector('[data-creator-search]');
    var nicheSel = document.querySelector('[data-creator-niche]');
    var count = document.querySelector('[data-directory-count]');
    var bookable = container.hasAttribute('data-bookable');
    var all = [];

    load().then(function (data) {
      all = data;
      if (nicheSel) {
        var niches = [];
        data.forEach(function (c) { if (niches.indexOf(c.niche) === -1) niches.push(c.niche); });
        niches.forEach(function (n) {
          var o = document.createElement('option');
          o.value = n; o.textContent = n;
          nicheSel.appendChild(o);
        });
      }
      applyFilter();
    });

    function applyFilter() {
      var q = (input ? input.value : '').trim().toLowerCase();
      var n = nicheSel ? nicheSel.value : '';
      var list = all.filter(function (c) {
        var matchQ = !q || (c.name + ' ' + c.handle + ' ' + c.niche + ' ' + c.city).toLowerCase().indexOf(q) !== -1;
        var matchN = !n || c.niche === n;
        return matchQ && matchN;
      });
      render(list, container, bookable);
      if (count) count.textContent = list.length + (list.length === 1 ? ' creator' : ' creators');
    }

    if (input) input.addEventListener('input', applyFilter);
    if (nicheSel) nicheSel.addEventListener('change', applyFilter);
  }

  function init() {
    document.querySelectorAll('[data-creators][data-directory]').forEach(wireDirectory);
    document.querySelectorAll('[data-creators]:not([data-directory])').forEach(function (el) {
      var limit = parseInt(el.getAttribute('data-limit'), 10) || 8;
      var bookable = el.hasAttribute('data-bookable');
      load().then(function (data) { render(data.slice(0, limit), el, bookable); });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
