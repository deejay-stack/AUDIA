"""Create isolated test apps; normal development uses the app in root app.py."""
from flask import Flask
from app import app as main_app
from modules.auth import install_security
from modules.database import init_database


def create_app(config):
    application = Flask("app", root_path=main_app.root_path,
                        static_folder=main_app.static_folder, static_url_path="/static",
                        template_folder=main_app.template_folder,
                        instance_path=main_app.instance_path)
    application.config.update(main_app.config)
    application.config.update(config)
    init_database(application)
    for blueprint in main_app.blueprints.values():
        application.register_blueprint(blueprint)
    install_security(application)
    # Reuse the actual page functions, not a separate test implementation.
    for rule in main_app.url_map.iter_rules():
        if rule.endpoint not in application.view_functions:
            application.add_url_rule(rule.rule, endpoint=rule.endpoint,
                                     view_func=main_app.view_functions[rule.endpoint],
                                     methods=rule.methods)
    for errors in main_app.error_handler_spec.get(None, {}).values():
        for exception, handler in errors.items():
            application.register_error_handler(exception, handler)
    return application
