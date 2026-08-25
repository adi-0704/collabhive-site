// CollabHive — GA4 + Meta Pixel loader.
// No-op until IDs are set. Configure before this script runs, e.g. in a small
// inline block right after <head>:
//   <script>window.CH_ANALYTICS = { ga4Id: "G-XXXXXXXXXX", pixelId: "0000000000000000" };</script>
(function () {
  'use strict';
  var cfg = window.CH_ANALYTICS || {};
  var GA4_ID = cfg.ga4Id || '';
  var PIXEL_ID = cfg.pixelId || '';

  // GA4 (gtag)
  if (GA4_ID) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA4_ID);
  }

  // Meta Pixel
  if (PIXEL_ID) {
    (function (f, b, e, v, n, t, s) {
      if (f.fbq) return;
      n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n;
      n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
      t = b.createElement(e); t.async = true; t.src = v;
      s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    })(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init', PIXEL_ID);
    window.fbq('track', 'PageView');
  }

  // Lead events on WhatsApp form submit (both main.js and this handler fire)
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.getAttribute('data-wa-form')) return;
    var eventName = form.getAttribute('data-event') || 'lead_submitted';
    if (window.gtag) window.gtag('event', eventName, { event_category: 'lead' });
    if (window.fbq) window.fbq('track', 'Lead', { content_name: eventName });
  });
})();
