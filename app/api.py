import inspect
from functools import wraps
from typing import Iterable, TypeVar, Optional, Type, List

from schematics import Model
from schematics.common import NOT_NONE
from schematics.types import (
    FloatType, UUIDType, StringType, ModelType, ListType, DateType, BaseType, DictType, IntType,
    BooleanType, PolyModelType
)
from schematics.exceptions import DataError
from schematics.types.base import TypeMeta
from flask import abort, request, Response, jsonify

# Validation
T = TypeVar('T')


def _first(x: Iterable[T]) -> Optional[T]:
    return next(iter(x), None)


def _get_input_annotation(signature: inspect.signature) -> Optional[Type[Model]]:
    first_param: Optional[inspect.Parameter] = _first(signature.parameters.values())
    if first_param is None:
        return none

    if first_param.kind not in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
        return None

    if not issubclass(first_param.annotation, Model):
        return None

    return first_param.annotation


def validate_models(fn):
    """
    Creates a Schematics Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    """

    signature = inspect.signature(fn)

    assert issubclass(signature.return_annotation,
                      Model), 'Must have a return type annotation'
    output_model = signature.return_annotation
    input_model = _get_input_annotation(signature)

    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        if input_model is None:
            res = fn(*args, **kwargs)
        else:
            model = None
            try:
                model = input_model().import_data(request.json, apply_defaults=True)
                model.validate()
            except DataError as e:
                abort(Response(str(e), status=400))

            res = fn(model, *args, **kwargs)

        assert isinstance(res, output_model)

        return jsonify(res.serialize())

    return wrapped_fn


class BaseModel(Model):
    class Options:
        export_level = NOT_NONE


# Inheriting this class will make an enum exhaustive
class EnumMeta(TypeMeta):
    def __new__(mcs, name, bases, attrs):
        attrs['choices'] = [v for k, v in attrs.items(
        ) if not k.startswith('_') and k.isupper()]
        return TypeMeta.__new__(mcs, name, bases, attrs)


class ApproxDateType(DateType):
    formats = ['%Y-%m']


# Intentionally non-exhaustive
class DemoResultType(StringType):
    ANY = 'ANY'
    ANY_CHARGE = 'ANY_CHARGE'
    NO_MATCH = 'NO_MATCH'

    # Errors
    ERROR_INVALID_CREDENTIALS = 'ERROR_INVALID_CREDENTIALS'
    ERROR_ANY_PROVIDER_MESSAGE = 'ERROR_ANY_PROVIDER_MESSAGE'
    ERROR_CONNECTION_TO_PROVIDER = 'ERROR_CONNECTION_TO_PROVIDER'


class CommercialRelationshipType(StringType, metaclass=EnumMeta):
    PASSFORT = 'PASSFORT'
    DIRECT = 'DIRECT'


class ErrorType(StringType, metaclass=EnumMeta):
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    INVALID_CONFIG = 'INVALID_CONFIG'
    MISSING_CHECK_INPUT = 'MISSING_CHECK_INPUT'
    INVALID_CHECK_INPUT = 'INVALID_CHECK_INPUT'
    PROVIDER_CONNECTION = 'PROVIDER_CONNECTION'
    PROVIDER_MESSAGE = 'PROVIDER_MESSAGE'
    UNSUPPORTED_DEMO_RESULT = 'UNSUPPORTED_DEMO_RESULT'


class ErrorSubType(StringType, metaclass=EnumMeta):
    # INVALID_CHECK_INPUT
    UNSUPPORTED_COUNTRY = 'UNSUPPORTED_COUNTRY'


class EntityType(StringType, metaclass=EnumMeta):
    COMPANY = 'COMPANY'
    INDIVIDUAL = 'INDIVIDUAL'


class EntityData(BaseModel):
    entity_type = EntityType(required=True)


class AddressType(StringType, metaclass=EnumMeta):
    STRUCTURED = 'STRUCTURED'


class ProviderConfig(BaseModel):
    ...


class ProviderCredentials(BaseModel):
    apikey = StringType(required=True)


# Local field names (for errors)
class Field(StringType):
    COUNTRY_OF_INCORPORATION = 'COUNTRY_OF_INCORPORATION'

class Warning(BaseModel):
    ...

class Error(BaseModel):
    type = ErrorType(required=True)
    sub_type = ErrorSubType()
    message = StringType(required=True)
    data = DictType(StringType(), default=None)

    @staticmethod
    def unsupported_country():
        return Error({
            'type': ErrorType.INVALID_CHECK_INPUT,
            'sub_type': ErrorSubType.UNSUPPORTED_COUNTRY,
            'message': 'Country not supported.',
        })

    @staticmethod
    def missing_required_field(field: str):
        return Error({
            'type': ErrorType.MISSING_CHECK_INPUT,
            'data': {
                'field': field,
            },
            'message': f'Missing required field ({field})',
        })



class Warn(BaseModel):
    type = ErrorType(required=True)
    message = StringType(required=True)



class Charge(BaseModel):
    amount = IntType(required=True)
    reference = StringType(default=None)
    sku = StringType(default=None)


class CustomData(BaseModel):
    counter = IntType(required=True)

class StartCheckRequest(BaseModel):
    id = UUIDType(required=True)
    demo_result = StringType(default=None)
    commercial_relationship = CommercialRelationshipType(required=True)
    check_input = ModelType(EntityData, required=True)
    provider_config = ModelType(ProviderConfig, required=True)
    provider_credentials = ModelType(ProviderConfig, default=None)


class StartCheckResponse(BaseModel):
    provider_id = UUIDType(default=None)
    reference = StringType(default=None)
    custom_data = ModelType(CustomData, required=True)
    provider_data = BaseType(default=None)
    warnings = ListType(ModelType(Warning), required=True, default=list)
    errors = ListType(ModelType(Error), required=True, default=list)

    def error(errors):
        return StartCheckResponse({
            'errors': errors,    
        })


class PollCheckRequest(BaseModel):
    id = UUIDType(required=True)
    provider_id = UUIDType(required=True)
    reference = StringType(required=True)
    demo_result = StringType(default=None)
    commercial_relationship = CommercialRelationshipType(required=True)
    provider_config = ModelType(ProviderConfig, required=True)
    provider_credentials = ModelType(ProviderConfig, default=None)
    custom_data = ModelType(CustomData, required=True)


class PollCheckResponse(BaseModel):
    provider_id = UUIDType(default=None)
    reference = StringType(default=None)
    custom_data = ModelType(CustomData, required=True)
    provider_data = BaseType(required=True)

    check_output = ModelType(EntityData, default=None)

    warnings = ListType(ModelType(Warning), required=True, default=list)
    errors = ListType(ModelType(Error), required=True, default=list)

    def error(errors):
        return PollCheckResponse({
            'errors': errors,    
        })