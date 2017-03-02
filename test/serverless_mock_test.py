import threading
import requests
import json
import os
from nose.tools import *
from server import Httpd

app_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "app")


class TestServerlessMock(object):
    def test_ok(self):
        ok_(True)

    def setUp(self):
        self.httpd = Httpd(app_path, 0)
        thread = threading.Thread(target=self.httpd.serve, args=())
        thread.daemon = True
        thread.start()

        self.prefix = "http://localhost:%d" % self.httpd.port

    def tearDown(self):
        self.httpd.shutdown()

    def test_return_hello_world(self):
        response = requests.get(self.url(""))
        eq_("Hello World", response.text)

    def test_run_get_function(self):
        response = requests.get(self.url("/hello"))

        eq_(200, response.status_code)

        data = response.json()

        eq_(200, data.get("statusCode"))
        body = json.loads(data.get("body"))
        eq_("Go Serverless v1.0! Your function executed successfully!", body.get("message"))

    def test_run_get_function_and_ignore_query_string_when_matching_path(self):
        response = requests.get(self.url("/hello?status=unknown"))

        eq_(200, response.status_code)

        data = response.json()

        eq_(200, data.get("statusCode"))
        body = json.loads(data.get("body"))
        eq_("Go Serverless v1.0! Your function executed successfully!", body.get("message"))

    def test_run_post_function(self):
        response = requests.post(self.url("/create"))
        eq_(200, response.status_code)

        data = response.json()
        eq_(201, data.get("statusCode"))

    def url(self, path):
        return "%s%s" % (self.prefix, path)
