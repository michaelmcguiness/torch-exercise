import datetime
from app.api.services.mta_service import MTAService, MTA_STATUS_ENDPOINT
from app.test.mock_responses import mta_service_status


def test_update_modifies_line_info_correctly(requests_mock):
    """Update method should fetch service statuses and update internal 'service_info' map"""
    requests_mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)
    old_time = datetime.datetime.now()

    mta_service = MTAService()
    mta_service.update()

    assert mta_service.line_map['123']['is_delayed'] is False
    assert mta_service.line_map['123']['downtime'] == 0
    assert mta_service.line_map['123']['uptime'] > 0
    assert mta_service.line_map['123']['last_update'] > old_time

    assert mta_service.line_map['456']['is_delayed'] is True
    assert mta_service.line_map['456']['downtime'] > 0
    assert mta_service.line_map['456']['uptime'] == 0
    assert mta_service.line_map['456']['last_update'] > old_time


def test_experiencing_delays_output(requests_mock, capsys):
    """
    When a line transitions from not delayed → delayed,
    should print the following message: to console or to a logfile:
    “Line <line_name> is experiencing delays”.
    """
    requests_mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)

    # not delayed -> delayed
    mta_service = MTAService()
    mta_service.line_map["456"] = {
        "is_delayed": False,
        "uptime": 0,
        "downtime": 0,
        "last_update": datetime.datetime.now()
    }
    mta_service.update()
    captured = capsys.readouterr()
    assert captured.out == "Line 456 is experiencing delays\n"


def test_now_recovered_output(requests_mock, capsys):
    """
    When a line transitions from delayed → not delayed,
    should print the following message: to console or to a logfile:
    “Line <line_name> is now recovered”.
    """
    requests_mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)

    # delayed -> not delayed
    mta_service = MTAService()
    mta_service.line_map["123"] = {
        "is_delayed": True,
        "uptime": 0,
        "downtime": 0,
        "last_update": datetime.datetime.now()
    }
    mta_service.update()
    captured = capsys.readouterr()
    assert captured.out == "Line 123 is now recovered\n"


def test_get_is_delayed(requests_mock):
    """
    get_is_delayed method should return status of a service (true if delayed, else false)
    """
    requests_mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)

    mta_service = MTAService()
    mta_service.update()

    is_delayed_123 = mta_service.get_is_delayed("123")
    is_delayed_456 = mta_service.get_is_delayed("456")

    assert is_delayed_123 is False
    assert is_delayed_456 is True


def test_get_uptime(requests_mock):
    """
    uptime method should return 'uptime' for a given service since inception
    'uptime' defined as '1 - (total_time_delayed/total_time)'
    """
    requests_mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)

    mta_service = MTAService()
    mta_service.line_map["123"] = {
        "is_delayed": True,
        "uptime": 10000,
        "downtime": 40000,
        "last_update": datetime.datetime.now()
    }

    # if delayed, adds time since last update to downtime
    assert mta_service.get_uptime("123") < 0.2
    assert mta_service.get_uptime("123") > 0.19

    # if not delayed, adds time since last update to uptime
    mta_service.line_map["123"]["is_delayed"] = False
    assert mta_service.get_uptime("123") > 0.2
    assert mta_service.get_uptime("123") < 0.21


def test_service_exists(requests_mock):
    """"service_exists method should return True if service in service_info map, else False"""
    requests_mock.get(MTA_STATUS_ENDPOINT, text=mta_service_status)

    mta_service = MTAService()
    mta_service.line_map["123"] = {
        "is_delayed": True,
        "uptime": 0,
        "downtime": 0,
        "last_update": datetime.datetime.now()
    }

    assert mta_service.line_exists("123") is True
    assert mta_service.line_exists("INVALID") is False
