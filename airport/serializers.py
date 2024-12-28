from rest_framework import serializers

from airport.models import (
    Country, City, Airport, Role, Crew, AirplaneType, AirlineCompany, Facility,
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


