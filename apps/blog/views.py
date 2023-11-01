from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from apps.category.models import Category

from .models import Post, ViewCount
from .serializers import PostListSerializer, PostSerializer
from .pagination import SmallSetPagination, MediumSetPagination, LargeSetPagination


class BlogListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        if Post.objects.all().exists():
            posts = Post.objects.all()

            paginator = SmallSetPagination()
            results = paginator.paginate_queryset(posts, request)

            serializer = PostListSerializer(results, many=True)

            return paginator.get_paginated_response({"posts": serializer.data})
        else:
            return Response(
                {"error": "No posts found"}, status=status.HTTP_404_NOT_FOUND
            )


class ListPostsByCategoryView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        slug = request.query_params.get("slug")

        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response(
                {"error": "No category found"}, status=status.HTTP_404_NOT_FOUND
            )

        posts = Post.objects.order_by("-published").all()

        sub_categories = Category.objects.filter(parent=category)
        filtered_categories = [category]
        for sub_category in sub_categories:
            filtered_categories.append(sub_category)

        posts = posts.filter(category__in=filtered_categories)

        if posts:
            paginator = SmallSetPagination()
            results = paginator.paginate_queryset(posts, request)

            serializer = PostListSerializer(results, many=True)

            return paginator.get_paginated_response({"posts": serializer.data})
        else:
            return Response(
                {"error": "No posts found"}, status=status.HTTP_404_NOT_FOUND
            )


class PostDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, slug, format=None):
        if Post.objects.filter(slug=slug).exists():
            post = Post.objects.get(slug=slug)
            serializer = PostSerializer(post)

            address = request.META.get("HTTP_X_FORWARDED_FOR")
            if address:
                ip = address.split(",")[-1].strip()
            else:
                ip = request.META.get("REMOTE_ADDR")

            if not ViewCount.objects.filter(post=post, ip_address=ip):
                view = ViewCount(post=post, ip_address=ip)
                view.save()
                post.views = post.get_view_count()
                post.save()

            print(post.views)

            return Response({"post": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
