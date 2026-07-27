import os
from pathlib import Path
import tempfile

from aiohttp.test_utils import AioHTTPTestCase

from src import create_app


class ApplicationRoutesTests(AioHTTPTestCase):
  async def get_application(self):
    self.static_dir = tempfile.TemporaryDirectory()
    Path(self.static_dir.name, 'index.html').write_text(
      '<!doctype html><title>MediaVault</title>',
      encoding='utf-8',
    )
    self.previous_static_dir = os.environ.get('MEDIAVAULT_STATIC_DIR')
    os.environ['MEDIAVAULT_STATIC_DIR'] = self.static_dir.name
    return create_app()

  async def asyncTearDown(self):
    await super().asyncTearDown()
    if self.previous_static_dir is None:
      os.environ.pop('MEDIAVAULT_STATIC_DIR', None)
    else:
      os.environ['MEDIAVAULT_STATIC_DIR'] = self.previous_static_dir
    self.static_dir.cleanup()

  async def test_health_endpoint(self):
    response = await self.client.get('/health')

    self.assertEqual(response.status, 200)
    payload = await response.json()
    self.assertEqual(payload['body']['status'], 'ok')

  async def test_unknown_frontend_route_uses_spa_fallback(self):
    response = await self.client.get('/watch')

    self.assertEqual(response.status, 200)
    self.assertIn('MediaVault', await response.text())

  async def test_proxy_route_is_not_handled_by_spa_fallback(self):
    response = await self.client.get('/proxy/missing')

    self.assertEqual(response.status, 404)
    self.assertNotIn('MediaVault', await response.text())
