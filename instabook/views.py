from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from instabook.models import Profile, Follow, Post, Like, Comment
from instabook.permisssions import IsProfileOwnerOrReadOnly
from instabook.serializers import (
    ProfileSerializer,
    FollowingListSerializer,
    FollowerListSerializer,
    PostSerializer,
    FollowRequestSerializer,
    LikeRequestSerializer,
    LikeListSerializer,
    PostListSerializer,
    CommentSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Returns a list of all user profiles that match the specified username parameter, if provided"""
        queryset = self.queryset
        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def perform_create(self, serializer):
        """Creates a new user profile and associates it with the authenticated user"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Updates an existing user profile for the authenticated user"""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Deletes the specified user profile if the authenticated user is the owner"""
        instance.delete(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by user username (ex. ?username=dicaprio)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Returns a list of all user profiles that match the 'username' parameter if it is specified"""
        return super().list(request, *args, **kwargs)

    @action(
        detail=True, methods=["POST"], serializer_class=FollowRequestSerializer
    )
    def follow(self, request):
        """Creates a request to subscribe to the user profile with the specified pk"""
        follower = self.request.user.profile
        following = self.get_object()

        if follower == following:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(
            follower=follower, following=following
        )

        if not created:
            return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": f"You are now following {following.full_name}."}
        )

    @action(
        detail=True, methods=["POST"], serializer_class=FollowRequestSerializer
    )
    def unfollow(self, request):
        """Cancels the subscription request to the user profile with the specified pk"""
        follower = self.request.user.profile
        following = self.get_object()

        follow = Follow.objects.filter(
            follower=follower, following=following
        ).first()

        if follower == following:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if not follow:
            return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()

        return Response(
            {"detail": f"You have unfollowed {following.full_name}."}
        )

    @action(detail=True, methods=["GET"])
    def followers(self, request):
        """Returns a list of all users who have subscribed to the user profile with the specified pk"""
        profile = self.get_object()
        serializer = FollowerListSerializer(profile.followers.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def following(self, request):
        """Returns a list of all user profiles that the user with the specified pk is subscribed to"""
        profile = self.get_object()
        serializer = FollowingListSerializer(
            profile.following.all(), many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def posts(self, request):
        """Returns a list of all posts created by the user with the specified pk"""
        profile = self.get_object()
        posts = Post.objects.filter(author=profile)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def following_posts(self, request):
        """Returns a list of all posts created by users that the user with the specified pk is subscribed to"""
        profile = self.get_object()
        followings = profile.followers.all()
        posts = Post.objects.filter(author__following__in=followings)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def liked_posts(self, request):
        """Returns a list of all posts that were liked by the user with the specified pk"""
        profile = self.get_object()
        likes = profile.likes.all()
        serializer = LikeListSerializer(likes, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsProfileOwnerOrReadOnly)

    def get_queryset(self):
        """Returns a queryset of Post objects, filtered by name if provided"""
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    def perform_create(self, serializer):
        """Saves the post author as the current user's profile on create"""
        serializer.save(author=self.request.user.profile)

    def perform_update(self, serializer):
        """Update a specific post, if the requesting user is the author"""
        serializer.save(post=self.request.user)

    def perform_destroy(self, instance):
        """Deletes the post if the current user is the author"""
        instance.save(post=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by post name (ex. ?name=the)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Returns a list of posts that match the 'name' parameter if it is specified"""
        return super().list(request, *args, **kwargs)

    @action(
        detail=True, methods=["POST"], serializer_class=LikeRequestSerializer
    )
    def like(self, request, pk=None):
        """Allows users to like a post"""
        profile = self.request.user.profile
        post = self.get_object()

        like, created = Like.objects.get_or_create(profile=profile, post=post)

        if not created:
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": f"You are liked {post.name} now."})

    @action(
        detail=True, methods=["POST"], serializer_class=LikeRequestSerializer
    )
    def unlike(self, request, pk=None):
        """Allows users to unlike a post"""
        profile = self.request.user.profile
        post = self.get_object()

        like = Like.objects.filter(profile=profile, post=post).first()

        if not like:
            return Response({"detail": "You have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()

        return Response({"detail": f"You have unliked {post.name}."})

    @action(detail=True, methods=["GET"])
    def comments(self, request, pk=None):
        """Returns all comments for a post"""
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], serializer_class=CommentSerializer)
    def add_comment(self, request, pk=None):
        """Adds a comment to a post"""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.save(profile=request.user.profile, post=post)

    @action(
        detail=True,
        methods=["PUT"],
        url_path="update_comment/(?P<comment_pk>[^/.]+)",
        serializer_class=CommentSerializer,
    )
    def update_comment(self, request, pk=None, comment_pk=None):
        """Updates a comment on a post"""
        comment = Comment.objects.get(pk=comment_pk)
        serializer = CommentSerializer(
            comment, data=request.data, partial=True
        )
        serializer.save()

    @action(
        detail=True,
        methods=["DELETE"],
        url_path="delete_comment/(?P<comment_pk>[^/.]+)",
        serializer_class=CommentSerializer,
    )
    def delete_comment(self, request, pk=None, comment_pk=None):
        """Deletes a comment from a post"""
        comment = Comment.objects.get(pk=comment_pk)

        if comment.profile != self.request.user.profile:
            return Response(status=status.HTTP_403_FORBIDDEN)

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
