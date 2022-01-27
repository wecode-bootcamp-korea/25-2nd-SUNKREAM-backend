import jwt
import requests
from json.decoder import JSONDecodeError

from django.http  import JsonResponse
from django.views import View

from users.models import User
from my_settings  import SECRET_KEY, ALGORITHMS

class KakaoLogin(View):
    def get(self, request):
        try: 
            token = request.headers.get('Authorization')

            if token == None:
                return JsonResponse({'messsage': 'INVALID_TOKEN'}, status=401)

            kakao_account = requests.get('https://kapi.kakao.com/v2/user/me', headers = {'Authorization': f'Bearer {token}'}).json()
            print('::::kakao_account:', kakao_account)

            if not User.objects.filter(kakao_id=kakao_account['id']).exists():
                user = User.objects.create(
                    kakao_id = kakao_account['id'],
                    email    = kakao_account['kakao_account']['email'],
                    name     = kakao_account['kakao_account']['profile']['nickname']
            )
            user = User.objects.get(kakao_id=kakao_account['id'])

            access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm=ALGORITHMS)

            return JsonResponse({'access_token': access_token}, status=201)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        
        except JSONDecodeError:
            return JsonResponse({'message': 'JSON_DECODE_ERROR'}, status=400)

        except jwt.DecodeError:
            return JsonResponse({'message': 'JWT_DECODE_ERROR'}, status=400)

        except ConnectionError:
            return JsonResponse({'message': 'CONNECTION_ERROR'}, status=400)