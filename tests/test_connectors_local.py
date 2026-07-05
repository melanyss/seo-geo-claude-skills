import os
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "connectors"))

import onpage  # noqa: E402
import linkgraph  # noqa: E402
import schema_lint  # noqa: E402
import robots  # noqa: E402
import psi  # noqa: E402
import ledger  # noqa: E402
import openpagerank  # noqa: E402
import resend  # noqa: E402
import firecrawl  # noqa: E402
import robots as robots_mod  # noqa: E402
import tavily  # noqa: E402
import doh  # noqa: E402
import pageviews  # noqa: E402
import gdelt  # noqa: E402
import youtube  # noqa: E402
import indexpush  # noqa: E402
import hn  # noqa: E402
import producthunt  # noqa: E402
import appstore  # noqa: E402
import bluesky  # noqa: E402
import fediverse  # noqa: E402
import discourse  # noqa: E402
import datetime as _dt  # noqa: E402


class OnPageParserTests(unittest.TestCase):
    def test_word_count_excludes_non_visible_head_and_script_text(self):
        html = """<!doctype html>
        <html>
          <head>
            <title>Invisible title</title>
            <style>.hidden words should not count</style>
            <script>var fake = "many invisible words here";</script>
          </head>
          <body>
            <h1>Hello world</h1>
            <p>Visible text only.</p>
          </body>
        </html>"""

        result = onpage.analyze(html)

        self.assertEqual(result["title"], "Invisible title")
        self.assertEqual(result["headings"]["h1"], ["Hello world"])
        self.assertEqual(result["word_count"], 5)


class LinkGraphTests(unittest.TestCase):
    def test_analyze_deduplicates_internal_links_and_reports_orphans(self):
        pages = [
            {
                "url": "https://example.com/",
                "depth": 0,
                "title": "Home",
                "links_out": [
                    "https://example.com/a",
                    "https://example.com/a",
                    "https://external.test/",
                ],
            },
            {
                "url": "https://example.com/a",
                "depth": 1,
                "title": "A",
                "links_out": [],
            },
            {
                "url": "https://example.com/orphan",
                "depth": 2,
                "title": "Orphan",
                "links_out": [],
            },
        ]

        result = linkgraph.analyze(pages)

        self.assertEqual(result["summary"]["total_internal_links"], 1)
        self.assertEqual(result["degrees"]["https://example.com/a"]["in"], 1)
        self.assertEqual(result["orphans"], ["https://example.com/orphan"])


class SchemaLintTests(unittest.TestCase):
    def test_lint_html_reports_required_schema_errors(self):
        html = """<script type="application/ld+json">
        {"@context":"https://schema.org","@type":"Article"}
        </script>"""

        result = schema_lint.lint_html(html, source="<test>")

        self.assertEqual(result["summary"]["errors"], 1)
        self.assertEqual(result["objects"][0]["@type"], "Article")
        self.assertEqual(result["objects"][0]["missing_required"], ["headline"])


class RobotsTxtTests(unittest.TestCase):
    def _parse(self, text):
        return robots.RobotsTxt.parse(text, "https://example.com/robots.txt", 200, None)

    def test_longest_match_wins_and_allow_beats_disallow(self):
        r = self._parse("User-agent: *\nDisallow: /admin\nAllow: /admin/public\n")
        # shorter Disallow /admin blocks a path with no longer match
        self.assertFalse(r.can_fetch("mybot", "/admin/secret")[0])
        # longer Allow /admin/public wins over the shorter Disallow
        self.assertTrue(r.can_fetch("mybot", "/admin/public/page")[0])
        # no rule matches -> default-allow
        self.assertTrue(r.can_fetch("mybot", "/blog/post")[0])

    def test_wildcard_and_end_anchor(self):
        r = self._parse("User-agent: *\nDisallow: /*.pdf$\n")
        self.assertFalse(r.can_fetch("mybot", "/files/report.pdf")[0])
        # the $ anchor means a query-suffixed path no longer matches -> allowed
        self.assertTrue(r.can_fetch("mybot", "/files/report.pdf?x=1")[0])


