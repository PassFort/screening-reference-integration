import json
import os
import re

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
from app.http_signature import HTTPSignatureAuth
from app.startup import integration_key_store

blueprint = Blueprint('company', __name__, url_prefix='/company')

SUPPORTED_COUNTRIES = ['GBR', 'USA', 'CAN', 'NLD']


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
    return StartCheckResponse.error([Error({
        'type': ErrorType.INVALID_CHECK_INPUT,
        'message': 'Not implemented!',
    })])


@blueprint.route('/checks/<uuid:check_id>/poll', methods=['POST'])
@auth.login_required
@validate_models
def poll_check_result(req: PollCheckRequest) -> PollCheckResponse:
   return PollCheckResponse.error([Error({
        'type': ErrorType.INVALID_CHECK_INPUT,
        'message': 'Not implemented!',
    })])
