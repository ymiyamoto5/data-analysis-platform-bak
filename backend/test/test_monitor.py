from ..models.monitor import Monitor


def test_monitor_run_normal(mocker):
    mon = Monitor()
    es_mock = mocker.Mock()
    es_mock.create_index = mocker.Mock()
    es_mock.exists.return_value = False
    es_mock.upsert = mocker.Mock()
    es_mock.search.return_value = [
        {'displacement': 1},
        {'displacement': 1},
        {'displacement': 1},
        {'displacement': 1},
        {'displacement': 1}
    ]
    mocker.patch.object(mon, 'es', es_mock)

    assert mon.run('event_id') == ''


def test_monitor_run_detect_anomaly(mocker):
    mon = Monitor()
    es_mock = mocker.Mock()
    es_mock.create_index = mocker.Mock()
    es_mock.exists.return_value = False
    es_mock.upsert = mocker.Mock()
    es_mock.search.return_value = [
        {'displacement': 0},
        {'displacement': 0},
        {'displacement': 0},
        {'displacement': 0},
        {'displacement': 0}
    ]
    mocker.patch.object(mon, 'es', es_mock)

    assert mon.run('event_id') == '変位0が一定回数以上発生しています'


def test_monitor_run_data_nothing(mocker):
    mon = Monitor()
    es_mock = mocker.Mock()
    es_mock.create_index = mocker.Mock()
    es_mock.exists.return_value = False
    es_mock.upsert = mocker.Mock()
    es_mock.search.return_value = {}
    mocker.patch.object(mon, 'es', es_mock)

    assert mon.run('event_id') == '一定時間センサーデータを受信しませんでした'
