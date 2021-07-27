def test_company_metadata(session):
    r = session.get('http://app/company/')
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/json'

    res = r.json()
    assert res['protocol_version'] == 1
    assert isinstance(res['provider_name'], str)

def test_individual_metadata(session):
    r = session.get('http://app/individual/')
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/json'

    res = r.json()
    assert res['protocol_version'] == 1
    assert isinstance(res['provider_name'], str)
