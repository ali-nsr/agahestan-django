from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from .serializers import (
    ProvinceListSerializer, ProvinceDetailSerializer,
    CityListSerializer, CityDetailSerializer,
    NeighborhoodSerializer
)
from ...models import Province, City, Neighborhood

class ProvinceListAPIView(generics.GenericAPIView):
    serializer_class = ProvinceListSerializer

    def get(self, request):
        qs = Province.objects.only('id', 'name', 'slug')
        serializer = self.get_serializer(qs, many=True)
        return Response(data=serializer.data)


class ProvinceRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ProvinceDetailSerializer

    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(Province, pk=pk)
        serializer = self.get_serializer(obj)
        return Response(data=serializer.data)


class CityListAPIView(generics.GenericAPIView):
    serializer_class = CityListSerializer

    def get(self, request):
        qs = (
            City.objects.select_related('province')
            .only('id', 'name', 'slug', 'province')
            .prefetch_related(
                Prefetch(
                    'neighborhoods',
                    queryset=Neighborhood.objects.only('id', 'name', 'slug', 'city'),
                )
            )
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(data=serializer.data)


class CityRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CityDetailSerializer

    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(City, pk=pk)
        serializer = self.get_serializer(obj)
        return Response(data=serializer.data)


class NeighborhoodListAPIView(generics.GenericAPIView):
    serializer_class = NeighborhoodSerializer

    def get(self, request):
        qs = (
            Neighborhood.objects.select_related('city', 'city__province')
            .only('id', 'name', 'slug', 'city')
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(data=serializer.data)


class NeighborhoodRetrieveAPIView(generics.GenericAPIView):
    serializer_class = NeighborhoodSerializer

    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(Neighborhood, pk=pk)
        serializer = self.get_serializer(obj)
        return Response(data=serializer.data)
