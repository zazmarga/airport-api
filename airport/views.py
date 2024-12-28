from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Country, City,
)
from airport.serializers import (
    CountrySerializer, CitySerializer, CityListSerializer,
)


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer
        return CitySerializer

