from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Country,
    City,
    Airport,
    Role,
    Crew, AirplaneType, AirlineCompany, Facility,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirportSerializer,
    AirportListSerializer,
    RoleSerializer,
    CrewSerializer,
    CrewListSerializer, AirplaneTypeSerializer, AirlineCompanySerializer, AirlineCompanyListSerializer,
    FacilitySerializer,
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


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("closest_big_city")
        return queryset


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("role")
        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirlineCompanyViewSet(viewsets.ModelViewSet):
    queryset = AirlineCompany.objects.all()
    serializer_class = AirlineCompanySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirlineCompanyListSerializer
        return AirlineCompanySerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("registration_country")
        return queryset


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
