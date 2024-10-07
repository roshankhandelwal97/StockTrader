from django.contrib.auth import login, authenticate
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserCreate(views.APIView):
    # Allow any user (authenticated or not) to hit this API.
    permission_classes = ()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)  # Log the user in.
            token = get_tokens_for_user(user)
            return Response({'user': serializer.data, 'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            token = get_tokens_for_user(user)
            return Response({'token': token, 'message': 'User Logged In'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    def post(self, request):
        # Simply instruct the client to delete the token as JWTs are inherently stateless
        return Response({'message': 'Please delete your token'}, status=status.HTTP_200_OK)
