from django.urls import path
from .views      import SignUpView, SignInView, KakaoSignInView, KakaoSignInCallBackView, CartView, DeliveryLocationView, LogoutView 
import users.views

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/signin/kakao',KakaoSignInView.as_view()),
    path('/signin/kakao/callback',KakaoSignInCallBackView.as_view()),
    path('/logout', LogoutView.as_view()),
    path('/cart', CartView.as_view()),
    path('/register/location', DeliveryLocationView.as_view()),
    path('',users.views.kakaologin),
]