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
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

@bot.command(name='today')
async def getTodaysWeather(ctx, *station):
    currentDate = date.today().strftime('%Y-%m-%d')

    stationId = ""
    try:
        stationId = getStationId(' '.join(station))
    except:
        await ctx.send("Please provide a valid station name: `/now {station}`.\nStation names can be searched using the `/station {location}` command.")
        return
    
    weather = getDailyWeatherDataForDates(currentDate, currentDate, stationId)
    weatherData = weather['data'][0]

    message = "Today's Weather for {} ({}):\n".format(' '.join(station), weatherData['date'])
    weatherDetails = "Average Temperature: {}°C\n".format(weatherData['tavg'])
    weatherDetails += "Lowest Temperature: {}°C\n".format(weatherData['tmin'])
    weatherDetails += "Highest Temperature: {}°C\n".format(weatherData['tmax'])
    weatherDetails += "Rain: {}mm\n".format(0 if weatherData['prcp'] == None else weatherData['prcp'])
    weatherDetails += "Snowfall: {}mm\n".format(0 if weatherData['snow'] == None else weatherData['snow'])
    weatherDetails += "Sunshine Total: {} minutes".format(0 if weatherData['tsun'] == None else weatherData['tsun'])
    message += "```{}```".format(weatherDetails)

    await ctx.send(message)

@bot.command(name='now')
async def getCurrentWeather(ctx, *station):
    currentDate = date.today().strftime('%Y-%m-%d')
    currentHour = datetime.now().strftime('%Y-%m-%d %H:00:00')

    stationId = ""
    try:
        stationId = getStationId(' '.join(station))
    except AssertionError:
        await ctx.send("Please provide a valid station name: `/now {station}`.\nStation names can be searched using the `/station {location}` command.")
        return
    
    weather = getHourlyWeatherDataForDate(currentDate, stationId)
    weatherData = weather['data']
    currentWeatherData = None
    for index in range(len(weatherData)):
        if weatherData[index]['time'] == currentHour:
            currentWeatherData = weatherData[index]
            break
    
    message = "Current Weather for {} ({}):\n".format(' '.join(station), currentWeatherData['time'])
    weatherDetails = "Condition: {}\n".format(getConditionString(currentWeatherData['coco']))
    weatherDetails += "Temperature: {}°C\n".format(currentWeatherData['temp'])
    weatherDetails += "Relative Humidity: {}%\n".format(currentWeatherData['rhum'])
    weatherDetails += "Rain: {}mm\n".format(0 if currentWeatherData['prcp'] == None else currentWeatherData['prcp'])
    weatherDetails += "Snowfall: {}mm\n".format(0 if currentWeatherData['snow'] == None else currentWeatherData['snow'])
    weatherDetails += "Sunshine Total: {} minutes".format(0 if currentWeatherData['tsun'] == None else currentWeatherData['tsun'])
    message += "```{}```".format(weatherDetails)

    await ctx.send(message)

@bot.command(name='hourly')
async def getCurrentWeather(ctx, *station):
    currentDate = datetime.now()
    hoursList = [(currentDate + timedelta(hours=x)).strftime('%Y-%m-%d %H:00:00') for x in range(5)]

    stationId = ""
    try:
        stationId = getStationId(' '.join(station))
    except AssertionError:
        await ctx.send("Please provide a valid station name: `/now {station}`.\nStation names can be searched using the `/station {location}` command.")
        return
    
    weather = getHourlyWeatherDataForDate(currentDate.strftime('%Y-%m-%d'), stationId)
    weatherData = weather['data']
    hourlyWeatherData = []
    for index in range(len(weatherData)):
        if weatherData[index]['time'] in hoursList:
            hourlyWeatherData.append(weatherData[index])
    
    message = "Hourly Weather for {} ({}):\n".format(' '.join(station), currentDate.strftime('%Y-%m-%d'))
    for hour in hourlyWeatherData:
        message += "Hour: {}\n".format(hour['time'][hour['time'].index(' ') + 1:])
        weatherDetails = "Condition: {}\n".format(getConditionString(hour['coco']))
        weatherDetails += "Temperature: {}°C\n".format(hour['temp'])
        weatherDetails += "Relative Humidity: {}%\n".format(hour['rhum'])
        weatherDetails += "Rain: {}mm\n".format(0 if hour['prcp'] == None else hour['prcp'])
        weatherDetails += "Snowfall: {}mm\n".format(0 if hour['snow'] == None else hour['snow'])
        weatherDetails += "Sunshine Total: {} minutes".format(0 if hour['tsun'] == None else hour['tsun'])
        message += "```{}```".format(weatherDetails)

    await ctx.send(message)

@bot.command(name='station')
async def searchStation(ctx, *stationQuery):
    stations = Stations().fetch()
    stationQuery = ' '.join(stationQuery)

    selectedStations = stations[stations['name'].str.contains(stationQuery)]

    message = "Found {} available stations:\n".format(len(selectedStations.index))
    stationString = selectedStations.loc[:, ['name', 'country', 'region', 'timezone']].to_string()
    message += "```{}```".format(stationString)

    await ctx.send(message)

# WIP: Weather for the upcoming week
# @bot.command(name='week')
# async def getWeekWeather(ctx, *location):
#     currentDate = date.today().strftime('%Y-%m-%d')
#     endDate = currentDate + timedelta(days=7)
#     stationId = ""
#     try:
#         stationId = getStationId(' '.join(location))
#     except:
#         await ctx.send("Please provide a valid station name: `/now {station}`.\nStation names can be searched using the `/station {location}` command.")
#         return
#     weather = getDailyWeatherDataForDates(currentDate, endDate, stationId)

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
    station = stations.loc[stations['name'] == location]
    if station.empty:
        raise AssertionError("Invalid station name provided")
    else:
        return station.index.tolist()[0]

bot.run("TOKEN")

