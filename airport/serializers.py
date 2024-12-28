from rest_framework import serializers

from airport.models import (
    Country, City, Airport, Role, Crew,
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
    closest_big_city = serializers.CharField(source="closest_big_city.name", read_only=True)

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
        fields = ("id", "first_name", "last_name", "role" )


class CrewListSerializer(CrewSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "role")

