import json, jwt

from django.test import TransactionTestCase, Client

from unittest.mock import patch, MagicMock

from users.models import User
from my_settings  import SECRET_KEY, ALGORITHMS

class KakaoLoginTest(TransactionTestCase):
    def setUp(self):
         User.objects.create(
            email    = 'maxsummer256@gmail.com',
            kakao_id = 123,
            point    = 100000000
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch('users.views.requests')
    def test_kakao_login_success_account_exist(self, mock_data_request):
        client = Client()

        class MockDataResponse:
            def json(self):
                return {
                    "id": 123,
                    "kakao_account": { 
                        "email" : 'maxsummer256@gmail.com'
                    }
                }

        mock_data_request.get = MagicMock(return_value=MockDataResponse())
        header                = {"HTTP_Authorization" : "access_token"}
        response              = client.get('/users/login/kakao', content_type="application/json", **header)
        login_token           = jwt.encode({'user_id': 1}, SECRET_KEY, ALGORITHMS)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'access_token': login_token})

class KakaoSignUpTest(TransactionTestCase):
    @patch('users.views.requests')
    def test_kakao_login_success_account_nonexist(self, mock_data_request):
        client = Client()

        class MockDataResponse:
            def json(self):
                return {
                    "id": 123,
                    "kakao_account": { 
                        "email" : 'maxsummer256@gmail.com'
                    }
                }

        mock_data_request.get = MagicMock(return_value=MockDataResponse())
        header                = {"HTTP_Authorization" : "access_token"}
        response              = client.get('/users/login/kakao', content_type="application/json", **header)
        login_token           = jwt.encode({'user_id': 1}, SECRET_KEY, ALGORITHMS)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'access_token': login_token})

    def test_kakao_login_fail(self):
        client   = Client()

        header   = {"No_Authorization" : ""}
        response = client.get("/users/login/kakao", content_type="application/json", **header)
        
        self.assertEqual(response.status_code, 401)