# Screening Integration

This project provides an example of a service implementing a [PassFort Integration](https://passfort.github.io/integration-docs/)
supporting PEPs, Sanctions and Adverse Media screening.

Only demo checks are supported, no provider specific logic is implemented.


## Running Locally

Requires at least Python 3.7

You can run the application in a Python environment of your choosing, install the
dependencies from `requirements.txt` and `requirements-dev.txt` and start
the service with `python main.py`.


## Deploying

This stateless service is designed to be deployed to Google App Engine, the `app.yaml`
and `Dockerfile` reflect this. However, there is no requirement for your integration
to use such a platform.
