import unittest
import requests


class TestEndpoint(unittest.TestCase):
    def test_send_json(self):
        with open("images.json", "r") as f:
            res = requests.post("http://127.0.0.1:8000", params={"height": 180, "sex": "m"}, data=f.read())
            print(res.status_code)
            assert res.status_code == 200


if __name__ == '__main__':
    unittest.main()
