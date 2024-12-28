from django.contrib import admin

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
    Ticket,
)

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Role)
admin.site.register(Crew)
admin.site.register(AirplaneType)
admin.site.register(AirlineCompany)
admin.site.register(Facility)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)
