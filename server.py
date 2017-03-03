import BaseHTTPServer
import imp
import json
import os
import yaml
import re
import sys
from jsonpath_rw import jsonpath, parse


class Httpd(object):
    app_path = None

    def __init__(self, app_path, port):
        Httpd.app_path = app_path
        sys.path.append(app_path)

        self.http_server = BaseHTTPServer.HTTPServer(("", port), RequestHandler)
        self.port = self.http_server.server_port

    def shutdown(self):
        self.http_server.shutdown()

    def serve(self):
        self.http_server.serve_forever()


class Handler(object):
    def __init__(self):
        self.method = None
        self.path = None
        self.module = None
        self.function_name = None
        self.template = None


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        handler = self.find_handler("get", self.path)
        self.perform(handler)

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        handler = self.find_handler("post", self.path)
        self.perform(handler)

    def find_handler(self, method, path):
        handlers = self.create_handlers()

        for handler in handlers:
            if handler.method.lower() == method and handler.path == path.split("?")[0]:
                return handler
        return None

    def perform(self, handler):
        if handler is not None:
            if handler.method == "post":
                content_length = int(self.headers.getheader('content-length', 0))

                if content_length > 0:
                    raw_body = self.rfile.read(content_length)
                    event = json.loads(raw_body)
                    if handler.template is not None:
                        template = handler.template
                        event = self.replace_input_json_in_template(raw_body, template)

                    body = getattr(handler.module, handler.function_name)(event, {})
                else:
                    body = getattr(handler.module, handler.function_name)({}, {})
            else:
                body = getattr(handler.module, handler.function_name)({}, {})
            self.wfile.write(json.dumps(body))
        else:
            self.wfile.write("Hello World")

    def replace_input_json_in_template(self, raw_body, template):
        input_json = re.search("\$input\.json\(['\"](.*?)['\"]\)", template)
        if input_json:
            command, path = input_json.group(0), input_json.group(1)
            jsonpath_expr = parse(path)
            command_result = jsonpath_expr.find(raw_body)[0].value
            return json.loads(template.replace(command, command_result))

    @staticmethod
    def create_handlers():
        yaml_path = os.path.join(Httpd.app_path, "serverless.yml")
        stream = file(yaml_path, 'r')
        content = yaml.load(stream)
        handlers = []
        functions = content.get("functions")
        for (name, hander_object) in functions.iteritems():
            events = hander_object.get("events")
            handler_name = hander_object["handler"]

            split_ = handler_name.split(".")[0:-1]
            function_name = handler_name.split(".").pop()
            join = os.path.join(*split_)
            module_path = os.path.join(Httpd.app_path, join)
            handler_module = imp.load_source(handler_name, module_path + ".py")
            for event in events:
                if event.has_key("http"):
                    path = event["http"]["path"]
                    method = event["http"]["method"]


                    if path[0] != "/":
                        path = "/" + path
                    h = Handler()
                    h.method = method
                    h.path = path
                    h.module = handler_module
                    h.function_name = function_name

                    jsonpath_expr = parse("http.request.template.'application/json'")
                    templates = jsonpath_expr.find(event)
                    if len(templates) > 0:
                        h.template = templates[0].value

                    handlers.append(h)
        return handlers


if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test", "app")
    Httpd(app_path, 8887).serve()
