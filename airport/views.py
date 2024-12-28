from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Country,
    City,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer
        return CitySerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("country")
        return queryset


