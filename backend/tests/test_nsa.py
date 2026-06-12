"""
═══════════════════════════════════════════════════════════════
  N.S.A // NEURAL SOC ANALYST — TEST SUITE
  Run from project root:  python -m pytest backend/test_nsa.py -v
  Or directly:            python backend/test_nsa.py
═══════════════════════════════════════════════════════════════
"""

import sys
import os
import json
import unittest

# Make sure backend modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# ── We mock the API calls so tests never hit real endpoints ──
from unittest.mock import patch, MagicMock


# ════════════════════════════════════════════════════════════
#  1. CONFIG TESTS
# ════════════════════════════════════════════════════════════
class TestConfig(unittest.TestCase):

    def test_api_url_format(self):
        """Groq API URL should be a valid HTTPS endpoint."""
        from config import API_URL
        self.assertTrue(API_URL.startswith("https://"),
            "API_URL must start with https://")

    def test_model_not_empty(self):
        """Model name should not be empty."""
        from config import MODEL
        self.assertIsInstance(MODEL, str)
        self.assertGreater(len(MODEL), 0)

    def test_history_file_path_is_string(self):
        """HISTORY_FILE should be a valid path string."""
        from config import HISTORY_FILE
        self.assertIsInstance(HISTORY_FILE, str)
        self.assertTrue(HISTORY_FILE.endswith(".json"))

    def test_max_history_is_positive(self):
        """MAX_HISTORY should be a positive integer."""
        from config import MAX_HISTORY
        self.assertIsInstance(MAX_HISTORY, int)
        self.assertGreater(MAX_HISTORY, 0)

    def test_vt_base_url(self):
        """VirusTotal base URL should point to v3 API."""
        from config import VT_BASE_URL
        self.assertIn("virustotal.com", VT_BASE_URL)
        self.assertIn("v3", VT_BASE_URL)


# ════════════════════════════════════════════════════════════
#  2. HISTORY TESTS
# ════════════════════════════════════════════════════════════
class TestHistory(unittest.TestCase):

    def setUp(self):
        """Use a temp history file so we don't touch the real one."""
        import tempfile
        self.tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        )
        self.tmp.write("[]")
        self.tmp.close()

        # Patch history.HISTORY_FILE directly — config patch arrives too late
        # because history.py already copied the value at import time
        import history
        import config
        self._orig_hist   = history.HISTORY_FILE
        self._orig_config = config.HISTORY_FILE
        history.HISTORY_FILE = self.tmp.name
        config.HISTORY_FILE  = self.tmp.name

    def tearDown(self):
        import history, config
        history.HISTORY_FILE = self._orig_hist
        config.HISTORY_FILE  = self._orig_config
        os.unlink(self.tmp.name)

    def test_get_history_empty_on_start(self):
        """Fresh history file should return empty list."""
        from history import get_history
        self.assertEqual(get_history(), [])

    def test_save_and_retrieve_incident(self):
        """Saving an incident should make it retrievable."""
        from history import save_incident, get_history
        incident = {
            "input": "test payload",
            "result": '{"risk_level":"Low","risk_score":10,"explanation":"safe","recommendation":"none"}'
        }
        save_incident(incident)
        history = get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["input"], "test payload")

    def test_newest_incident_is_first(self):
        """Most recent incident should be at index 0."""
        from history import save_incident, get_history
        save_incident({"input": "first",  "result": "{}"})
        save_incident({"input": "second", "result": "{}"})
        save_incident({"input": "third",  "result": "{}"})
        history = get_history()
        self.assertEqual(history[0]["input"], "third")

    def test_history_respects_max_limit(self):
        """History should never exceed MAX_HISTORY entries."""
        from history import save_incident, get_history
        from config import MAX_HISTORY
        for i in range(MAX_HISTORY + 10):
            save_incident({"input": f"incident_{i}", "result": "{}"})
        self.assertLessEqual(len(get_history()), MAX_HISTORY)

    def test_history_persists_to_disk(self):
        """History should survive a re-import (simulating restart)."""
        from history import save_incident
        save_incident({"input": "persistent", "result": "{}"})

        # Re-read raw file
        with open(self.tmp.name, "r") as f:
            data = json.load(f)
        self.assertEqual(data[0]["input"], "persistent")


