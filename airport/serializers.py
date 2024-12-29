from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
    Ticket,
    Order,
)


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ("id", "name", )


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ("id", "name", "country", )


class CityListSerializer(CitySerializer):
    country = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "country", )


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ("id", "name", "cod_iata", "closest_big_city", )


class AirportListSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.CharField(
        source="closest_big_city.name", read_only=True
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "cod_iata", "closest_big_city", )


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ("id", "name", )


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "role", )


class CrewListSerializer(CrewSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "role")


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name", )


class AirlineCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = AirlineCompany
        fields = ("id", "name", "registration_country", "logo", )


class AirlineCompanyListSerializer(serializers.ModelSerializer):
    registration_country = serializers.CharField(
        source="registration_country.name", read_only=True
    )

    class Meta:
        model = AirlineCompany
        fields = ("id", "name", "registration_country", "logo", )


class FacilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Facility
        fields = ("id", "name", )


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "airline_company",
            "facilities",
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name", read_only=True
    )
    airline_company = serializers.CharField(
        source="airline_company.name", read_only=True
    )
    facilities = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "airline_company",
            "facilities",
        )


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", )


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="source.full_name", read_only=True
    )
    destination = serializers.CharField(
        source="destination.full_name", read_only=True
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = (
            "id",
            "name",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew_members",
        )


class FlightListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="route.source.closest_big_city", read_only=True
    )
    destination = serializers.CharField(
        source="route.destination.closest_big_city", read_only=True
    )
    airplane_name = serializers.CharField(
        source="airplane.name", read_only=True
    )
    crew_members = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "name",
            "route",
            "source",
            "destination",
            "airplane",
            "airplane_name",
            "departure_time",
            "arrival_time",
            "crew_members",
        )


class FlightRetrieveSerializer(FlightListSerializer):

    class Meta:
        model = Flight
        fields = (
            "id",
            "name",
            "route",
            "source",
            "destination",
            "airplane",
            "airplane_name",
            "departure_time",
            "arrival_time",
        )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", )

    def validate(self, attrs):
        print(f"{attrs=}")
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["flight"].airplane.rows,
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            ValidationError,
        )
        return data


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightRetrieveSerializer(many=False, read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
