// CollabHive — data layer.
// Backend priority: Supabase > Google Sheets (Apps Script) > demo (local JSON + localStorage).
// Supabase: set window.CH_API.supabaseUrl + supabaseAnonKey (see backend/SUPABASE.md).
(function () {
  'use strict';
  var API = window.CH_API = window.CH_API || {};
  var base = (API.base || '').replace(/\/$/, '');
  function adminKey() { return (window.CH_API && window.CH_API.adminKey) || 'collabhive'; }
  var WA_NUMBER = '918178022572';

  function lsGet(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function lsSet(k, v) { localStorage.setItem(k, JSON.stringify(v)); }

  var FILES = { creators: 'data/creators.json', brands: 'data/brands.json', bookings: 'data/bookings.json' };

  // ---------- Supabase (PostgREST) ----------
  function sb() {
    var url = ((window.CH_API && window.CH_API.supabaseUrl) || '').replace(/\/$/, '');
    var key = (window.CH_API && window.CH_API.supabaseAnonKey) || '';
    return { url: url, key: key };
  }
  function supabaseActive() { var s = sb(); return !!(s.url && s.key); }

  function sgFetch(path, opts) {
    var s = sb();
    opts = opts || {};
    opts.headers = opts.headers || {};
    opts.headers['apikey'] = s.key;
    opts.headers['Authorization'] = 'Bearer ' + s.key;
    return fetch(s.url + path, opts);
  }
  function sgList(sheet) {
    return sgFetch('/rest/v1/' + sheet + '?select=*').then(function (r) { return r.json(); });
  }
  function sgAdd(sheet, row) {
    return sgFetch('/rest/v1/' + sheet, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Prefer': 'return=minimal' },
      body: JSON.stringify(row)
    }).then(function (r) { return { ok: r.ok }; });
  }
  function sgAdmin() {
    return sgFetch('/rest/v1/rpc/admin_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_key: adminKey() })
    }).then(function (r) { return r.json(); });
  }

  // ---------- Google Sheets (Apps Script) ----------
  function apiGet(params) {
    return fetch(base + '?' + params).then(function (r) { return r.json(); });
  }

  // ---------- Demo ----------
  function demoFile(sheet) {
    return fetch(FILES[sheet]).then(function (r) { return r.json(); }).catch(function () { return []; });
  }
  function demoList(sheet) {
    return demoFile(sheet).then(function (seed) {
      var extra = lsGet('ch_' + sheet + '_add') || [];
      return seed.concat(extra);
    });
  }

  // ---------- Public API ----------
  function list(sheet) {
    if (supabaseActive()) {
      if (sheet === 'creators') return sgList('creators');
      return sgAdmin().then(function (d) { return (d && d[sheet]) || []; });
    }
    if (base) {
      var p = 'action=list&sheet=' + encodeURIComponent(sheet);
      if (sheet !== 'creators' && adminKey()) p += '&key=' + encodeURIComponent(adminKey());
      return apiGet(p).then(function (d) { return d.rows || []; });
    }
    return FILES[sheet] ? demoList(sheet) : Promise.resolve([]);
  }

  function add(sheet, row) {
    row = row || {};
    row.timestamp = row.timestamp || new Date().toISOString();
    if (supabaseActive()) return sgAdd(sheet, row);
    if (base) {
      return fetch(base + '?action=add&sheet=' + encodeURIComponent(sheet), {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(row)
      }).then(function (r) { return r.json(); });
    }
    var k = 'ch_' + sheet + '_add';
    var cur = (lsGet(k) || []).slice();
    cur.push(row);
    lsSet(k, cur);
    return Promise.resolve({ ok: true });
  }

  function stats() {
    if (supabaseActive()) return sgAdmin().then(function (d) { return d.stats || {}; });
    if (base) return apiGet('action=stats&key=' + encodeURIComponent(adminKey()));
    return Promise.all([list('brands'), list('creators'), list('bookings')]).then(function (a) {
      return { brands: a[0].length, creators: a[1].length, bookings: a[2].length };
    });
  }

  function wa(text) { return 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(text); }

  var backend = supabaseActive() ? 'supabase' : (base ? 'sheets' : 'demo');

  window.CH = window.CH || {};
  window.CH.data = { list: list, add: add, stats: stats, isLive: backend !== 'demo', backend: backend, adminKey: adminKey };
  window.CH.wa = wa;
  window.CH.WA_NUMBER = WA_NUMBER;
})();
