from rest_framework import serializers
from .models import Profile, Post


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "profile_picture",
            "username",
            "bio",
            "first_name",
            "last_name",
            "followers",
        )
        read_only_fields = ("user",)


class PostSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "user", "content", "hashtags", "created_at")
