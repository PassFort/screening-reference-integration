import json
import os
import re

from app.api import (
    Charge,
    CommercialRelationshipType,
    DemoResultType,
    EntityType,
    PollCheckResponse,
)

UNSUPPORTED_DEMO_RESULT_FILENAME = '../static/demo_results/UNSUPPORTED_DEMO_RESULT.json'

def _sanitize_filename(value: str, program=re.compile('^[a-z0-9A-Z_]+$')):
    if not program.match(value):
        abort(Response('Invalid demo request', status=400))
    return value


def _get_file_content(model, filename):
    try:
        # Load file relative to current script
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as file:
            demo_response = model().import_data(json.load(file), apply_defaults=True)
    except FileNotFoundError:
        return None

    return demo_response

def _filename(entity_type: EntityType, demo_result: str):
    if entity_type == EntityType.INDIVIDUAL:
        return f'../static/demo_results/individuals/{_sanitize_filename(demo_result)}.json'
    elif entity_type == EntityType.COMPANY:   
        return f'../static/demo_results/companies/{_sanitize_filename(demo_result)}.json'


def _try_load_result(entity_type: EntityType, commercial_relationship: CommercialRelationshipType, name: str):
    if name in {
        DemoResultType.ANY, DemoResultType.ANY_CHARGE
    }: 
        name = DemoResultType.ALL_DATA

    filename = _filename(entity_type, name)
    if filename is None:
        return _get_file_content(PollCheckResponse, UNSUPPORTED_DEMO_RESULT_FILENAME)

    demo_response = _get_file_content(PollCheckResponse, filename)
    if demo_response is None:
        return _get_file_content(PollCheckResponse, UNSUPPORTED_DEMO_RESULT_FILENAME)

    if commercial_relationship == CommercialRelationshipType.PASSFORT:
        demo_response.charges = [
            Charge({
                'amount': 100,
                'reference': 'DUMMY REFERENCE'
            }),
            Charge({
                'amount': 50,
                'sku': 'NORMAL'
            })
        ]
    
    return demo_response


def try_load_individual_result(commercial_relationship: CommercialRelationshipType, name: str):
    return _try_load_result(EntityType.INDIVIDUAL, commercial_relationship, name)

def try_load_company_result(commercial_relationship: CommercialRelationshipType, name: str):
    return _try_load_result(EntityType.COMPANY, commercial_relationship, name)

def try_load_demo_error_result(response_model, name: str):
    filename = f'../static/demo_results/errors/{_sanitize_filename(name)}.json'
    demo_response = _get_file_content(response_model, filename)
    return demo_response
