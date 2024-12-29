from rest_framework import viewsets

from airport.models import (
    Country,
    City,
    Airport,
    Role,
    Crew,
    AirplaneType,
    AirlineCompany,
    Facility,
    Airplane,
    Route,
    Flight,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirportSerializer,
    AirportListSerializer,
    RoleSerializer,
    CrewSerializer,
    CrewListSerializer,
    AirplaneTypeSerializer,
    AirlineCompanySerializer,
    AirlineCompanyListSerializer,
    FacilitySerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    RouteSerializer,
    RouteListSerializer,
    FlightSerializer,
    FlightListSerializer,
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


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.select_related(
            "airplane_type",
            "airline_company__registration_country",
        )
        queryset = queryset.prefetch_related("facilities")
        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "source__closest_big_city__country",
            "destination__closest_big_city__country",
        )
        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FlightListSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "route__source__closest_big_city__country",
            "route__destination__closest_big_city__country",
            "airplane__airplane_type",
            "airplane__airline_company",
        )
        queryset = queryset.prefetch_related("crew_members__role")
        return queryset
