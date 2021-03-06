from flask import Flask, request
from flask.logging import create_logger

from app.company import blueprint as company_blueprint
from app.individual import blueprint as individual_blueprint

# If `entrypoint` is not defined in app.yaml, App Engine will look
# for an app called `app` in `main.py`
app = Flask(__name__)
logger = create_logger(app)

@app.before_request
def pre_request_logging():
    request_data = '\n' + request.data.decode('utf8')
    request_data = request_data.replace('\n', '\n    ')

    logger.info(f'{request.method} {request.url}{request_data}')


@app.after_request
def post_request_logging(response):
    if response.direct_passthrough:
        response_data = '\n(direct pass-through)'
    else:
        response_data = '\n' + response.data.decode('utf8')
    response_data = response_data.replace('\n', '\n    ')

    logger.info(f'{response.status} {request.url}{response_data}')
    return response

app.register_blueprint(company_blueprint)
app.register_blueprint(individual_blueprint)