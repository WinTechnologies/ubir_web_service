from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.authtoken.models import Token

from customer.models import UBIRWiFi, Customer
from store.models import Company


class IsUBIRLoggedIn(BasePermission):
    def has_permission(self, request, view):
        try:
            phone_number_without_code = request.data['phone_number_without_code']
            if UBIRWiFi.objects.filter(phone=phone_number_without_code):
                return True
        except:
            pass
        try:
            company_id = request.data['companyId']
            company = Company.objects.get(company_id=company_id)
            specific_phone_number_prefix = company.specific_phone_number_prefix
            if specific_phone_number_prefix != "" and phone_number_without_code.startswith(specific_phone_number_prefix):
                return True
        except:
            pass
        return False


class IsOnTable(BasePermission):
    def has_permission(self, request, view):
        try:
            company_id = request.data['companyId']
            store_id = request.data['storeId']
            table_id = request.data['tableId']
            phone_number_without_code = request.data['phone_number']
            session_token = request.data['session_token']
            customer = Customer.objects.get(is_in_store=True,
                                            phone=phone_number_without_code,
                                            company_id=company_id,
                                            store_id=store_id)
            if customer.session_token == session_token:
                return True
        except:
            pass
        return False


class IsServiceman(BasePermission):
    def has_permission(self, request, view):
        try:
            token = request.data['token']
            Token.objects.get(key=token)
            return True
        except:
            pass
        return False
