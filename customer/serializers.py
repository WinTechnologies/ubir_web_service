from rest_framework import serializers

from customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        id = validated_data.get("id", None)
        customer, created = Customer.objects.update_or_create(
            id=id, defaults=validated_data
        )
        return customer

    class Meta:
        model = Customer
        fields = '__all__'
