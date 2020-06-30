import os
import base64
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from .models import Customer
from .serializers import CustomerSerializer
from common.permissions import IsClientOwner


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsClientOwner]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        api_key = os.getenv('API_KEY')
        if 'header' in request.headers:
            try:
                decoded_string = base64.b64decode(request.headers['header']).decode("utf-8")
            except:
                return Response({'Error': 'Unauthorized Request.'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Unauthorized Request.'}, status=status.HTTP_200_OK)

        if decoded_string == api_key:
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
            except Exception as e:
                return Response({'Error': 'There is a problem in processing request.'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Unauthorized Request.'}, status=status.HTTP_200_OK)
