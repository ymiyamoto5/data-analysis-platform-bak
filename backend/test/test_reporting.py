from ..models import reporting


def test_report(mocker):
    insmock = mocker.Mock()
    insmock.search.return_value = {'Test': 'test'}
    mocker.patch.object(reporting, "ElasticsearchWrapper",
                        mocker.Mock(return_value=insmock))

    assert reporting.Reporting.getMetaData() == {'Test': 'test'}