class PsiGradeTests(unittest.TestCase):
    def test_lcp_threshold_boundaries(self):
        self.assertEqual(psi.grade("LCP_ms", 2500.0), "good")            # <= good_max
        self.assertEqual(psi.grade("LCP_ms", 2500.1), "needs-improvement")
        self.assertEqual(psi.grade("LCP_ms", 4000.0), "needs-improvement")  # <= ni_max
        self.assertEqual(psi.grade("LCP_ms", 4000.1), "poor")

    def test_cls_none_and_unknown_metric(self):
        self.assertEqual(psi.grade("CLS", 0.1), "good")
        self.assertEqual(psi.grade("CLS", 0.26), "poor")
        self.assertIsNone(psi.grade("LCP_ms", None))
        self.assertIsNone(psi.grade("not_a_metric", 1.0))


class LedgerTests(unittest.TestCase):
    def test_slugify_normalizes_collapses_and_defaults(self):
        self.assertEqual(ledger.slugify("https://www.Example.com/path/"), "www.example.com-path")
        self.assertEqual(ledger.slugify("HTTP://a//b"), "a-b")
        self.assertEqual(ledger.slugify("   "), "unnamed")

    def test_flatten_dotted_keys_and_list_indices(self):
        flat = ledger.flatten({"a": {"b": 1}, "c": [10, 20]})
        self.assertEqual(flat["a.b"], 1)
        self.assertEqual(flat["c[0]"], 10)
        self.assertEqual(flat["c[1]"], 20)


class OpenPageRankTests(unittest.TestCase):
    def test_normalize_domain(self):
        self.assertEqual(openpagerank.normalize_domain("https://www.Example.com/path"), "www.example.com")
        self.assertEqual(openpagerank.normalize_domain("Example.com/foo"), "example.com")
        self.assertEqual(openpagerank.normalize_domain(""), "")

    def test_parse_response_maps_onto_requested_order(self):
        payload = {"status_code": 200, "response": [
            {"domain": "b.com", "page_rank_decimal": 5.1, "page_rank_integer": 5,
             "rank": "100", "status_code": 200},
        ]}
        rows = openpagerank.parse_response(payload, ["a.com", "b.com"])
        self.assertEqual([r["domain"] for r in rows], ["a.com", "b.com"])
        self.assertFalse(rows[0]["found"])   # a.com absent from response
        self.assertTrue(rows[1]["found"])    # b.com present with status 200
        self.assertEqual(rows[1]["page_rank_decimal"], 5.1)


