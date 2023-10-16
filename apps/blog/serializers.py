from rest_framework import serializers
from .models import *


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        field = [
            "id",
            "name",
            "slug",
            "views",
        ]