# ════════════════════════════════════════════════════════════
#  3. ANALYZER TESTS (mocked — never hits Groq API)
# ════════════════════════════════════════════════════════════
MOCK_GROQ_RESPONSE = {
    "choices": [{
        "message": {
            "content": json.dumps({
                "risk_level":     "High",
                "risk_score":     87,
                "explanation":    "Payload contains obfuscated PowerShell with base64 encoded command.",
                "recommendation": "Isolate host immediately and run full EDR scan."
            })
        }
    }]
}


class TestAnalyzer(unittest.TestCase):

    @patch("analyzer.requests.post")
    def test_analyze_returns_json_string(self, mock_post):
        """Analyzer should return a JSON string from the LLM."""
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        from analyzer import analyze_text
        result = analyze_text("powershell -enc SQBFAFgA")
        parsed = json.loads(result)
        self.assertIn("risk_level",     parsed)
        self.assertIn("risk_score",     parsed)
        self.assertIn("explanation",    parsed)
        self.assertIn("recommendation", parsed)

    @patch("analyzer.requests.post")
    def test_risk_score_in_range(self, mock_post):
        """Risk score should be between 0 and 100."""
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        from analyzer import analyze_text
        result = json.loads(analyze_text("test input"))
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 100)

    @patch("analyzer.requests.post")
    def test_risk_level_valid_values(self, mock_post):
        """Risk level should be Low, Medium, or High."""
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        from analyzer import analyze_text
        result = json.loads(analyze_text("test input"))
        self.assertIn(result["risk_level"], ["Low", "Medium", "High"])

    @patch("analyzer.requests.post", side_effect=Exception("Network error"))
    def test_analyzer_handles_network_error(self, mock_post):
        """Analyzer should return an ERROR string if request fails."""
        from analyzer import analyze_text
        result = analyze_text("test")
        self.assertTrue(result.startswith("ERROR:"))

    @patch("analyzer.requests.post")
    def test_empty_input_still_calls_api(self, mock_post):
        """Analyzer calls API even with minimal input (Flask guards empty)."""
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        from analyzer import analyze_text
        result = analyze_text(" ")
        self.assertIsInstance(result, str)


# ════════════════════════════════════════════════════════════
#  4. VIRUSTOTAL MODULE TESTS (mocked)
# ════════════════════════════════════════════════════════════
class TestVTDetection(unittest.TestCase):
    """Test the auto-type detection logic in vt.py."""

    def test_detects_ipv4(self):
        from vt import _detect_type
        self.assertEqual(_detect_type("8.8.8.8"),          "ip")
        self.assertEqual(_detect_type("192.168.1.100"),     "ip")
        self.assertEqual(_detect_type("255.255.255.255"),   "ip")

    def test_detects_md5(self):
        from vt import _detect_type
        self.assertEqual(_detect_type("d41d8cd98f00b204e9800998ecf8427e"), "hash")

    def test_detects_sha1(self):
        from vt import _detect_type
        self.assertEqual(_detect_type("da39a3ee5e6b4b0d3255bfef95601890afd80709"), "hash")

    def test_detects_sha256(self):
        from vt import _detect_type
        h = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(_detect_type(h), "hash")

    def test_detects_url(self):
        from vt import _detect_type
        self.assertEqual(_detect_type("http://evil.com/payload"),  "url")
        self.assertEqual(_detect_type("https://phishing.io/login"), "url")

    def test_detects_domain(self):
        from vt import _detect_type
        self.assertEqual(_detect_type("malware-host.ru"), "domain")
        self.assertEqual(_detect_type("google.com"),      "domain")

    def test_strips_whitespace(self):
        from vt import _detect_type
        self.assertEqual(_detect_type("  8.8.8.8  "), "ip")


