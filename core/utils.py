import jwt

from django.http  import JsonResponse

from my_settings  import ALGORITHM, SECRET_KEY
from users.models import User, Token

def signin_decorator(func):
    def wrapper(self, request, *args, **kargs):
        try:
            token        = request.headers.get('Authorization', None)
            payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)

            if not Token.objects.filter(user_id=payload['id']).exists():
                return JsonResponse({"message": "INVALID_USER"})

            user         = User.objects.get(id = payload['id'])
            request.user = user
        
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID_TOKEN' }, status=400)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status=400)
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "EXPIRED_TOKEN"}, status = 400)
        return func(self,request,*args,**kargs)
    return wrapper