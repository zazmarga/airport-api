from django.urls import path, include
from rest_framework import routers

from airport.views import (
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    RoleViewSet,
    CrewViewSet,
    AirplaneTypeViewSet,
    AirlineCompanyViewSet,
    FacilityViewSet,
    AirplaneViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
    AirportTimeZoneViewSet,
)

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("time_zones", AirportTimeZoneViewSet)
router.register("airports", AirportViewSet)
router.register("roles", RoleViewSet)
router.register("crews", CrewViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airline_companies", AirlineCompanyViewSet)
router.register("facilities", FacilityViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