class ResendSpecTests(unittest.TestCase):
    def _spec(self, argv):
        return resend.build_spec(resend.build_parser().parse_args(argv))

    def test_read_commands_are_not_mutating(self):
        for argv in (["domains"], ["contacts"], ["segments"], ["broadcasts"],
                     ["emails", "--limit", "5"]):
            spec = self._spec(argv)
            self.assertFalse(spec["mutating"], argv)
            self.assertEqual(spec["request"]["method"], "GET")

    def test_every_send_path_is_flagged_mutating(self):
        send = ["send", "--from", "me@x.dev", "--to", "a@y.com",
                "--subject", "s", "--text", "body text"]
        for argv in (send, ["verify-domain", "d1"], ["suppress", "a@y.com"],
                     ["cancel-email", "e1"], ["broadcast-send", "b1"]):
            self.assertTrue(self._spec(argv)["mutating"], argv)

    def test_seed_expands_one_message_per_recipient(self):
        spec = self._spec(["seed", "--from", "me@x.dev",
                           "--to", "s1@gmail.com, s2@outlook.com",
                           "--subject", "seed", "--text", "plain body"])
        body = spec["request"]["body"]
        self.assertEqual(spec["request"]["url"], resend.API_BASE + "/emails/batch")
        self.assertEqual([m["to"] for m in body], [["s1@gmail.com"], ["s2@outlook.com"]])

    def test_send_requires_content_and_recipients(self):
        base = ["send", "--from", "me@x.dev", "--subject", "s"]
        self.assertEqual(self._spec(base + ["--to", "a@y.com"])["error"],
                         "missing_content")
        self.assertEqual(self._spec(base + ["--to", " ", "--text", "t"])["error"],
                         "no_recipients")

    def test_suppress_quotes_email_in_path_and_sets_unsubscribed(self):
        spec = self._spec(["suppress", "jane@example.com"])
        self.assertEqual(spec["request"]["url"],
                         resend.API_BASE + "/contacts/jane%40example.com")
        self.assertEqual(spec["request"]["method"], "PATCH")
        self.assertEqual(spec["request"]["body"], {"unsubscribed": True})

    def test_sends_carry_idempotency_key_but_non_supporting_calls_do_not(self):
        send = ["send", "--from", "me@x.dev", "--to", "a@y.com",
                "--subject", "s", "--text", "t"]
        seed = ["seed", "--from", "me@x.dev", "--to", "a@y.com",
                "--subject", "s", "--text", "t"]
        for argv in (send, seed):
            hdrs = self._spec(argv)["request"]["headers"]
            self.assertTrue(hdrs["Idempotency-Key"].startswith("resend-py/"), argv)
        # No Idempotency-Key on endpoints Resend does not support it for.
        for argv in (["suppress", "a@y.com"], ["broadcast-send", "b1"],
                     ["verify-domain", "d1"]):
            self.assertEqual(self._spec(argv)["request"]["headers"], {}, argv)

    def test_explicit_idempotency_key_is_used_and_capped(self):
        spec = self._spec(["send", "--from", "me@x.dev", "--to", "a@y.com",
                           "--subject", "s", "--text", "t",
                           "--idempotency-key", "welcome/123"])
        self.assertEqual(spec["request"]["headers"]["Idempotency-Key"], "welcome/123")
        self.assertEqual(len(resend.idempotency_key("x" * 400)),
                         resend.IDEMPOTENCY_MAX)


class FirecrawlSpecTests(unittest.TestCase):
    def _spec(self, argv):
        return firecrawl.build_spec(firecrawl.build_parser().parse_args(argv))

    def test_scrape_body_and_preflight_target(self):
        spec = self._spec(["scrape", "https://x.dev/p", "--formats",
                           "markdown, links", "--wait", "1500", "--full-page"])
        self.assertEqual(spec["target"], "https://x.dev/p")
        self.assertEqual(spec["request"]["body"], {
            "url": "https://x.dev/p", "formats": ["markdown", "links"],
            "onlyMainContent": False, "waitFor": 1500})

    def test_search_has_no_preflight_target_and_splits_domains(self):
        spec = self._spec(["search", "best crm", "--limit", "5", "--scrape",
                           "--include-domains", "a.com, b.com"])
        self.assertIsNone(spec["target"])
        body = spec["request"]["body"]
        self.assertEqual(body["includeDomains"], ["a.com", "b.com"])
        self.assertEqual(body["scrapeOptions"], {"formats": ["markdown"]})

    def test_crawl_job_endpoints(self):
        start = self._spec(["crawl", "https://x.dev", "--limit", "50"])
        self.assertEqual(start["request"]["body"]["limit"], 50)
        self.assertEqual(start["target"], "https://x.dev")
        status = self._spec(["crawl-status", "job/1"])
        self.assertEqual(status["request"]["method"], "GET")
        self.assertEqual(status["request"]["url"],
                         firecrawl.API_BASE + "/crawl/job%2F1")
        self.assertIsNone(status["target"])

    def test_preflight_refuses_on_disallow_and_allows_otherwise(self):
        parsed = robots_mod.RobotsTxt.parse(
            "User-agent: *\nDisallow: /private\n",
            "https://x.dev/robots.txt", 200, None)
        original = firecrawl.robots.fetch
        firecrawl.robots.fetch = lambda url: parsed
        try:
            self.assertFalse(firecrawl.preflight("https://x.dev/private/a")["allowed"])
            self.assertTrue(firecrawl.preflight("https://x.dev/public")["allowed"])
        finally:
            firecrawl.robots.fetch = original


