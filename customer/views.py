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

    def create(self, request, *args, **kwargs):
        phone = request.data['phone']
        customer, created = Customer.objects.update_or_create(defaults=request.data)
        data = CustomerSerializer(instance=customer).data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_200_OK, headers=headers)
