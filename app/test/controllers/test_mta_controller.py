import unittest
import json
import requests_mock

from app.app import create_app
from app.api.services.mta_service import MTAService, MTA_STATUS_ENDPOINT
from app.test.mock_responses import mta_service_status


@requests_mock.Mocker()
class TestMTAController(unittest.TestCase):
    def setUp(self) -> None:
        application = create_app()
        application.app_context().push()
        self.client = application.test_client()

    def test_get_line_status(self, mock) -> None:
        mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)
        response = self.client.get('/v1/status/123')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['isDelayed'] is True

    def test_get_line_uptime(self, mock) -> None:
        mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)
        response = self.client.get('/v1/uptime/123')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['uptime'] == 0