class TavilySpecTests(unittest.TestCase):
    def _spec(self, argv):
        return tavily.build_spec(tavily.build_parser().parse_args(argv))

    def test_search_body_and_no_preflight_targets(self):
        spec = self._spec(["search", "topic q", "--limit", "10", "--answer",
                           "--topic", "news", "--time-range", "w",
                           "--include-domains", "a.com, b.com"])
        self.assertEqual(spec["targets"], [])
        body = spec["request"]["body"]
        self.assertEqual(body["max_results"], 10)
        self.assertEqual(body["include_answer"], True)
        self.assertEqual(body["topic"], "news")
        self.assertEqual(body["include_domains"], ["a.com", "b.com"])

    def test_answer_level_passthrough(self):
        body = self._spec(["search", "q", "--answer", "advanced"])["request"]["body"]
        self.assertEqual(body["include_answer"], "advanced")

    def test_extract_targets_and_url_shape(self):
        one = self._spec(["extract", "https://x.dev/a"])
        self.assertEqual(one["request"]["body"]["urls"], "https://x.dev/a")
        self.assertEqual(one["targets"], ["https://x.dev/a"])
        many = self._spec(["extract", "https://x.dev/a", "https://y.dev/b"])
        self.assertEqual(many["request"]["body"]["urls"],
                         ["https://x.dev/a", "https://y.dev/b"])
        self.assertEqual(len(many["targets"]), 2)

    def test_extract_preflight_blocks_on_disallow(self):
        parsed = robots_mod.RobotsTxt.parse(
            "User-agent: *\nDisallow: /private\n",
            "https://x.dev/robots.txt", 200, None)
        original = tavily.robots.fetch
        tavily.robots.fetch = lambda url: parsed
        try:
            self.assertFalse(tavily.preflight("https://x.dev/private/a")["allowed"])
            self.assertTrue(tavily.preflight("https://x.dev/ok")["allowed"])
        finally:
            tavily.robots.fetch = original


class DohTests(unittest.TestCase):
    def test_strip_txt_joins_chunked_quoted_payloads(self):
        self.assertEqual(doh._strip_txt('"v=DMARC1; p=no" "ne; rua=x"'),
                         "v=DMARC1; p=none; rua=x")
        self.assertEqual(doh._strip_txt("plain"), "plain")

    def test_parse_tags(self):
        tags = doh.parse_tags("v=DMARC1; p=none; rua=mailto:a@b; aspf=s")
        self.assertEqual(tags["p"], "none")
        self.assertEqual(tags["aspf"], "s")

    def test_spf_facts_flags(self):
        ok = doh.spf_facts(["v=spf1 include:_spf.x.com ~all"])
        self.assertTrue(ok["present"])
        self.assertEqual(ok["flags"], [])
        redirect = doh.spf_facts(["v=spf1 redirect=_spf.google.com"])
        self.assertEqual(redirect["flags"], [])
        open_ended = doh.spf_facts(["v=spf1 include:_spf.x.com"])
        self.assertIn("no_all_or_redirect", open_ended["flags"])
        double = doh.spf_facts(["v=spf1 ~all", "v=spf1 -all"])
        self.assertIn("multiple_spf_records", double["flags"])
        absent = doh.spf_facts(["some-verification=abc"])
        self.assertFalse(absent["present"])

    def test_build_url_per_resolver(self):
        self.assertIn("dns.google/resolve?", doh.build_url("_dmarc.x.com"))
        self.assertIn("cloudflare-dns.com", doh.build_url("x.com", "MX", "cloudflare"))


class PageviewsTests(unittest.TestCase):
    def test_build_url_encodes_title(self):
        url = pageviews.build_url("Claude (language model)/x")
        self.assertIn("Claude_%28language_model%29%2Fx", url)
        self.assertIn("/monthly/", url)

    def test_default_range_monthly_uses_full_months(self):
        start, end = pageviews.default_range(
            "monthly", months=3, today=_dt.date(2026, 7, 4))
        self.assertEqual(start, "2026040100")
        self.assertEqual(end, "2026063000")

    def test_default_range_daily_excludes_today(self):
        start, end = pageviews.default_range(
            "daily", days=7, today=_dt.date(2026, 7, 4))
        self.assertEqual(start, "2026062700")
        self.assertEqual(end, "2026070300")


