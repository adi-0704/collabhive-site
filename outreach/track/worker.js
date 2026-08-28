// CollabHive Outreach — open/click tracker (Cloudflare Worker, FREE tier).
//
// Deploy to https://workers.cloudflare.com (free, no card needed):
//   1. Create a new Worker (name it e.g. "collabhive-track").
//   2. Paste this entire file in. Save + deploy.
//   3. Note your Worker URL, e.g. https://collabhive-track.NAMESPACE.workers.dev
//
// How emails use it (implied in templates/config):
//   * Tracking pixel (open):  <img src="https://collabhive-track.../o?e=base64(email)&c=campaign&brand=slug">
//   * Click redirect:         https://collabhive-track.../r?u=<encoded target>&e=...&c=...
//
// It logs each hit to a per-day JSONL "file" via KV (optional) or just returns
// the redirect. For a data-only version, each hit is appended to the response
// and can be captured by a logging endpoint. To keep it FREE and simple, this
// worker also supports writing to Cloudflare KV (free) under namespace "TRACK".
//
// NOTE: If you don't want KV, hit the /h path which just records nothing and
// returns 1x1 gif for opens. We'll ALSO reconcile opens via Gmail replies
// (already built) as the fallback signal.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const q = (p, d) => url.searchParams.get(p) || d;
    const email = q('e', '');
    const campaign = q('c', '');
    const brand = q('b', '');

    // Record hit to KV if configured.
    const store = env.TRACK;
    if (store) {
      const day = new Date().toISOString().slice(0, 10);
      const key = `${day}:${brand || 'brand'}:${campaign || 'camp'}`;
      const cur = await store.get(key).then(v => (v ? parseInt(v, 10) : 0)).catch(() => 0);
      await store.put(key, String(cur + 1), { expirationTtl: 60 * 86400 }).catch(() => {});
      const tot = await store.get('tot:' + day).then(v => (v ? parseInt(v, 10) : 0)).catch(() => 0);
      await store.put('tot:' + day, String(tot + 1), { expirationTtl: 60 * 86400 }).catch(() => {});
    }

    // Open pixel: return a 1x1 transparent GIF.
    if (path === '/o' || path === '/h') {
      const gif = Uint8Array.from([0x47,0x49,0x46,0x38,0x39,0x61,0x01,0x00,0x01,0x00,
        0x80,0x00,0x00,0x00,0x00,0x00,0xff,0xff,0xff,0x21,0xf9,0x04,0x01,0x00,0x00,
        0x00,0x00,0x2c,0x00,0x00,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0x02,0x02,0x44,
        0x01,0x00,0x3b]);
      return new Response(gif, { headers: { 'Content-Type': 'image/gif', 'Cache-Control': 'no-store' } });
    }

    // Click redirect.
    if (path === '/r') {
      const target = q('u', 'https://adi-0704.github.io/collabhive-site/');
      // Safety: only allow our known domains.
      try {
        const t = new URL(target);
        if (!['adi-0704.github.io', 'docs.google.com'].includes(t.hostname)) {
          return new Response('Blocked', { status: 403 });
        }
      } catch (e) { return new Response('Bad URL', { status: 400 }); }
      return Response.redirect(target, 302);
    }

    return new Response('ok', { status: 200 });
  },
};
