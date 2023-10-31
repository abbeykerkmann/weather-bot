# Abbey's Weather Bot (WIP)

## Overview
This project was created for me to experiment with creating my own weather bot for Discord.
The bot was created using Python and leverages the meteostat APIs to get weather data

## How it works
The weather can be queried for a variety of different stations with the option of getting the average weather for the day (`/today {station}`), or the weather for the current hour (`/now {station}`).
You can find available weather stations using the `/station {location}`. This command will search the list of stations for a match to the provided location. A valid weather station is required to get the current weather data from meteostat.

### Currently Supported Commands
```
/today {station}
/now {station}
/station {location}
```