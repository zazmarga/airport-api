from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
    Order,
    AirportTimeZone,
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
    OrderSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
    AirportTimeZoneSerializer,
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


class AirportTimeZoneViewSet(viewsets.ModelViewSet):
    queryset = AirportTimeZone.objects.all()
    serializer_class = AirportTimeZoneSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirportListSerializer
        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "closest_big_city__country", "time_zone"
        )
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
        if self.action in ("list", "retrieve"):
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

    @staticmethod
    def _params_to_ints(query_string: str) -> list:
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        if self.request.method == "GET":
            airline_companies_ids = self.request.query_params.get("companies")
            if airline_companies_ids:
                airline_companies_ids = self._params_to_ints(
                    airline_companies_ids
                )
                queryset = queryset.filter(
                    airplane__airline_company__id__in=airline_companies_ids
                )

        if self.request.method in ("GET", "POST"):
            queryset = queryset.select_related(
                "route__source__closest_big_city",
                "route__destination__closest_big_city",
                "airplane__airplane_type",
                "airplane__airline_company__registration_country",
            )
            queryset = queryset.prefetch_related("crew_members__role")

        return queryset.distinct()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        "user", "tickets",
        "tickets__flight",
        "tickets__flight__airplane__airline_company__registration_country",
        "tickets__flight__route__source",
        "tickets__flight__route__destination",
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
