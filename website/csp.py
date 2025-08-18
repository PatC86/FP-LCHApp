# Name      : csp
# Author    : Patrick Cronin
# Date      : 21/07/2025
# Updated   : 21/07/2025
# Purpose   : Define and enforce CSP

from flask import Response, request, jsonify, Blueprint

CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; ",
)

csp = Blueprint('csp', __name__)


# blueprint route for content security policy
# Need to remove -Report-Only
@csp.after_request
def after_request(response: Response):
    response.headers['Content-Security-Policy-Report-Only'] = CSP_POLICY
    return response


# blueprint route for content security policy reporting
@csp.route('/cspreport', methods=['POST'])
def cspreport():
    violations = request.get_json()
    print('Violations:', violations)
    return "", 204
