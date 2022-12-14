from flask import make_response, render_template
from werkzeug.exceptions import HTTPException

class InputError(HTTPException):
    def __init__(self, status_code, error_code, error_message, html_page, trackers=None, tracker=None, uname=None, condition=None, current=None, log=None, choices=None):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(render_template(html_page, error=error_message, trackers=trackers, tracker=tracker, uname=uname, condition=condition, current=current, log=log, choices=choices), status_code)

class ServerError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(error_message, status_code)