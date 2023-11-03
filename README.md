# Abbey's Weather Bot (WIP)

## Overview
This project was created for me to experiment with creating my own weather bot for Discord.
The bot was created using Python and leverages the meteostat APIs to get weather data

## How it works
The weather can be queried for a variety of different stations with the option of getting the average weather for the day (`/today {station}`), or the weather for the current hour (`/now {station}`).
You can find available weather stations using the `/station {location}`. This command will search the list of stations for a match to the provided location. A valid weather station is required to get the current weather data from meteostat.

### Commands

#### Supported Commands
Here is a list of the currently functioning commands:
```
/today {station}: gets the average weather for the current day at the given station
/now {station}: gets the current weather for the current day at the given station
/hourly {station}: gets the weather for the current hour and the next 4 hours
/station {location}: searches the available stations and provides matches for a given location
```

#### Future Commands
Here is a list of commands/functionalities I want to introduce down the line as I work on this project:
- Command to get the weather forecast for the next 7 days
- Option to specify how many hours to get for the hourly command
- Option to get weather by station ID for more specific results
- Images representing the current conditions for the now command
- Features for viewing historical weather data for a location