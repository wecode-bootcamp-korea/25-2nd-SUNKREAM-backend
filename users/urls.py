from django.urls import path

from users.views import KakaoLogin

urlpatterns = [
    path('/login/kakao', KakaoLogin.as_view()),
]