class GdeltTests(unittest.TestCase):
    def test_build_url_params(self):
        url = gdelt.build_url('"acme corp"', "artlist", days=7, maxrecords=999)
        self.assertIn("timespan=7d", url)
        self.assertIn("maxrecords=%d" % gdelt.MAX_RECORDS, url)  # capped
        self.assertNotIn("maxrecords", gdelt.build_url("q", "timelinevol"))

    def test_parse_response_shapes(self):
        arts = gdelt.parse_response(
            {"articles": [{"title": "t", "url": "u", "domain": "d"}]}, "artlist")
        self.assertEqual(arts["count"], 1)
        self.assertEqual(arts["articles"][0]["domain"], "d")
        tl = gdelt.parse_response(
            {"timeline": [{"data": [{"date": "20260701", "value": 2}]}]},
            "timelinevol")
        self.assertEqual(tl["timeline"], [{"date": "20260701", "value": 2}])


class YoutubeSpecTests(unittest.TestCase):
    def test_parse_channel_ref_forms(self):
        self.assertEqual(youtube.parse_channel_ref("@mkbhd"), ("handle", "@mkbhd"))
        self.assertEqual(youtube.parse_channel_ref("mkbhd"), ("handle", "@mkbhd"))
        self.assertEqual(youtube.parse_channel_ref("UCBJycsmduvYEL83R_U4JriQ"),
                         ("id", "UCBJycsmduvYEL83R_U4JriQ"))
        self.assertEqual(
            youtube.parse_channel_ref(
                "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ"),
            ("id", "UCBJycsmduvYEL83R_U4JriQ"))
        self.assertEqual(youtube.parse_channel_ref("https://youtube.com/@mkbhd"),
                         ("handle", "@mkbhd"))

    def test_uploads_playlist_swap(self):
        self.assertEqual(youtube.uploads_playlist("UCabc123def456"), "UUabc123def456")
        self.assertIsNone(youtube.uploads_playlist("HCxyz"))


class IndexpushSpecTests(unittest.TestCase):
    def test_indexnow_requires_single_host_and_key(self):
        mixed = indexpush.build_spec("indexnow",
                                     ["https://a.com/1", "https://b.com/2"], key="k")
        self.assertEqual(mixed["error"], "mixed_or_missing_hosts")
        nokey = indexpush.build_spec("indexnow", ["https://a.com/1"])
        self.assertEqual(nokey["error"], "missing_key")

    def test_indexnow_body_shape(self):
        spec = indexpush.build_spec(
            "indexnow", ["https://a.com/1", "https://a.com/2"],
            key="abc123", key_location="https://a.com/abc123.txt")
        body = spec["request"]["body"]
        self.assertEqual(body["host"], "a.com")
        self.assertEqual(body["urlList"], ["https://a.com/1", "https://a.com/2"])
        self.assertEqual(body["keyLocation"], "https://a.com/abc123.txt")
        over = indexpush.build_spec(
            "indexnow", ["https://a.com/%d" % i for i in range(10_001)], key="k")
        self.assertEqual(over["error"], "too_many_urls")

    def test_baidu_spec(self):
        self.assertEqual(indexpush.build_spec("baidu", ["https://a.com/1"],
                                              key="t")["error"], "missing_site")
        spec = indexpush.build_spec("baidu", ["https://a.com/1"],
                                    key="tok", site="www.a.com")
        self.assertIn("site=www.a.com", spec["request"]["url"])
        self.assertIn("token=tok", spec["request"]["url"])
        self.assertEqual(spec["request"]["content_type"], "text/plain")
        self.assertEqual(spec["request"]["body"], ["https://a.com/1"])

    def test_collect_urls_dedupes_preserving_order(self):
        self.assertEqual(indexpush.collect_urls(["a", "b", "a", "c"], None),
                         ["a", "b", "c"])


