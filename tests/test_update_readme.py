import io
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'update_readme.py'
README = 'Before\n<!-- writing starts -->\nOld writing\n<!-- writing ends -->\nAfter\n'


class UpdateReadmeTests(unittest.TestCase):
    def run_script(self, opener):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                Path('README.md').write_text(README, encoding='utf-8')
                with patch('urllib.request.urlopen', side_effect=opener):
                    runpy.run_path(str(SCRIPT))
                return Path('README.md').read_text(encoding='utf-8')
            finally:
                os.chdir(old_cwd)

    def test_feed_request_identifies_profile_automation(self):
        def serve(request, timeout):
            self.assertIsInstance(request, Request)
            self.assertEqual(request.full_url, 'https://udayprakash.com/rss.xml')
            self.assertIn('UdayGPrakash-ProfileFeed', request.get_header('User-agent'))
            self.assertEqual(timeout, 30)
            return io.BytesIO(b'<rss><channel/></rss>')
        self.assertEqual(self.run_script(serve), README.replace('Old writing\n', ''))

    def test_keeps_surrounding_content_and_renders_recent_post(self):
        from datetime import datetime, timezone
        from email.utils import format_datetime
        date = format_datetime(datetime.now(timezone.utc))
        feed = f'<rss><channel><item><title>Example</title><link>https://example.com/post</link><pubDate>{date}</pubDate></item></channel></rss>'
        result = self.run_script(lambda *_a, **_kw: io.BytesIO(feed.encode()))
        self.assertTrue(result.startswith('Before\n<!-- writing starts -->\n'))
        self.assertTrue(result.endswith('<!-- writing ends -->\nAfter\n'))
        self.assertIn('- [Example](https://example.com/post)', result)

    def test_old_posts_still_excluded(self):
        feed = b'<rss><channel><item><title>Old</title><link>https://example.com/old</link><pubDate>Sat, 04 Jan 2020 00:00:00 GMT</pubDate></item></channel></rss>'
        self.assertEqual(self.run_script(lambda *_a, **_kw: io.BytesIO(feed)), README.replace('Old writing\n', ''))

    def test_http_error_does_not_overwrite_readme(self):
        def fail(*_a, **_kw):
            raise HTTPError('https://udayprakash.com/rss.xml', 403, 'Forbidden', {}, None)
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                Path('README.md').write_text(README, encoding='utf-8')
                with patch('urllib.request.urlopen', side_effect=fail):
                    with self.assertRaises(HTTPError):
                        runpy.run_path(str(SCRIPT))
                self.assertEqual(Path('README.md').read_text(encoding='utf-8'), README)
            finally:
                os.chdir(old_cwd)


if __name__ == '__main__':
    unittest.main()
