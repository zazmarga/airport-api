from rest_framework import serializers

from airport.models import (
    Country, City, Airport, Role, Crew, AirplaneType, AirlineCompany, Facility, Airplane, Route,
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
    source = serializers.CharField(source="source.full_name", read_only=True)
    destination = serializers.CharField(source="destination.full_name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)
