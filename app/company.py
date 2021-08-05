import json
import os
import re
from random import randrange
from uuid import UUID

from dataclasses import dataclass
from typing import Optional, List, Tuple

from flask import Flask, Blueprint, send_file, request, abort, Response

from app.auth import auth
from app.api import (
    CommercialRelationshipType,
    Charge,
    DemoResultType,
    Error,
    ErrorType,
    Field,
    StartCheckResponse,
    StartCheckRequest,
    PollCheckResponse,
    PollCheckRequest,
    validate_models,
)

from app.demo_results import (try_load_company_result, try_load_demo_error_result)
from app.http_signature import HTTPSignatureAuth
from app.startup import integration_key_store

blueprint = Blueprint('company', __name__, url_prefix='/company')

SUPPORTED_COUNTRIES = ['GBR', 'USA', 'CAN', 'NLD']

PROVIDER_ID = "540eec24-11ae-4d60-a64f-71b9948e2b15"

@blueprint.route('/')
def index():
    return send_file('../static/company/metadata.json', cache_timeout=-1)

@blueprint.route('/config')
@auth.login_required
def get_config():
    return send_file('../static/company/config.json', cache_timeout=-1)


@blueprint.route('/checks', methods=['POST'])
@auth.login_required
@validate_models
def start_check(req: StartCheckRequest) -> StartCheckResponse:
    if 'ERROR' in req.demo_result:
        return try_load_demo_error_result(StartCheckResponse, req.demo_result)


    return StartCheckResponse({
        'provider_id': PROVIDER_ID,
        'reference': "12345",
        'custom_data': {
            'counter': randrange(6)
        },
        "provider_data": "Demo result. Did not make request to provider."
    })


@blueprint.route('/checks/<uuid:_check_id>/poll', methods=['POST'])
@auth.login_required
@validate_models
def poll_check_result(req: PollCheckRequest, _check_id: UUID) -> PollCheckResponse:
    remaining_polls = req.custom_data["counter"]

    if remaining_polls == 0:
        return try_load_company_result(req.commercial_relationship, req.demo_result)

    return PollCheckResponse({
        "provider_id": PROVIDER_ID,
        "reference": req.reference,
        "custom_data": {"counter": remaining_polls - 1 },
        "provider_data": "Demo result. Did not make request to provider.",
    })