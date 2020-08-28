import os
import base64
import random
import string

from datetime import datetime, timezone
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from django.core.exceptions import ObjectDoesNotExist
from phone_verify.api import VerificationViewSet
from phone_verify.serializers import PhoneSerializer, SMSVerificationSerializer
from phone_verify.services import send_security_code_and_generate_session_token
from phone_verify.base import response

from .models import Customer, UBIRWiFi
from store.models import StoreTableStatus, Store, Company, DiningType
from .serializers import CustomerSerializer, UBIRWiFiSerializer
from users.permissions import IsUBIRLoggedIn, IsServiceman


class UBIRWiFiViewSet(ModelViewSet):
    serializer_class = UBIRWiFiSerializer
    queryset = UBIRWiFi.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        api_key = os.getenv('API_KEY')
        if 'header' in request.headers:
            try:
                decoded_string = base64.b64decode(request.headers['header']).decode("utf-8")
            except:
                return Response({'Error': 'Unauthorized Request.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'Error': 'Unauthorized Request.'}, status=status.HTTP_401_UNAUTHORIZED)

        if decoded_string == api_key:
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
            except Exception as e:
                return Response({'Error': 'There is a problem in processing request.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'Error': 'Unauthorized Request.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='login', permission_classes=[IsUBIRLoggedIn])
    def login(self, request):
        company_id = request.data['companyId']
        store_id = request.data['storeId']
        table_id = request.data['tableId']
        try:
            customer = Customer.objects.get(phone=phone)
        except ObjectDoesNotExist:
            return Response({'Error': 'You must login to the store Guest WiFi to use this service.  Please login to "UBIRserve WiFi"'}, status=status.HTTP_404_NOT_FOUND)
        data = CustomerSerializer(instance=customer).data
        return Response(data, status=status.HTTP_200_OK)


class CustomVerificationViewSet(VerificationViewSet):
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsUBIRLoggedIn],
        serializer_class=PhoneSerializer,
    )
    def register(self, request):
        is_specific_phone_number = False
        company_id = request.data.pop('companyId')
        store_id = request.data.pop('storeId')
        table_id = request.data.pop('tableId')
        phone_number_without_code = request.data['phone_number_without_code']
        company = Company.objects.get(company_id=company_id)
        specific_phone_number_prefix = company.specific_phone_number_prefix
        if specific_phone_number_prefix != "" and phone_number_without_code.startswith(specific_phone_number_prefix):
            is_specific_phone_number = True
        if not is_specific_phone_number:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            request_ip_address = ip
            try:
                store = Store.objects.get(store_id=store_id)
            except Store.DoesNotExist:
                return response.Ok({"error": "Store does not exist."})
            if not store.ip_addresses:
                return response.Ok({"error": "Store does not have IP addresses defined yet."})
            if "0.0.0.0" not in store.ip_addresses:
                if request_ip_address not in store.ip_addresses:
                    return response.Ok({"error": "You must login to the store Guest WiFi to use this service. Please login to \"UBIRserve WiFi\""})
        # wifi_logins = UBIRWiFi.objects.filter(phone=phone_number_without_code)
        # if not wifi_logins:
        #    return response.Ok({"error": "You must login to the store Guest WiFi to use this service.  "
        #                                 "Please login to \"UBIRserve WiFi\""})
        try:
            customer = Customer.objects.get(phone=phone_number_without_code)
            if customer.is_in_store:
                return response.Ok({"error": "This phone number is already logged in this company/store."})
        except Customer.DoesNotExist:
            pass
        try:
            store_table_status = StoreTableStatus.objects.get(store__store_id=store_id, table_seat=table_id)
            if store_table_status.status == StoreTableStatus.CLOSED:
                return response.Ok({"error": "The table is closed now. Please ask the service person."})
        except StoreTableStatus.DoesNotExist:
            return response.Ok({"error": "This table is closed. "
                                         "Please tell a server or the manager you need a new table"})
        if is_specific_phone_number:
            try:
                customer = Customer.objects.get(phone=phone_number_without_code)
            except:
                customer = Customer(phone=phone_number_without_code)
            customer.company_id = company_id
            customer.store_id = store_id
            customer.table_id = table_id
            customer.is_in_store = True
            session_token = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(25))
            customer.session_token = session_token
            customer.save()
            return response.Ok({"session_token": session_token, "is_authenticated": True})
        else:
            serializer = PhoneSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            session_token = send_security_code_and_generate_session_token(
                str(serializer.validated_data["phone_number"])
            )
            return response.Ok({"session_token": session_token, "is_authenticated": False})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=PhoneSerializer,
    )
    def wait_list_register(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"])
        )
        return response.Ok({"session_token": session_token, "is_authenticated": False})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSVerificationSerializer,
    )
    def verify(self, request):
        company_id = request.data.pop('companyId')
        store_id = request.data.pop('storeId')
        table_id = request.data.pop('tableId')
        serializer = SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number_without_code = request.data['phone_number_without_code']
        try:
            customer = Customer.objects.get(phone=phone_number_without_code)
        except:
            customer = Customer(phone=phone_number_without_code)
        customer.company_id = company_id
        customer.store_id = store_id
        customer.table_id = table_id
        customer.is_in_store = True
        customer.session_token = request.data['session_token']
        customer.save()
        return response.Ok({"message": "Security code is valid."})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSVerificationSerializer,
    )
    def wait_list_verify(self, request):
        company_id = request.data.pop('companyId')
        store_id = request.data.pop('storeId')
        table_id = request.data.pop('tableId')
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        number_in_party = request.data['number_in_party']
        selected_dining_type = request.data['selected_dining_type']
        serializer = SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number_without_code = request.data['phone_number_without_code']
        try:
            customer = Customer.objects.get(phone=phone_number_without_code)
        except:
            customer = Customer(phone=phone_number_without_code)
        customer.company_id = company_id
        customer.store_id = store_id
        customer.table_id = table_id
        customer.first_name = first_name
        customer.last_name = last_name
        customer.number_in_party = number_in_party
        dining_type = DiningType.objects.get(title=selected_dining_type)
        customer.dining_type = dining_type
        customer.is_in_store = True
        customer.session_token = request.data['session_token']
        customer.start_time = datetime.now(timezone.utc)
        customer.save()
        return response.Ok({"message": "Security code is valid."})
