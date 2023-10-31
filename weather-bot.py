import requests
from datetime import date, datetime, timedelta
import discord
from discord.ext import commands
from meteostat import Stations
from pandas import DataFrame

url = "https://meteostat.p.rapidapi.com/stations/"
timezone = "America/Toronto"
conditions = {1: 'Clear', 2: 'Fair', 3: 'Cloudy', 4: 'Overcast', 5: 'Fog', 6: 'Freezing Fog', 7: 'Light Rain',
              8: 'Rain', 9: 'Heavy Rain', 10: 'Freezing Rain', 11: 'Heavy Freezing Rain', 12: 'Sleet', 13: 'Heavy Sleet',
              14: 'Light Snowfall', 15: 'Snowfall', 16: 'Heavy Snowfall', 17: 'Rain Shower', 18: 'Heavy Rain Shower',
              19: 'Sleet Shower', 20: 'Heavy Sleet Shower', 21: 'Snow Shower', 22: 'Heavy Snow Shower', 23: 'Lightning',
              24: 'Hail', 25: 'Thunderstorm', 26: 'Heavy Thunderstorm', 27: 'Storm'}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

@bot.command(name='today')
async def getTodaysWeather(ctx, location):
    currentDate = date.today().strftime('%Y-%m-%d')
    stationId = getStationId(' '.join(location))
    weather = getDailyWeatherDataForDates(currentDate, currentDate, stationId)
    weatherData = weather['data'][0]
    message = "Weather for Today's Date ({}):\n".format(weatherData['date'])
    message += "Average Temperature: {}°C\n".format(weatherData['tavg'])
    message += "Lowest Temperature: {}°C\n".format(weatherData['tmin'])
    message += "Highest Temperature: {}°C\n".format(weatherData['tmax'])
    message += "Rain: {}mm\n".format(0 if weatherData['prcp'] == None else weatherData['prcp'])
    message += "Snowfall: {}mm\n".format(0 if weatherData['snow'] == None else weatherData['snow'])
    message += "Sunshine Total: {} minutes".format(0 if weatherData['tsun'] == None else weatherData['tsun'])
    await ctx.send(message)

@bot.command(name='now')
async def getCurrentWeather(ctx, *location):
    currentDate = date.today().strftime('%Y-%m-%d')
    currentHour = datetime.now().strftime('%Y-%m-%d %H:00:00')
    stationId = getStationId(' '.join(location))
    weather = getHourlyWeatherDataForDate(currentDate, stationId)
    weatherData = weather['data']
    currentWeatherData = None
    for index in range(len(weatherData)):
        if weatherData[index]['time'] == currentHour:
            currentWeatherData = weatherData[index]
            break
    message = "Current Weather for Today's Date ({}):\n".format(currentWeatherData['time'])
    message += "Condition: {}\n".format(getConditionString(currentWeatherData['coco']))
    message += "Temperature: {}°C\n".format(currentWeatherData['temp'])
    message += "Relative Humidity: {}%\n".format(currentWeatherData['rhum'])
    message += "Rain: {}mm\n".format(0 if currentWeatherData['prcp'] == None else currentWeatherData['prcp'])
    message += "Snowfall: {}mm\n".format(0 if currentWeatherData['snow'] == None else currentWeatherData['snow'])
    message += "Sunshine Total: {} minutes".format(0 if currentWeatherData['tsun'] == None else currentWeatherData['tsun'])
    await ctx.send(message)

@bot.command(name='station')
async def searchStation(ctx, *stationQuery):
    stations = Stations().fetch()
    stationQuery = ' '.join(stationQuery)
    station = stations.loc[stations['name'].str.lower().contains(stationQuery.lower())]
    message = "Found {} available stations:\n".format(len(station.index))
    stationString = station.loc[:, ['name', 'country', 'region']].to_string()
    message += "```{}```".format(stationString)
    await ctx.send(message)

# @bot.command(name='week')
# async def getWeekWeather(ctx):
#     currentDate = date.today().strftime('%Y-%m-%d')
#     endDate = currentDate + timedelta(days=7)
#     getWeatherDataForDate

def getDailyWeatherDataForDates(startDate, endDate, stationId):
    querystring = {"station": stationId, "start": startDate, "end": endDate, "tz": timezone}
    headers = {
        "X-RapidAPI-Key": "794afc0b6bmsh3de9edcbf8ef6eap153973jsndc7883566d76",
        "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
    }
    response = requests.get(url + "daily", headers=headers, params=querystring)
    return response.json()

def getHourlyWeatherDataForDate(date, stationId):
    querystring = {"station": stationId, "start": date, "end": date, "tz": timezone}
    headers = {
        "X-RapidAPI-Key": "794afc0b6bmsh3de9edcbf8ef6eap153973jsndc7883566d76",
        "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
    }
    response = requests.get(url + "hourly", headers=headers, params=querystring)
    return response.json()

def getConditionString(condition):
    return conditions[condition]

def getStationId(location):
    stations = Stations().fetch()
    print(stations)
    station = stations.loc[stations['name'] == location]
    if len(station.index) > 1:
        station = station.iloc[0]
    print(station['wmo'])
    return station['wmo']

bot.run("TOKEN")

