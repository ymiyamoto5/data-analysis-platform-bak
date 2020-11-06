from .. import views


def test_views_monitoring_start(mocker):
    monmock = mocker.Mock()
    monmock.run.return_value = ''
    mocker.patch.object(views, 'Monitor', mocker.Mock(return_value=monmock))

    reqmock = mocker.Mock()
    reqmock.json = {'eventId': 'event_id'}
    mocker.patch.object(views, 'request', reqmock)

    resp = views.monitoring_start()
    assert resp.get_data() == b'{"message": ""}'


def test_views_record_stop_event(mocker):
    monmock = mocker.Mock()
    monmock.record_stop_event = mocker.Mock()
    mocker.patch.object(views, 'Monitor', mocker.Mock(return_value=monmock))

    reqmock = mocker.Mock()
    reqmock.json = {
        'stoppedTime': 'stopped_time',
        'stopReason': 'stop_reason',
        'stopFactor': 'stop_factor',
        'eventId': 'event_id'
    }
    mocker.patch.object(views, 'request', reqmock)

    resp = views.record_stop_event()
    print(resp.get_data())
    assert resp.get_data() == '{"message": "停止中"}'.encode(
        'ascii', 'backslashreplace')


def test_views_report(mocker):
    repmock = mocker.Mock()
    repmock.getMetaData.return_value = {"Test": "Test"}
    mocker.patch.object(views, 'Reporting', mocker.Mock(return_value=repmock))
    jsonify_mock = mocker.patch.object(views, 'jsonify', mocker.Mock())

    views.report()

    jsonify_mock.assert_called_once()
