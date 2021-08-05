import base64
import os
import time

from email.utils import formatdate
from uuid import uuid4

from app.company import PROVIDER_ID


def test_run_check_protected(session, auth):
    # Should require authentication
    r = session.post('http://app/company/checks', json={})
    assert r.status_code == 401

    # Should require correct key
    bad_key = os.urandom(256)
    r = session.post('http://app/company/checks', json={}, auth=auth(key=bad_key))
    assert r.status_code == 401

    # Should require '(request-target)' *and* 'date' headers to be signed
    r = session.post('http://app/company/checks', json={}, auth=auth(headers=['date']))
    assert r.status_code == 401

    # Should require 'date' header to be recent
    old_date = formatdate(time.time() - 120)
    r = session.post('http://app/company/checks', json={}, headers={'date': old_date}, auth=auth())
    assert r.status_code == 401

    # Should require digest to be correct
    bad_digest = base64.b64encode(os.urandom(256)).decode()
    r = session.post('http://app/company/checks', json={}, headers={'digest': f'SHA-256={bad_digest}'}, auth=auth())
    assert r.status_code == 401


def test_company_check_smoke(session, auth):
    r = session.post('http://app/company/checks', json={
        'id': str(uuid4()),
        'check_input': {
            'entity_type': 'COMPANY',
            'metadata': {
                'name': 'PASSFORT LIMITED',
                'number': '09565115',
                'country_of_incorporation': 'GBR'
            },
        },
        'commercial_relationship': 'DIRECT',
        'provider_config': {},
        'demo_result': 'ALL_DATA'
    }, auth=auth())
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/json'

    res = r.json()

    assert res['errors'] == []


def test_company_check_unsupported_demo_result(session, auth):
    check_id = uuid4()
    r = session.post(f'http://app/company/checks/{check_id}/poll', json={
        'id': str(check_id),
        'provider_id': PROVIDER_ID, 
        'reference': '12345',
        'demo_result': 'NOT_A_REAL_DEMO_RESULT',
        'commercial_relationship': 'DIRECT',
        'provider_config': {},
        'custom_data': { 'counter': 0 },
    }, auth=auth())

    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/json'

    res = r.json()

    assert res['errors'] == [{
        'type': 'UNSUPPORTED_DEMO_RESULT',
        'message': 'Demo result is not supported.',
    }]

def test_company_check_invalid_credentials(session, auth):
    r = session.post('http://app/company/checks', json={
        'id': str(uuid4()),
        'check_input': {
            'entity_type': 'COMPANY',
            'metadata': {
                'name': 'PASSFORT LIMITED',
                'number': '09565115',
                'country_of_incorporation': 'GBR'
            }
        },
        'commercial_relationship': 'DIRECT',
        'provider_config': {},
        'demo_result': 'ERROR_INVALID_CREDENTIALS'
    }, auth=auth())
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/json'

    res = r.json()

    assert res['errors'] == [{
        'type': 'INVALID_CREDENTIALS',
        'message': 'Username or password is invalid.',
    }]