class HnTests(unittest.TestCase):
    def test_numeric_filters_force_search_by_date_index(self):
        url, endpoint = hn.build_search_url("acme", tags="story")
        self.assertEqual(endpoint, "search")
        self.assertIn("/search?", url)
        self.assertIn("tags=story", url)
        filters = hn.build_numeric_filters(since_epoch=1750000000, min_points=50)
        self.assertEqual(filters, ["created_at_i>=1750000000", "points>=50"])
        url, endpoint = hn.build_search_url("acme", tags="(story,show_hn)",
                                            numeric_filters=filters)
        self.assertEqual(endpoint, "search_by_date")
        self.assertIn("/search_by_date?", url)
        self.assertIn("numericFilters=created_at_i%3E%3D1750000000%2Cpoints%3E%3D50", url)
        self.assertIn("tags=%28story%2Cshow_hn%29", url)
        # hitsPerPage clamped to [1, MAX_HITS]
        self.assertIn("hitsPerPage=100", hn.build_search_url("q", hits_per_page=500)[0])
        self.assertIn("hitsPerPage=1", hn.build_search_url("q", hits_per_page=0)[0])

    def test_rank_composes_list_position_and_comments_gt_points_fact(self):
        responses = {
            hn.build_firebase_url("showstories"): {"json": [111, 222, 333]},
            hn.build_firebase_url("item/222"): {"json": {
                "id": 222, "type": "story", "title": "Show HN: X",
                "score": 10, "descendants": 25, "by": "alice", "time": 0}},
        }
        original = hn._polite_get_json
        hn._polite_get_json = lambda url: responses[url]
        try:
            out = hn.rank(222, "showstories")
        finally:
            hn._polite_get_json = original
        self.assertEqual(out["rank"], 2)          # 1-based position
        self.assertEqual(out["list_size"], 3)
        self.assertEqual(out["points"], 10)
        self.assertEqual(out["descendants"], 25)
        self.assertTrue(out["comments_gt_points"])
        self.assertIsNone(hn.find_rank([111, 222, 333], 999))


class ProducthuntTests(unittest.TestCase):
    def test_day_window_defaults_to_last_completed_utc_day(self):
        today = _dt.date(2026, 7, 5)
        self.assertEqual(producthunt.day_window(today=today),
                         ("2026-07-04", "2026-07-04T00:00:00Z",
                          "2026-07-05T00:00:00Z"))
        self.assertEqual(producthunt.day_window("2026-06-30", today=today),
                         ("2026-06-30", "2026-06-30T00:00:00Z",
                          "2026-07-01T00:00:00Z"))
        with self.assertRaises(ValueError):
            producthunt.day_window("2026-07-05", today=today)  # in-progress day
        with self.assertRaises(ValueError):
            producthunt.day_window("2026-07-09", today=today)  # future day

    def test_build_query_caps_first_and_shapes_variables(self):
        q = producthunt.build_query("daily", posted_after="A",
                                    posted_before="B", first=500)
        self.assertEqual(q["variables"],
                         {"first": producthunt.MAX_POSTS, "after": "A",
                          "before": "B"})
        self.assertIn("order: VOTES", q["query"])
        post = producthunt.build_query("post", slug="my-app")
        self.assertEqual(post["variables"], {"slug": "my-app"})
        self.assertIn("createdAt", post["query"])
        topic = producthunt.build_query("topic", topic="ai", first=0)
        self.assertEqual(topic["variables"], {"topic": "ai", "first": 1})
        with self.assertRaises(ValueError):
            producthunt.build_query("nope")

    def test_classify_failure_rate_limit_auth_and_missing_token(self):
        code, err = producthunt.classify_failure(
            {"status": 429, "headers": {"X-Rate-Limit-Reset": "600"},
             "json": None})
        self.assertEqual((code, err["error"], err["reset_seconds"]),
                         (3, "rate_limited", "600"))
        code, err = producthunt.classify_failure(
            {"status": 401, "headers": {}, "json": None})
        self.assertEqual((code, err["error"]), (3, "auth_failed"))
        self.assertIsNone(producthunt.classify_failure(
            {"status": 200, "headers": {},
             "json": {"data": {"posts": {"edges": []}}}}))
        # no --token, no env token, no client_credentials pair -> classified
        saved = {k: os.environ.pop(k, None) for k in
                 (producthunt.ENV_TOKEN, producthunt.ENV_CLIENT_ID,
                  producthunt.ENV_CLIENT_SECRET)}
        try:
            self.assertEqual(producthunt.resolve_token(),
                             ("", "no token configured"))
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v


