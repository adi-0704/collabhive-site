"""CollabHive Outreach — test harness.

White-box unit tests + black-box mode runs. Uses a throwaway temp data dir and
stubs SMTP/IMAP/network so NO real email is sent and NO external service is hit.
Run:  python src/tests.py [module]
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Point at a temp data dir so we never touch live data.
_TEST_ROOT = Path(tempfile.mkdtemp(prefix="ch_outreach_test_"))
os.environ["OUTREACH_ROOT"] = str(_TEST_ROOT)
# Import package paths.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _mkdata(cfg=None):
    """Sandbox root already set via OUTREACH_ROOT; copy templates + seed data.
    Resets all data/*.json each call so tests don't leak state."""
    import src.common as common
    common.ROOT = _TEST_ROOT
    tpl_src = Path(__file__).resolve().parent.parent / "templates"
    (_TEST_ROOT / "templates").mkdir(parents=True, exist_ok=True)
    for f in tpl_src.glob("*"):
        shutil.copy(f, _TEST_ROOT / "templates")
    data = Path(__file__).resolve().parent.parent / "data"
    ddir = _TEST_ROOT / "data"
    shutil.rmtree(ddir, ignore_errors=True)
    ddir.mkdir(parents=True, exist_ok=True)
    for name in ("brands_seed.json", "creators_pool.json", "brand_briefs.json"):
        shutil.copy(data / name, ddir / name)
    shutil.copy(Path(__file__).resolve().parent.parent / "config.json", _TEST_ROOT / "config.json")
    return common


def _load_cfg():
    import src.common as common
    return common.load_config()


class TestCommon(unittest.TestCase):
    def setUp(self):
        self.common = _mkdata(None)
        self.cfg = _load_cfg()

    def test_load_config_valid(self):
        self.assertIn("smtp", self.cfg)
        self.assertIn("niches", self.cfg)
        self.assertGreater(len(self.cfg["niches"]["categories"]), 0)

    def test_save_load_roundtrip(self):
        p = _TEST_ROOT / "data" / "_t.json"
        self.common.save_json(p, {"a": 1})
        self.assertEqual(self.common.load_json(p), {"a": 1})

    def test_load_json_missing(self):
        self.assertEqual(self.common.load_json(_TEST_ROOT / "nope.json"), [])

    def test_scoring_helpers(self):
        from src.sales import _to_int, _slug  # noqa
        self.assertEqual(_to_int("₹15,000"), 15000)
        self.assertEqual(_to_int("1.2K"), 12)


class TestBrands(unittest.TestCase):
    def setUp(self):
        self.common = _mkdata(None)
        self.cfg = _load_cfg()
        # load a pool with emails
        pool = [
            {"name": "A", "niche": "Food & Beverage", "city": "Delhi", "website": "a.com",
             "email": "hi@a.com", "emails": ["hi@a.com"]},
            {"name": "B", "niche": "Fashion & Apparel", "city": "Mumbai", "website": "b.com",
             "email": "hi@b.com", "emails": ["hi@b.com"]},
        ]
        self.common.save_json(_TEST_ROOT / "data" / "brands_seed.json", pool)

    def test_select_targets_skips_sent(self):
        from src.brands import select_targets
        state = {"emailed_emails": ["hi@a.com"], "emailed_domains": ["a.com"]}
        sel, _ = select_targets(self.cfg, state, 10)
        self.assertEqual(len(sel), 1)
        self.assertEqual(sel[0]["email"], "hi@b.com")

    def test_select_targets_skips_bounced(self):
        from src.brands import select_targets
        state = {"bounced_emails": ["hi@b.com"]}
        sel, _ = select_targets(self.cfg, state, 10)
        self.assertEqual(len(sel), 1)
        self.assertEqual(sel[0]["email"], "hi@a.com")

    def test_select_targets_skips_dnc(self):
        from src.brands import select_targets
        self.common.save_json(_TEST_ROOT / "data" / "dnc.json",
                              [{"email": "hi@b.com"}])
        sel, _ = select_targets(self.cfg, {}, 10)
        self.assertEqual(len(sel), 1)

    def test_email_hygiene_asset(self):
        from src.brands import _is_good, emails_from_html
        self.assertFalse(_is_good("files@q.bundle.js", ""))
        self.assertTrue(_is_good("hello@brand.co.in", ""))
        got = emails_from_html("mailto:hi@x.com <a>files@q.bundle.js</a>", "x.com", 3)
        self.assertIn("hi@x.com", got)
        self.assertNotIn("files@q.bundle.js", got)

    def test_email_hygiene_notification_bots(self):
        from src.brands import _is_good
        self.assertFalse(_is_good("no-reply@aqualogica.in", ""))
        self.assertFalse(_is_good("back-in-stock@notifyboost.net", ""))
        self.assertFalse(_is_good("orders@bunai.com", ""))
        self.assertTrue(_is_good("support@wakefit.co", ""))
        self.assertTrue(_is_good("hello@urbanladder.com", ""))


class TestSales(unittest.TestCase):
    def setUp(self):
        self.common = _mkdata(None)
        self.cfg = _load_cfg()

    def test_match_briefs_returns_shortlist(self):
        from src.sales import match_briefs
        res = match_briefs(self.cfg)
        self.assertIn("matched", res)
        self.assertGreaterEqual(res.get("matched", 0), 0)

    def test_quote_math(self):
        from src.sales import build_quote
        quote = build_quote(self.cfg, {"brand": "X", "posts": 2},
                            [{"handle": "@a", "rate": 3000}, {"handle": "@b", "rate": 2000}])
        self.assertEqual(quote["creator_payout"], 10000)
        self.assertEqual(quote["commission"], 1000.0)
        self.assertEqual(quote["total"], 11000.0)

    def test_score_briefs_tiers(self):
        from src.sales import _score
        s = _score({"niche": "Food & Beverage", "city": "Delhi", "budget": "20000"},
                   {"niche": "Food & Beverage", "city": "Delhi", "followers": 20000, "rate": 2000})
        self.assertGreater(s, 0)


class TestMailerNoNetwork(unittest.TestCase):
    def setUp(self):
        self.common = _mkdata(None)
        self.cfg = _load_cfg()

    def test_render_subject_variants(self):
        from src.mailer import _pick_subject, _render, load_templates
        st, txt, html = load_templates(self.cfg)
        chosen = _pick_subject(self.cfg, {"name": "UniqBrandX"})
        subj, btxt, bhtml = _render(chosen, txt, html, {"name": "UniqBrandX", "niche": "Food"}, self.cfg)
        self.assertIn("UniqBrandX", subj)

    def test_render_opener_in_body(self):
        from src.mailer import _render, load_templates
        st, txt, html = load_templates(self.cfg)
        subj, btxt, bhtml = _render(st, txt, html,
                                    {"name": "Cafe", "niche": "Food & Beverage", "city": "Delhi"}, self.cfg)
        self.assertIn("Food & Beverage creators", btxt)

    def test_render_missing_tokens_safe(self):
        from src.mailer import _render, load_templates
        st, txt, html = load_templates(self.cfg)
        # templates reference {brief_url} etc — ensure format tolerant
        subj, btxt, bhtml = _render(st, txt, html, {"name": "X"}, self.cfg)
        self.assertTrue(btxt)

    def test_count_sent_last_hours(self):
        from src.mailer import count_sent_last_hours
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        s = {"sent_log": [{"ts": now.isoformat()}, {"ts": (now - timedelta(days=2)).isoformat()}]}
        self.assertEqual(count_sent_last_hours(s, 24), 1)

    def test_tracking_inject_no_worker(self):
        from src.mailer import _inject_tracking
        cfg = dict(self.cfg)
        cfg["tracking"] = {"enabled": True, "worker_url": ""}
        html = _inject_tracking("<a href='https://site.com'>x</a>", "a@b.com", {"name": "X"}, cfg)
        self.assertEqual(html, "<a href='https://site.com'>x</a>")

    def test_tracking_inject_with_worker(self):
        from src.mailer import _inject_tracking
        cfg = dict(self.cfg)
        cfg["tracking"] = {"enabled": True, "worker_url": "https://t.example.workers.dev"}
        html = _inject_tracking("<a href='https://adi-0704.github.io/x'>x</a>", "a@b.com", {"name": "X"}, cfg)
        self.assertIn("/o?", html)      # open pixel present
        self.assertIn("/r?u=", html)    # click redirect present


class TestGrowth(unittest.TestCase):
    def setUp(self):
        self.common = _mkdata(None)
        self.cfg = _load_cfg()

    def test_dnc_add_and_set(self):
        from src.growth import manage_dnc, dnc_set
        self.common.save_json(_TEST_ROOT / "data" / "dnc.json", [])
        res = manage_dnc(self.cfg, "please unsubscribe me", "spam@x.com")
        self.assertIn("spam@x.com", dnc_set(self.cfg))

    def test_pipeline_stages(self):
        from src.growth import pipeline_status
        self.common.save_json(_TEST_ROOT / "data" / "brand_briefs.json", [
            {"brand": "B1", "niche": "Food", "budget": "10000", "priority": 0.7}])
        rows = pipeline_status(self.cfg)
        self.assertTrue(rows)

    def test_sitemap_writes(self):
        from src.growth import generate_sitemap
        # output_dir is '../seo-pages' relative to ROOT (sandbox), i.e. sibling.
        seo_dir = _TEST_ROOT.parent / "seo-pages"
        seo_dir.mkdir(parents=True, exist_ok=True)
        (seo_dir / "food-in-delhi.html").write_text("x", encoding="utf-8")
        res = generate_sitemap(self.cfg)
        self.assertGreater(res.get("urls", 0), 0)
        self.assertTrue((seo_dir / "sitemap.xml").exists())

    def test_ab_winner(self):
        from src.growth import ab_winner
        self.common.save_json(_TEST_ROOT / "data" / "state.json", {"sent_log": []})
        res = ab_winner(self.cfg)
        self.assertIn("winner", res)


class TestProtect(unittest.TestCase):
    def test_throttle_circuit(self):
        from src.protect import Throttle
        th = Throttle(backoff_after_failures=3)
        self.assertFalse(th.is_circuit_open())
        th.record(ok=False)
        th.record(ok=False)
        th.record(ok=False)
        self.assertTrue(th.is_circuit_open())

    def test_record_success_resets(self):
        from src.protect import Throttle
        th = Throttle(backoff_after_failures=3)
        th.record(ok=False)
        th.record(ok=True)
        self.assertEqual(th._failures, 0)


class TestOnboarding(unittest.TestCase):
    def setUp(self):
        self.common = _mkdata(None)
        self.cfg = _load_cfg()

    def test_record_and_funnel(self):
        from src import onboarding as ob
        ob.record_event(self.cfg, "form_view", "a@x.com")
        ob.record_event(self.cfg, "creator_submit", "c@y.com")
        ob.record_event(self.cfg, "brand_submit", "b@z.com")
        ob.record_event(self.cfg, "approve", "c@y.com")
        f = ob.funnel_analytics(self.cfg)
        self.assertEqual(f["form_views"], 1)
        self.assertEqual(f["creator_submissions"], 1)
        self.assertEqual(f["approve_rate_pct"], 100.0)

    def test_seed_events_idempotent(self):
        from src import onboarding as ob
        r1 = ob.seed_events_from_data(self.cfg)
        r2 = ob.seed_events_from_data(self.cfg)
        self.assertEqual(r2["added"], 0)  # second run adds nothing

    def test_social_proof_counts(self):
        from src import onboarding as ob
        ob.record_event(self.cfg, "creator_submit", "c@y.com")
        ob.record_event(self.cfg, "brief", "b@z.com")
        p = ob.social_proof(self.cfg)
        self.assertIn("creators_joined", p)
        self.assertGreaterEqual(p["creators_joined"], 1)

    def test_referral_tracking(self):
        from src import onboarding as ob
        ob.track_referral(self.cfg, "@aarav")
        ob.track_referral(self.cfg, "@aarav")
        s = ob.referral_stats(self.cfg)
        self.assertEqual(s["total_referrals"], 2)
        self.assertEqual(s["top"][0]["creator"], "@aarav")
        self.assertEqual(s["top"][0]["signups"], 2)

    def test_cta_variant_assign(self):
        from src import onboarding as ob
        v1 = ob.assign_cta_variant(self.cfg, "visitorA")
        v2 = ob.assign_cta_variant(self.cfg, "visitorA")
        self.assertEqual(v1["variant"], v2["variant"])  # deterministic
        self.assertIn(v1["variant"], ["Start a Campaign", "Get a Free Quote"])

    def test_cta_winner_scoring(self):
        from src import onboarding as ob
        ob.record_cta_click(self.cfg, "Start a Campaign")
        ob.record_event(self.cfg, "creator_submit", "c@y.com", extra={"variant": "Start a Campaign"})
        w = ob.cta_winner(self.cfg)
        self.assertEqual(w["rows"][0]["variant"], "Start a Campaign")

    def test_whatsapp_handoff_deeplink(self):
        from src import onboarding as ob
        r = ob.whatsapp_handoff(self.cfg, brand="X", kind="brief")
        self.assertIn("wa.me", r["deep_link"])
        self.assertIsNone(r["auto_sent"])  # no token -> no auto send

    def test_digest_plain_text_render(self):
        from src import automation as auto
        from src.common import load_config
        cfg = load_config()
        subj, txt, html = auto._render_tpl("digest", {"date": "01 Jan 2026", "owner": "T",
                                                      "days": 7, "sent_total": "0", "delivery_rate": "0",
                                                      "bounces": "0", "unique_brands": "0", "closing": "0",
                                                      "interested": "0", "negotiating": "0", "declined": "0",
                                                      "matched_briefs": "0", "quotes_sent": "0", "creator_pool": "0",
                                                      "seo_pages": "0", "actions": "OK"},
                                            "CollabHive Weekly Report — {date}")
        self.assertTrue(txt)  # digest.txt exists; digest.html may not -> should not crash
        self.assertIn("CollabHive Weekly Report", subj)


def _blackbox_modes():
    """Run each run.py mode in a fresh subprocess with a temp data dir,
    no SMTP password, no network (must skip, never crash)."""
    os.environ.pop("OUTREACH_EMAIL_PASS", None)
    os.environ["OUTREACH_DISCOVERY"] = "0"
    os.environ.pop("OUTREACH_ROOT", None)  # so subprocess uses its own clone root
    failures = []
    # Build a temp clone of outreach/ so modules get a clean ROOT.
    clone = Path(tempfile.mkdtemp(prefix="ch_bb_"))
    src_root = Path(__file__).resolve().parent.parent
    shutil.copytree(src_root / "src", clone / "src")
    shutil.copytree(src_root / "templates", clone / "templates")
    (clone / "data").mkdir(exist_ok=True)
    # Use a minimal seed pool + empty briefs so no real network is attempted.
    (clone / "data" / "brands_seed.json").write_text(
        json.dumps([{"name": "TestBrand", "niche": "Tech & Startups", "city": "Delhi",
                     "website": "", "email": "", "emails": []}]), encoding="utf-8")
    (clone / "data" / "creators_pool.json").write_text(
        json.dumps([{"name": "C1", "handle": "@c1", "niche": "Tech & Startups",
                     "city": "Delhi", "followers": 5000, "rate": 2000}]), encoding="utf-8")
    (clone / "data" / "brand_briefs.json").write_text(
        json.dumps([{"brand": "B1", "niche": "Tech & Startups", "city": "Delhi",
                     "budget": "10000", "goal": "awareness"}]), encoding="utf-8")
    shutil.copy(src_root / "config.json", clone / "config.json")
    # Runner script to avoid shell-quoting issues in -c.
    runner = clone / "_runner.py"
    runner.write_text(
        "import sys, os\n"
        "os.environ['OUTREACH_DISCOVERY'] = '0'\n"
        "os.environ.pop('OUTREACH_EMAIL_PASS', None)\n"
        "from src import run\n"
        "sys.exit(run.main(sys.argv[1:]))\n", encoding="utf-8")
    for mode in ("daily", "enrich", "report", "sales", "seo", "verify",
                 "automation", "growth", "onboarding", "all"):
        import subprocess
        try:
            p = subprocess.run([sys.executable, str(runner), mode],
                               capture_output=True, text=True, timeout=90, cwd=str(clone))
            if p.returncode != 0:
                tail = (p.stdout or "").strip().splitlines()[-2:]
                tail += (p.stderr or "").strip().splitlines()[-3:]
                failures.append("%s rc=%s %s" % (mode, p.returncode, " | ".join(tail)))
        except subprocess.TimeoutExpired:
            failures.append("%s TIMEOUT" % mode)
        except Exception as exc:
            failures.append("%s EXC %s" % (mode, exc))
    shutil.rmtree(clone, ignore_errors=True)
    return failures


class TestBlackboxModes(unittest.TestCase):
    def test_all_modes_run_without_crash(self):
        fails = _blackbox_modes()
        self.assertEqual(fails, [], "modes crashed: %s" % fails)


def _suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (TestCommon, TestBrands, TestSales, TestMailerNoNetwork,
                TestGrowth, TestProtect, TestOnboarding, TestBlackboxModes):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(_suite())
    # Always clean up temp dir.
    shutil.rmtree(_TEST_ROOT, ignore_errors=True)
    sys.exit(0 if result.wasSuccessful() else 1)
