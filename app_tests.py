import urllib3
from flask import Flask, jsonify
from flask_testing import LiveServerTestCase, TestCase
import unittest

class MyTest(LiveServerTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        # Default port is 5000
        app.config['LIVESERVER_PORT'] = 3306
        # Default timeout is 5 seconds
        app.config['LIVESERVER_TIMEOUT'] = 10
        return app

    def test_server_is_up_and_running(self):
        response = urllib3.HTTPResponse(self.get_server_url())
        self.assertEqual(response.connection, 200)

if __name__ == '__main__':
    unittest.main()