class AppstoreTests(unittest.TestCase):
    def test_lookup_batches_ids_and_flags_bad_ones(self):
        ids, bad = appstore.parse_ids(["310633997,284882215", "12345", "abc"])
        self.assertEqual(ids, ["310633997", "284882215", "12345", "abc"])
        self.assertEqual(bad, ["abc"])
        url = appstore.build_lookup_url(["310633997", "284882215"], "gb")
        self.assertIn("/lookup?", url)
        self.assertIn("id=310633997%2C284882215", url)  # comma-batched ids
        self.assertIn("country=gb", url)

    def test_charts_url_uses_new_marketingtools_host_and_documented_sizes(self):
        self.assertEqual(appstore.chart_size_for(10), 10)
        self.assertEqual(appstore.chart_size_for(11), 25)
        self.assertEqual(appstore.chart_size_for(999), 50)
        self.assertEqual(
            appstore.build_charts_url("us", "top-paid", appstore.chart_size_for(11)),
            "https://rss.marketingtools.apple.com/api/v2/us/apps/top-paid/25/apps.json")

    def test_search_url_locks_media_to_software_and_caps_limit(self):
        url = appstore.build_search_url("meditation app", "us", 500)
        self.assertIn("term=meditation+app", url)
        self.assertIn("country=us", url)
        self.assertIn("media=software", url)
        self.assertIn("limit=200", url)   # SEARCH_MAX cap
        self.assertIn("limit=1", appstore.build_search_url("x", "us", 0))


class BlueskyTests(unittest.TestCase):
    def test_build_xrpc_url_encodes_params_and_picks_base(self):
        url = bluesky.build_xrpc_url("app.bsky.actor.getProfile",
                                     {"actor": "bsky.app"})
        self.assertTrue(url.startswith(bluesky.PUBLIC_BASE + "/"))
        self.assertIn("app.bsky.actor.getProfile?", url)
        self.assertIn("actor=bsky.app", url)
        # search hits the authed base, not the public AppView
        authed = bluesky.build_xrpc_url("app.bsky.feed.searchPosts",
                                        {"q": "acme"}, base=bluesky.AUTH_BASE)
        self.assertTrue(authed.startswith(bluesky.AUTH_BASE + "/"))

    def test_clamp_limit_window_and_default(self):
        self.assertEqual(bluesky.clamp_limit(None), 25)
        self.assertEqual(bluesky.clamp_limit(0), 1)
        self.assertEqual(bluesky.clamp_limit(500), bluesky.MAX_LIMIT)

    def test_parse_since_and_bad_date(self):
        self.assertEqual(bluesky.parse_since("2026-06-01"),
                         "2026-06-01T00:00:00Z")
        with self.assertRaises(ValueError):
            bluesky.parse_since("2026/06/01")

    def test_resolve_credentials_over_supplied_mapping(self):
        ident, pw, err = bluesky.resolve_credentials(
            {"BSKY_IDENTIFIER": "me.bsky.social", "BSKY_APP_PASSWORD": "x-x"})
        self.assertEqual((ident, pw, err), ("me.bsky.social", "x-x", None))
        _, _, err = bluesky.resolve_credentials({"BSKY_IDENTIFIER": "me"})
        self.assertIn("BSKY_APP_PASSWORD", err)

    def test_parse_feed_marks_reposts(self):
        payload = {"feed": [
            {"post": {"uri": "at://1", "record": {"createdAt": "t1",
                      "text": "hi"}, "author": {"handle": "a"},
                      "likeCount": 3}},
            {"post": {"uri": "at://2", "record": {"createdAt": "t0"}},
             "reason": {"$type": "app.bsky.feed.defs#reasonRepost"}},
        ]}
        rows = bluesky.parse_feed(payload)
        self.assertEqual(rows[0]["likes"], 3)
        self.assertFalse(rows[0]["is_repost"])
        self.assertTrue(rows[1]["is_repost"])


