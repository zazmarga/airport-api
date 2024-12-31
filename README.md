# Airport - API

This is a  Django RFW project.
Airport-api provides information about various flights, airlines and airports around the world. 
With the ability to arrange ticket booking for registered users.

### Built with:

 - Python
 - Django RFW
 - djangorestframework-simplejwt
 - Pillow
 - Swagger: drf-spectacular

### In This Project:

 - User built-in Django
 - Standard Django RFW pagination
 - JWT Authentication
 - Permissions: Authenticated users read-only
 - Permissions: Admin all except destroy
 - For own orders, permission: all without exception
 - Standard Django RFW Throttling

### Diagram of Project

[HERE](diagram.png)

### Installing using GitHub

Install PostgresSQL and create db

    git clone https://github.com/zazmarga/airport-api.git
    cd airport_api
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Create .env file with variables (see env.example)

    python manage.py migrate
    python manage.py runserver

### Run with docker

Docker should be installed

    docker-compose build
    docker-compose up

### Getting access

 * create user via /api/user/register/
 * get access token via /api/user/token/

### Features

 * Admin panel  /admin/
 * Documentation is located:
   - /api/doc/swagger/
   - /api/doc/redoc/
   - /api/schema/
 * Creating Country, City, AirportTimeZone (ex. "Europe/Madrid" for Barcelona)
 * Create Airports with code IATA (ex. "BCN" for Barcelona) & closest big city
 * Create Route entre two airports
 * Create AirplaneType, AirlineCompany (with logo-image)
 * Create Facility (ex. "Wi-Fi") & Airplane with list of facilities
 * Create Role (ex. "Co-pilot") & Crew with role
 * Create Flight with list of crews, departure_time & arrival_time
   (taking into time zone and the ability to calculate the flight duration)
 * Managing orders and tickets 

### Added Features:

 * Filter Flights by Airline Company (ex. "/?companies=1,3")
 * Calculating the flight duration
 * Managing flights (ex. "is_completed" - True, cannot delete past flights, but its will be displayed at the end of list)

###  Some screenshots of the project

[screenshots1](airport-api1.png)
[screenshots2](airport-api2.png)
[screenshots3](airport-api3.png)
[screenshots4](airport-api4.png)