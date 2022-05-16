import json, bcrypt, jwt, re
import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib   import auth

from django.http            import JsonResponse
from django.views           import View
from django.core.exceptions import ValidationError

from core.utils      import signin_decorator
from .models         import User, Cart, DeliveryLocation, Token
from products.models import Product
from my_settings     import SECRET_KEY, ALGORITHM, KAKAO_REST_API_KEY


class SignUpView(View):
    def post(self, request):
        try:
            data     = json.loads(request.body)
            name     = data['name']
            email    = data['email']
            password = data['password']
            # email_check(user_email)

            domain_list = ['naver.com', 'gmail.com', 'daum.net']
            if email[email.index('@')+1:] not in domain_list:
                return JsonResponse({'message' : 'INVALID_DOMAIN'}, status = 400)

            regex_email    = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9-.]+$' 
            regex_password = '\S{8,25}'
            if not re.match(regex_email, email):
                return JsonResponse({'message' : 'INVALID_EMAIL'}, status = 400)
            if not re.match(regex_password, password):
                return JsonResponse({'message' : 'INVALID_PASSWORD'}, status = 400)


            if User.objects.filter(email=email).exists():
                return JsonResponse({"MESSAGE" : "EMAIL_ALREADY_EXIST"}, status=400)

            # password_check(user_password)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            User.objects.create(
                name     = name,
                email    = email,
                password = hashed_password
            )
            return JsonResponse({"MESSAGE" : "SUCCESS"}, status=201)

        except ValidationError :
            return JsonResponse({'massage':"VALIDATION_ERROR"}, status=400)

        except KeyError :
            return JsonResponse({'massage':"KEY_ERROR"}, status=400)


class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            user = User.objects.get(email = data['email'])
            
            if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({'message' : 'INVALID_USER'}, status=400)

            token = jwt.encode({ 'id' : user.id, 'exp':datetime.utcnow() + timedelta(days=1)}, SECRET_KEY, algorithm='HS256')

            if Token.objects.filter(user=user).exists():
                Token.objects.filter(user=user).delete()
                
            Token.objects.create(user=user, token=token)
            return JsonResponse({'message' : 'SUCCESS', 'access_token' : token}, status=200)

        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status=401)

class LogoutView(View):
    @signin_decorator
    def post(self, request):
        user = request.user

        Token.objects.get(user_id=user.id).delete()

        return JsonResponse({"message": "LOGOUT_SUCCESS"}, status=200)


class KakaoSignInView(View):
    def get(self, request):
        client_id = KAKAO_REST_API_KEY
        redirect_uri = 'http://127.0.0.1:8000/users/signin/kakao/callback'
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        )



class KakaoSignInCallBackView(View):
    def get(self, request):
        try:
            auth_code = request.GET.get('code')
            kakao_token_api = 'https://kauth.kakao.com/oauth/token'
            data = {
                'grant_type': 'authorization_co de',
                'client_id': KAKAO_REST_API_KEY,
                'redirection_uri': 'http://127.0.0.1:8000/accounts/signin/kakao/callback',
                'code': auth_code
            }

            token_response = requests.post(kakao_token_api, data=data)

            access_token = token_response.json().get('access_token')

            kakao_user = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'}).json()
            kakao_id      = kakao_user['id']
            name          = kakao_user['kakao_account']['profile']['nickname']
            email         = kakao_user['kakao_account']['email']

            user, created = User.objects.get_or_create(
                    kakao_id = kakao_id,
                    defaults = {'name'      : name,
                                'email'     : email
                    }
            )
            
            token = jwt.encode({'id': user.id}, SECRET_KEY, ALGORITHM)

            return render(request, 'kakao_login_success.html')
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)
        


def kakaologin(request):
    return render(request, 'kakao_login.html')



