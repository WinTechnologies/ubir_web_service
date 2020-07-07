from rest_framework.permissions import BasePermission, SAFE_METHODS

from customer.models import UBIRWiFi, Customer


class IsUBIRLoggedIn(BasePermission):
    def has_permission(self, request, view):
        try:
            phone_number_without_code = request.data['phone_number_without_code']
            if UBIRWiFi.objects.filter(phone=phone_number_without_code):
                return True
        except:
            pass
        return False


class IsOnTable(BasePermission):
    def has_permission(self, request, view):
        try:
            phone_number_without_code = request.data['phone_number']
            session_token = request.data['session_token']
            customer = Customer.objects.get(phone=phone_number_without_code)
            if customer.session_token == session_token:
                return True
        except:
            return False
        return False


class IsClientOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return hasattr(request.user, "client") and obj == request.user.client
