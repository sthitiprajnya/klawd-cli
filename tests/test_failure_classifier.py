import logging
from unittest.mock import patch
from src.application.orchestration.failure_classifier import alert_human

@patch("src.application.orchestration.failure_classifier.uuid.uuid4")
@patch("src.application.orchestration.failure_classifier.httpx.put")
def test_alert_human_success(mock_put, mock_uuid4, caplog):
    mock_uuid4.return_value = "1234-5678"
    room = "#myroom:matrix.org"
    error_message = "Disk is on fire"

    with caplog.at_level(logging.CRITICAL):
        alert_human(room, error_message)

    expected_room_id = "%23myroom%3Amatrix.org"
    expected_url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{expected_room_id}/send/m.room.message/1234-5678"

    mock_put.assert_called_once_with(
        expected_url,
        json={"msgtype": "m.text", "body": "🚨 URGENT INFRA FAILURE: Disk is on fire"},
        timeout=2.0
    )
    assert "INFRA failure detected: Disk is on fire" in caplog.text

@patch("src.application.orchestration.failure_classifier.httpx.put")
def test_alert_human_exception(mock_put, caplog):
    mock_put.side_effect = Exception("Network unreachable")
    room = "#myroom:matrix.org"
    error_message = "Disk is on fire"

    with caplog.at_level(logging.ERROR):
        alert_human(room, error_message)

    assert "Failed to alert human on Matrix: Network unreachable" in caplog.text
