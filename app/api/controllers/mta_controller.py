from flask_restful import Resource, reqparse

from api.libs.util import get_error

_user_parser = reqparse.RequestParser()
_user_parser.add_argument("line", type=str, required=True, help="This field cannot be blank")


class Status(Resource):
    def __init__(self, **kwargs):
        self.mta_service = kwargs['mta_service']

    def get(self, line: str):
        """Returns whether or not the line is currently delayed"""

        if not self.mta_service.line_exists(line):
            return get_error(400, "Line does not exist")

        return {'isDelayed': self.mta_service.get_is_delayed(line)}


class Uptime(Resource):
    def __init__(self, **kwargs):
        self.mta_service = kwargs['mta_service']

    def get(self, line: str):
        """Returns the fraction of time that line has not been delayed since inception"""

        if not self.mta_service.line_exists(line):
            return get_error(400, "Line does not exist")

        return {'uptime': self.mta_service.get_uptime(line)}
