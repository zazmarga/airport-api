from rest_framework.reverse import reverse

from airport.models import (
    Country,
    AirportTimeZone,
    AirplaneType,
    Facility,
    Role
)

COUNTRY_URL = reverse("airport:country-list")
CITY_URL = reverse("airport:city-list")
TIMEZONE_URL = reverse("airport:airporttimezone-list")
AIRPORT_URL = reverse("airport:airport-list")
TYPE_URL = reverse("airport:airplanetype-list")
COMPANY_URL = reverse("airport:airlinecompany-list")
FACILITY_URL = reverse("airport:facility-list")
AIRPLANE_URL = reverse("airport:airplane-list")
ROLE_URL = reverse("airport:role-list")
CREW_URL = reverse("airport:crew-list")
ROUTE_URL = reverse("airport:route-list")
FLIGHT_URL = reverse("airport:flight-list")
ORDER_URL = reverse("airport:order-list")


def sample_country(**params):
    defaults = {
        "name": "Argentina",
    }
    defaults.update(params)
    return Country.objects.create(**defaults)


def sample_time_zone(**params):
    defaults = {
        "name": "America/Argentina/Buenos_Aires",
    }
    defaults.update(params)
    return AirportTimeZone.objects.create(**defaults)


def sample_type(**params):
    defaults = {
        "name": "Passenger Jets",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_facility(**params):
    defaults = {
        "name": "Wi-Fi",
    }
    defaults.update(params)
    return Facility.objects.create(**defaults)


def sample_role(**params):
    defaults = {
        "name": "Flight attendant",
    }
    defaults.update(params)
    return Role.objects.create(**defaults)
