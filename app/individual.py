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
    EntityType,
    Error,
    ErrorType,
    Field,
    StartCheckResponse,
    StartCheckRequest,
    PollCheckResponse,
    PollCheckRequest,
    validate_models,
)
from app.demo_results import (try_load_individual_result, try_load_demo_error_result)
from app.http_signature import HTTPSignatureAuth
from app.startup import integration_key_store

blueprint = Blueprint('individual', __name__, url_prefix='/individual')

SUPPORTED_COUNTRIES = ['GBR', 'USA', 'CAN', 'NLD']

PROVIDER_ID = "6e15bc41-17a1-4568-8549-b5f828b13060"

@blueprint.route('/')
def index():
    return send_file('../static/individual/metadata.json', cache_timeout=-1)

@blueprint.route('/config')
@auth.login_required
def get_config():
    return send_file('../static/individual/config.json', cache_timeout=-1)


@blueprint.route('/checks', methods=['POST'])
@auth.login_required
@validate_models
def run_check(req: StartCheckRequest) -> StartCheckResponse:
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
        return try_load_individual_result(req.commercial_relationship, req.demo_result)

    return PollCheckResponse({
        "provider_id": PROVIDER_ID,
        "reference": req.reference,
        "custom_data": {"counter": remaining_polls - 1 },
        "provider_data": "Demo result. Did not make request to provider.",
    })
