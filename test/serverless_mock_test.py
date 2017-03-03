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

    def test_simple_get(self):
        response = requests.get(self.url("/simple_get"))

        eq_(200, response.status_code)

        data = response.json()

        eq_(200, data.get("statusCode"))
        body = json.loads(data.get("body"))
        eq_("Go Serverless v1.0! Your function executed successfully!", body.get("message"))

    def test_simple_get_and_ignore_query_string(self):
        response = requests.get(self.url("/simple_get?status=unknown"))

        eq_(200, response.status_code)

        data = response.json()

        eq_(200, data.get("statusCode"))
        body = json.loads(data.get("body"))
        eq_("Go Serverless v1.0! Your function executed successfully!", body.get("message"))

    def test_simple_post(self):
        response = requests.post(self.url("/simple_post"))
        eq_(200, response.status_code)

        data = response.json()
        eq_(201, data.get("statusCode"))

    def test_post_with_payload(self):
        response = requests.post(self.url("/post_with_payload"), data=json.dumps({"id" : 123}))
        eq_(200, response.status_code)

        data = response.json()
        eq_(200, data.get("statusCode"))
        eq_({"id" : 123}, data.get("body"))

    def test_post_with_payload_and_template(self):
        response = requests.post(self.url("/post_with_payload_and_template"), data=json.dumps({"id" : 123}))
        eq_(200, response.status_code)

        data = response.json()
        eq_(200, data.get("statusCode"))
        eq_({"body" : {"id" : 123}}, data.get("body"))

    def url(self, path):
        return "%s%s" % (self.prefix, path)