class TestVTLookup(unittest.TestCase):

    @patch("vt.VT_API_KEY", "fake_key_for_testing")
    @patch("vt.requests.get")
    def test_ip_lookup_clean(self, mock_get):
        """Clean IP should return verdict: clean."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {"attributes": {
                "last_analysis_stats": {
                    "malicious": 0, "suspicious": 0,
                    "harmless": 70, "undetected": 10
                },
                "country":  "US",
                "as_owner": "Google LLC"
            }}
        }
        from vt import lookup_ip
        result = lookup_ip("8.8.8.8")
        self.assertEqual(result["verdict"], "clean")
        self.assertEqual(result["country"], "US")

    @patch("vt.VT_API_KEY", "fake_key_for_testing")
    @patch("vt.requests.get")
    def test_ip_lookup_malicious(self, mock_get):
        """IP flagged by engines should return verdict: malicious."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {"attributes": {
                "last_analysis_stats": {
                    "malicious": 15, "suspicious": 3,
                    "harmless": 2, "undetected": 5
                },
                "country":  "RU",
                "as_owner": "Unknown AS"
            }}
        }
        from vt import lookup_ip
        result = lookup_ip("1.2.3.4")
        self.assertEqual(result["verdict"], "malicious")
        self.assertEqual(result["stats"]["malicious"], 15)

    @patch("vt.VT_API_KEY", "fake_key_for_testing")
    @patch("vt.requests.get")
    def test_hash_not_found(self, mock_get):
        """Unknown hash should return verdict: not_found."""
        mock_get.return_value.status_code = 404
        from vt import lookup_hash
        result = lookup_hash("d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(result["verdict"], "not_found")

    @patch("vt.VT_API_KEY", "")
    def test_vt_lookup_no_key(self):
        """Missing API key should return a clear error."""
        from vt import vt_lookup
        result = vt_lookup("8.8.8.8")
        self.assertIn("error", result)
        self.assertIn("VT_API_KEY", result["error"])

    @patch("vt.VT_API_KEY", "fake_key_for_testing")
    @patch("vt.requests.get", side_effect=Exception("Timeout"))
    def test_vt_lookup_handles_exception(self, mock_get):
        """Network errors should be caught and returned as error dict."""
        from vt import vt_lookup
        result = vt_lookup("8.8.8.8")
        self.assertIn("error", result)


# ════════════════════════════════════════════════════════════
#  5. FLASK ENDPOINT TESTS
# ════════════════════════════════════════════════════════════
class TestFlaskEndpoints(unittest.TestCase):

    def setUp(self):
        import tempfile, config, history
        self.tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        )
        self.tmp.write("[]")
        self.tmp.close()
        self._orig_hist   = history.HISTORY_FILE
        self._orig_config = config.HISTORY_FILE
        history.HISTORY_FILE = self.tmp.name
        config.HISTORY_FILE  = self.tmp.name

        from app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        import history, config
        history.HISTORY_FILE = self._orig_hist
        config.HISTORY_FILE  = self._orig_config
        os.unlink(self.tmp.name)

    # ── /history ──────────────────────────────────────────
    def test_history_returns_200(self):
        res = self.client.get("/history")
        self.assertEqual(res.status_code, 200)

    def test_history_returns_list(self):
        res = self.client.get("/history")
        data = json.loads(res.data)
        self.assertIsInstance(data, list)

    # ── /analyze ──────────────────────────────────────────
    def test_analyze_no_input_returns_400(self):
        res = self.client.post(
            "/analyze",
            data=json.dumps({"text": ""}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_analyze_missing_body_returns_400(self):
        res = self.client.post(
            "/analyze",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    @patch("analyzer.requests.post")
    def test_analyze_valid_input_returns_200(self, mock_post):
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        res = self.client.post(
            "/analyze",
            data=json.dumps({"text": "suspicious powershell command"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("analysis", data)

    @patch("analyzer.requests.post")
    def test_analyze_saves_to_history(self, mock_post):
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        self.client.post(
            "/analyze",
            data=json.dumps({"text": "test malware sample"}),
            content_type="application/json"
        )
        res = self.client.get("/history")
        history = json.loads(res.data)
        self.assertGreater(len(history), 0)

    # ── /vt ───────────────────────────────────────────────
    def test_vt_no_query_returns_400(self):
        res = self.client.post(
            "/vt",
            data=json.dumps({"query": ""}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    @patch("vt.VT_API_KEY", "fake_key")
    @patch("vt.requests.get")
    def test_vt_valid_ip_returns_200(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {"attributes": {
                "last_analysis_stats": {
                    "malicious": 0, "suspicious": 0,
                    "harmless": 50, "undetected": 5
                },
                "country": "US", "as_owner": "Test"
            }}
        }
        res = self.client.post(
            "/vt",
            data=json.dumps({"query": "8.8.8.8"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("verdict", data)

    # ── /webhook/analyze ──────────────────────────────────
    def test_webhook_no_text_returns_400(self):
        res = self.client.post(
            "/webhook/analyze",
            data=json.dumps({"source": "n8n"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    @patch("analyzer.requests.post")
    def test_webhook_valid_input_returns_200(self, mock_post):
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        res = self.client.post(
            "/webhook/analyze",
            data=json.dumps({
                "text":   "suspicious email from ceo@fake-domain.ru",
                "source": "n8n_email_pipeline"
            }),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("analysis",  data)
        self.assertIn("source",    data)
        self.assertIn("webhook",   data)
        self.assertEqual(data["webhook"], "NSA_PROCESSED")

    @patch("analyzer.requests.post")
    def test_webhook_tags_source_in_history(self, mock_post):
        mock_post.return_value.json.return_value = MOCK_GROQ_RESPONSE
        self.client.post(
            "/webhook/analyze",
            data=json.dumps({"text": "test", "source": "slack_bot"}),
            content_type="application/json"
        )
        history = json.loads(self.client.get("/history").data)
        self.assertIn("[slack_bot]", history[0]["input"])


# ════════════════════════════════════════════════════════════
#  6. REPORT TESTS
# ════════════════════════════════════════════════════════════
class TestReport(unittest.TestCase):

    SAMPLE_HISTORY = [
        {
            "input": "Suspicious email from ceo@malicious-domain.ru asking for wire transfer.",
            "analysis": json.dumps({
                "risk_level":     "High",
                "risk_score":     91,
                "explanation":    "Classic BEC (Business Email Compromise) pattern.",
                "recommendation": "Block sender, alert finance team, escalate to IR."
            })
        },
        {
            "input": "http://bit.ly/3xR9mK — shortened URL received via Slack.",
            "analysis": json.dumps({
                "risk_level":     "Medium",
                "risk_score":     55,
                "explanation":    "Shortened URL obscures destination. Possible phishing.",
                "recommendation": "Expand URL before clicking. Submit to VirusTotal."
            })
        },
        {
            "input": "ping google.com",
            "analysis": json.dumps({
                "risk_level":     "Low",
                "risk_score":     4,
                "explanation":    "Standard ICMP ping. No threat indicators.",
                "recommendation": "No action required."
            })
        }
    ]

    def test_report_returns_bytes(self):
        """PDF generator should return a BytesIO buffer."""
        from report import generate_pdf
        buf = generate_pdf(self.SAMPLE_HISTORY)
        self.assertTrue(hasattr(buf, "read"))

    def test_report_is_valid_pdf(self):
        """Output should start with the PDF magic bytes."""
        from report import generate_pdf
        buf = generate_pdf(self.SAMPLE_HISTORY)
        header = buf.read(5)
        self.assertEqual(header, b"%PDF-")

    def test_report_empty_history(self):
        """PDF should still generate with zero incidents."""
        from report import generate_pdf
        buf = generate_pdf([])
        header = buf.read(5)
        self.assertEqual(header, b"%PDF-")

    def test_report_handles_malformed_analysis(self):
        """PDF should not crash if analysis JSON is broken."""
        from report import generate_pdf
        bad_history = [{"input": "test", "analysis": "NOT_JSON{{{{"}]
        try:
            buf = generate_pdf(bad_history)
            self.assertTrue(buf.read(5) == b"%PDF-")
        except Exception as e:
            self.fail(f"generate_pdf crashed on bad JSON: {e}")

if __name__ == "__main__":
    unittest.main(verbosity=2)