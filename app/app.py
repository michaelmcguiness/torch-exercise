from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler

from api.services.mta_service import MTAService

from api.controllers.mta_controller import Status, Uptime


def create_app():
    app = Flask(__name__)
    api = Api(app)

    scheduler = APScheduler()

    mta_service = MTAService()

    @scheduler.task('interval', seconds=30)
    def update_mta_services():
        mta_service.update()

    scheduler.init_app(app)
    scheduler.start()

    api.add_resource(Status, '/v1/status/<string:line>',
                     resource_class_kwargs={'mta_service': mta_service})
    api.add_resource(Uptime, '/v1/uptime/<string:line>',
                     resource_class_kwargs={'mta_service': mta_service})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
