from django.urls import path, include
from rest_framework import routers

from instabook.views import ProfileViewSet, PostViewSet

app_name = "instabook"
router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