class CartView(View):
    # @signin_decorator
    def post(self, request):        
        try:
            data = json.loads(request.body)
            if 'itemOption' in data:
                size = data['itemOption']
            else:
                size = None

            print(data)

            # user_id        = request.user
            # product_id     = Product.objects.get(id=data['product_id'])
            product     = Product.objects.get(sku_number=data['sku_number'])
            # quantity       = int(data['quantity'])
            
            # if Cart.objects.filter(user=user_id, product=product_id).exists():
            if Cart.objects.filter(product=product, size=size).exists():
                return JsonResponse({'MESSAGE' : 'ITEM_ALREADY_EXIST'}, status=400)
                
            Cart.objects.create(
                # user     = user_id,
                product  = product,
                # quantity = quantity,
                size=size
            )

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status= 201)

        except KeyError: 
            return JsonResponse({'MESSAGE' : 'KEY_ERROR'}, status= 400)

        except Product.DoesNotExist: 
            return JsonResponse({'MESSAGE' : 'ITEM_DOES_NOT_EXIST'}, status = 401)

    # @signin_decorator
    def get(self, request):
        # cart_list = Cart.objects.filter(user_id=request.user)
        cart_list = Cart.objects.filter(user_id=None)
        
        result=[  # image, brand, item_name, size, quantity, price, sale_price
           {
            "image"          : cart.product.image_set.all()[0].url,
            "brand"          : cart.product.brand,
            "name"           : cart.product.name,
            "selectedOption" : cart.size,
            "option"         : [option.size for option in cart.product.option_set.all()],
            "quantity"       : cart.quantity,
            "price"          : cart.product.price,
            "sale_price"     : cart.product.sale_price,
            "sku_number"     : cart.product.sku_number,
            "product_id"     : cart.product.id,
            "cart_id"        : cart.id,
            }
        for cart in cart_list
        ]

        return JsonResponse({'result': result}, status=200)


    # @signin_decorator
    def delete(self, request):
        cart_id = request.GET.get('cartId')

        if cart_id: 
            Cart.objects.get(id=cart_id).delete()
            return JsonResponse({'MESSAGE':'ITEM_DELETED'},status = 200)

        if not Cart.objects.filter(user=request.user).exists(): 
            return JsonResponse({'MESSAGE':'DOES_NOT_EXIST'}, status = 400)

        Cart.objects.filter(user=request.user).delete()
        return JsonResponse({'MESSAGE':'ALL_DELETED'},status = 200)
    

    # @signin_decorator
    def patch(self, request):
        try:
            data      = json.loads(request.body)
            size_list = data['itemOption']
            print(size_list)
            # quantity      = data['quantity']
            # cart_id       = data['cart_id']
            # cart          = Cart.objects.get(id=cart_id, user_id=request.user)
            cart_list = Cart.objects.filter(user_id=None)

            for i, cart_item in enumerate(cart_list):
                cart_item.size = size_list[i]
                cart_item.save()
            
            return JsonResponse({'MESSAGE':'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE':'OBJECT_NOT_EXITST'}, status=400)





class DeliveryLocationView(View):
    @signin_decorator
    def post(self, request):
        try:
            data     = json.loads(request.body)
            user  = request.user
            post_number = data['post_number']
            address1 = data['address1']
            address2 = data['address2']

            DeliveryLocation.objects.filter(user=user).delete()

            DeliveryLocation.objects.create(
                user = user,
                post_number = post_number,
                address1 = address1,
                address2 = address2
            )

            return JsonResponse({'MESSAGE':'SUCCESS'}, status=201)
        
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE':'OBJECT_NOT_EXIST'}, status=400)

    @signin_decorator
    def get(self, request):
        try:
            user = request.user
            location = DeliveryLocation.objects.get(user=user)

            result = {
                "post_number" : location.post_number,
                "address1"    : location.address1,
                "address2"    : location.address2,
            }

            return JsonResponse({'result': result}, status=200)
        
        except DeliveryLocation.DoesNotExist:
            return JsonResponse({'MESSAGE':'DELIVERYLOCATION_NOT_EXIST'}, status=400)
