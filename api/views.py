from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import KBEntry, QueryLog
from .permissions import IsAdminUser
from .serializers import (
    KBEntrySerializer,
    KBQuerySerializer,
    LoginSerializer,
    RegisterSerializer,
)


def generate_access_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        company = user.company

        return Response(
            {
                "username": user.username,
                "company_name": company.company_name,
                "api_key": company.api_key,
                "access": generate_access_token(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {
                    "error": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        company = user.company

        return Response(
            {
                "access": generate_access_token(user),
                "company_name": company.company_name,
                "api_key": company.api_key,
            },
            status=status.HTTP_200_OK,
        )


class KBQueryView(APIView):
    def post(self, request):
        serializer = KBQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_term = serializer.validated_data["search"]
        company = request.user.company

        with transaction.atomic():
            results = KBEntry.objects.filter(
                Q(question__icontains=search_term)
                | Q(answer__icontains=search_term)
            ).order_by("id")

            results_count = results.count()

            results_data = KBEntrySerializer(
                results,
                many=True,
            ).data

            QueryLog.objects.create(
                company=company,
                search_term=search_term,
                results_count=results_count,
            )

        return Response(
            {
                "search": search_term,
                "count": results_count,
                "results": results_data,
            },
            status=status.HTTP_200_OK,
        )


class UsageSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(
            total=Count("id")
        )["total"]

        active_companies = (
            QueryLog.objects
            .values("company")
            .distinct()
            .count()
        )

        top_search_terms = list(
            QueryLog.objects
            .values("search_term")
            .annotate(count=Count("id"))
            .order_by("-count", "search_term")[:5]
        )

        return Response(
            {
                "total_queries": total_queries,
                "active_companies": active_companies,
                "top_search_terms": top_search_terms,
            },
            status=status.HTTP_200_OK,
        )