class FediverseTests(unittest.TestCase):
    def test_normalize_instance_strips_scheme_and_path(self):
        self.assertEqual(fediverse.normalize_instance("https://mastodon.social/"),
                         "mastodon.social")
        self.assertEqual(fediverse.normalize_instance("HACHYDERM.IO/foo"),
                         "HACHYDERM.IO")

    def test_build_urls_cap_limits_and_encode(self):
        self.assertEqual(
            fediverse.build_trends_tags_url("mastodon.social", 999),
            "https://mastodon.social/api/v1/trends/tags?limit=%d"
            % fediverse.MAX_TRENDS)
        tag = fediverse.build_tag_url("mastodon.social", "#opensource", 5)
        self.assertIn("/api/v1/timelines/tag/opensource?", tag)
        self.assertIn("limit=5", tag)
        rss = fediverse.tag_rss_url("mastodon.social", "#opensource")
        self.assertEqual(rss, "https://mastodon.social/tags/opensource.rss")

    def test_build_lemmy_search_url_shape(self):
        url = fediverse.build_lemmy_search_url("lemmy.world", "self host",
                                               "TopMonth", 99)
        self.assertIn("type_=All", url)
        self.assertIn("sort=TopMonth", url)
        self.assertIn("limit=%d" % fediverse.LEMMY_MAX, url)  # capped

    def test_parse_trend_tag_totals_7day_uses(self):
        parsed = fediverse.parse_trend_tag({
            "name": "opensource", "url": "https://x/tags/opensource",
            "history": [{"day": "1751328000", "uses": "5", "accounts": "3"},
                        {"day": "1751241600", "uses": "2", "accounts": "1"}]})
        self.assertEqual(parsed["name"], "opensource")
        self.assertEqual(parsed["uses_7d"], 7)
        self.assertEqual(parsed["accounts_today"], 3)   # newest day first

    def test_strip_html_unwraps_paragraphs_and_entities(self):
        self.assertEqual(fediverse.strip_html("<p>a&amp;b<br>c</p>"), "a&b\nc")


class DiscourseTests(unittest.TestCase):
    def test_normalize_base_to_origin_no_trailing_slash(self):
        self.assertEqual(discourse.normalize_base("meta.discourse.org"),
                         "https://meta.discourse.org")
        self.assertEqual(
            discourse.normalize_base("https://meta.discourse.org/latest/"),
            "https://meta.discourse.org")

    def test_build_endpoint_urls(self):
        base = "https://meta.discourse.org"
        self.assertEqual(discourse.build_latest_url(base),
                         base + "/latest.json")
        self.assertEqual(discourse.build_topic_url(base, 42),
                         base + "/t/42.json")
        d = discourse.build_directory_url(base, period="monthly", limit=999)
        self.assertIn("/directory_items.json?", d)
        self.assertIn("period=monthly", d)
        self.assertIn("limit=%d" % discourse.DIRECTORY_MAX_API, d)  # capped

    def test_time_to_first_response_skips_op_self_replies(self):
        posts = [
            {"post_number": 1, "username": "op", "created_at": "2026-07-01T00:00:00Z"},
            {"post_number": 2, "username": "op", "created_at": "2026-07-01T00:05:00Z"},
            {"post_number": 3, "username": "other", "created_at": "2026-07-01T00:10:00Z"},
        ]
        self.assertEqual(discourse.time_to_first_response(posts), 600)
        # no reply by another user -> None (unanswered)
        self.assertIsNone(discourse.time_to_first_response(
            [{"post_number": 1, "username": "op",
              "created_at": "2026-07-01T00:00:00Z"}]))

    def test_parse_directory_tallies_trust_levels(self):
        payload = {"directory_items": [
            {"user": {"username": "a", "trust_level": 2}},
            {"user": {"username": "b", "trust_level": 2}},
            {"user": {"username": "c", "trust_level": 0}},
        ]}
        out = discourse.parse_directory(payload)
        self.assertEqual(out["rows_counted"], 3)
        self.assertEqual(out["trust_level_distribution"]["2_member"], 2)
        self.assertEqual(out["trust_level_distribution"]["0_new"], 1)


if __name__ == "__main__":
    unittest.main()
