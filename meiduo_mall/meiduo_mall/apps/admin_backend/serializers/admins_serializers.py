from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import User


class AdminSerializers(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = "__all__"

        # extra_kwargs = {
        #     "password": {"write_only": True}
        # }

    def create(self, validated_data):
        validated_data["is_staff"] = True

        validated_data["password"] = make_password(validated_data.get("password"))

        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get("password")

        if password:
            validated_data["password"] = make_password(password)

        else:
            validated_data["password"] = password
        return super().update(instance,validated_data)
