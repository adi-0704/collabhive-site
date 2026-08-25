// CollabHive — data layer.
// Demo mode (default): creators from data/creators.json, brands/bookings seeded,
//   writes go to localStorage (your own browser only — for previewing the flow).
// Live mode: set  window.CH_API = { base: "<Apps Script exec URL>", adminKey: "<secret>" }
//   in the page <head>, and all reads/writes go to Google Sheets via Apps Script.
(function () {
  'use strict';
  var API = window.CH_API = window.CH_API || {};
  var base = (API.base || '').replace(/\/$/, '');
  function adminKey() { return (window.CH_API && window.CH_API.adminKey) || 'collabhive'; }
  var WA_NUMBER = '918178022572';

  var DEMO_BRANDS = [
    { timestamp: '2026-08-24', business: 'UrbanBrew', category: 'Food & Beverage', city: 'Delhi', budget: '₹10,000 – ₹25,000', goal: 'Footfall / visits', status: 'Active' },
    { timestamp: '2026-08-24', business: 'FitKart', category: 'Fitness & Wellness', city: 'Gurugram', budget: '₹25,000 – ₹50,000', goal: 'Sales & conversions', status: 'Active' },
    { timestamp: '2026-08-25', business: 'Glowly', category: 'Fashion & Beauty', city: 'Delhi', budget: 'Under ₹10,000', goal: 'Brand awareness', status: 'Active' },
    { timestamp: '2026-08-25', business: 'The Green Table', category: 'Food & Beverage', city: 'Noida', budget: '₹10,000 – ₹25,000', goal: 'Engagement', status: 'Active' }
  ];

  var DEMO_BOOKINGS = [
    { timestamp: '2026-08-25', brand: 'UrbanBrew', creator: '@aarav.eats', niche: 'Food & Beverage', city: 'Delhi', status: 'Pending' },
    { timestamp: '2026-08-25', brand: 'FitKart', creator: '@kabir.fits', niche: 'Fitness & Wellness', city: 'Gurugram', status: 'Confirmed' },
    { timestamp: '2026-08-25', brand: 'Glowly', creator: '@sanya.glow', niche: 'Beauty', city: 'Delhi', status: 'Pending' }
  ];

  function lsGet(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function lsSet(k, v) { localStorage.setItem(k, JSON.stringify(v)); }

  function demoCreators() {
    return fetch('data/creators.json').then(function (r) { return r.json(); }).catch(function () { return []; });
  }

  function apiGet(params) {
    return fetch(base + '?' + params).then(function (r) { return r.json(); });
  }

  // list(sheet) -> Promise<Array>  (creators is public; brands/bookings need key in live mode)
  function list(sheet) {
    if (base) {
      var p = 'action=list&sheet=' + encodeURIComponent(sheet);
      if (sheet !== 'creators' && adminKey()) p += '&key=' + encodeURIComponent(adminKey());
      return apiGet(p).then(function (d) { return d.rows || []; });
    }
    if (sheet === 'creators') {
      return demoCreators().then(function (json) {
        var extra = lsGet('ch_creators') || [];
        return json.concat(extra);
      });
    }
    if (sheet === 'brands') return Promise.resolve(lsGet('ch_brands') || DEMO_BRANDS.slice());
    if (sheet === 'bookings') return Promise.resolve(lsGet('ch_bookings') || DEMO_BOOKINGS.slice());
    return Promise.resolve([]);
  }

  // add(sheet, row) -> Promise<{ok}>
  function add(sheet, row) {
    row = row || {};
    row.timestamp = row.timestamp || new Date().toISOString();
    if (base) {
      return fetch(base + '?action=add&sheet=' + encodeURIComponent(sheet), {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(row)
      }).then(function (r) { return r.json(); });
    }
    var k = 'ch_' + sheet;
    var cur = (lsGet(k) || (sheet === 'brands' ? DEMO_BRANDS : (sheet === 'bookings' ? DEMO_BOOKINGS : []))).slice();
    cur.push(row);
    lsSet(k, cur);
    return Promise.resolve({ ok: true });
  }

  // stats() -> Promise<{brands, creators, bookings}>
  function stats() {
    if (base) return apiGet('action=stats&key=' + encodeURIComponent(adminKey()));
    return Promise.all([list('brands'), list('creators'), list('bookings')]).then(function (a) {
      return { brands: a[0].length, creators: a[1].length, bookings: a[2].length };
    });
  }

  function wa(text) { return 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(text); }

  window.CH = window.CH || {};
  window.CH.data = { list: list, add: add, stats: stats, isLive: !!base, adminKey: adminKey };
  window.CH.wa = wa;
  window.CH.WA_NUMBER = WA_NUMBER;
})();
