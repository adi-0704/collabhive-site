// CollabHive — onboarding funnel tracker + social-proof widget.
// Records funnel events to the (optional) FREE Cloudflare Worker so the admin
// dashboard can show conversion + drop-off. Reads social proof from data/report.json.
(function () {
  'use strict';
  var WORKER = (window.CH_FUNNEL && window.CH_FUNNEL.eventsUrl) || '';

  function send(kind, email, ref) {
    if (!WORKER) return; // no worker configured -> tracking off (still logs locally)
    var payload = { kind: kind, email: email || '', ref: ref || '', source: 'site' };
    try {
      // Use sendBeacon for reliability on unmount.
      if (navigator.sendBeacon) {
        var blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
        navigator.sendBeacon(WORKER + '/events', blob);
      } else {
        fetch(WORKER + '/events', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), keepalive: true });
      }
    } catch (e) { /* ignore */ }
  }

  // Record form_view when the apply/brief forms are in view.
  document.querySelectorAll('[data-funnel]').forEach(function (el) {
    send(el.getAttribute('data-funnel'), el.getAttribute('data-email'), el.getAttribute('data-ref'));
  });
  // Track the influencer apply form link click.
  document.querySelectorAll('a[data-apply], #apply-online').forEach(function (a) {
    a.addEventListener('click', function () { send('form_view'); });
  });

  // Social proof widget: reads report.json -> proof section.
  var proofEl = document.querySelector('[data-social-proof]');
  if (proofEl) {
    fetch('../data/report.json', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var proof = (d.onboarding && d.onboarding.proof) || {};
        var creators = proof.creators_joined || 0;
        var campaigns = proof.campaigns_run || 0;
        proofEl.innerHTML =
          '<div class="proof-item"><span class="p-num">' + creators + '</span><span class="p-lbl">creators joined</span></div>' +
          '<div class="proof-item"><span class="p-num">' + campaigns + '</span><span class="p-lbl">campaigns run</span></div>';
      }).catch(function () { /* silent */ });
  }
})();
