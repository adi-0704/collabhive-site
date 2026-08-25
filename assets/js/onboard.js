// CollabHive — onboarding capture.
// Records brand briefs + creator applications into the data layer, and stores the
// brand identity locally so the dashboard can greet the brand.
(function () {
  'use strict';

  function collect(form) {
    var d = {};
    form.querySelectorAll('[name]').forEach(function (f) {
      var v = (f.value || '').trim();
      if (v) d[f.getAttribute('data-label') || f.name] = v;
    });
    return d;
  }

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.getAttribute('data-wa-form')) return;
    var event = form.getAttribute('data-event') || '';
    var d = collect(form);

    if (event === 'brand_brief_submitted') {
      var brand = {
        business: d['Business'] || '',
        category: d['Category'] || '',
        city: d['City'] || '',
        budget: d['Budget'] || '',
        goal: d['Goal'] || '',
        link: d['Link'] || '',
        notes: d['Notes'] || ''
      };
      if (brand.business) localStorage.setItem('ch_brand', brand.business);
      if (window.CH && CH.data) CH.data.add('brands', brand);
    } else if (event === 'creator_application_submitted') {
      var creator = {
        name: d['Name'] || '',
        handle: d['Handle'] || '',
        niche: d['Niche'] || '',
        followers: d['Followers'] || '',
        city: d['City'] || '',
        links: d['Links'] || '',
        about: d['About'] || ''
      };
      if (window.CH && CH.data) CH.data.add('creators', creator);
    }
  });
})();
