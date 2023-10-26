import grequests
import requests
import math
from datetime import datetime
from .objects.match import Match
from .objects.participant import Participant
from django.db import connection

# Set up environment variables to use
import environ
env = environ.Env()
environ.Env.read_env()

"""
	This file is to process all league-related API calls.
	For now, store the API key here.
"""
api_key = env('api_key')
summoner_id = [None, None, None]  # summonerName, encryptedSummonerId, puuid
area = [None, None]  # platform, region
version = None


# Update the API key via method instead of doing so directly
def update_api_key(api_key_input):
    api_key = api_key_input


# Update the platform, and also determine the region
def update_platform_and_region(platform):
    area[0] = platform
    area[1] = get_regional_value(platform)


# Given the platform, return the region
# Even though there is a "return None," this should never be returned, since the platform values are from a dropdown
def get_regional_value(platform):
    if platform in ['br1', 'na1', 'la1', 'la2']:
        return 'americas'
    elif platform in ['eun1', 'euw1', 'tr1', 'ru']:
        return 'europe'
    elif platform in ['oc1', 'ph2', 'sg2', 'th2', 'tw2', 'vn2']:
        return 'sea'
    elif platform in ['jp1', 'kr']:
        return 'asia'
    else:
        return None


# Get the summoner's encrypted id and puuid and store it within summoner_id.
def get_summoner_api(platform, name):
    summoner_id_url = 'https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner}?api_key={api}'.format(
        platform=platform, summoner=name, api=api_key)
    summoner_response_json = requests.get(summoner_id_url).json()
    if 'status' in summoner_response_json:
        print('There is a status code, indicating that there is an error.')
        if summoner_response_json['status']['status_code'] == 403:
            print(
                'Error, you must supply a valid, non-expired API key somewhere in this project.'
            )
            return summoner_response_json, False
        if summoner_response_json['status']['status_code'] == 404:
            print(
                'Error, {name} does not exist in the {platform} server'.format(
                    name=name, platform=platform))
            return summoner_response_json, False

    else:
        print('Nice, no error found here :)')
        summoner_id[0] = summoner_response_json['name']
        summoner_id[1] = summoner_response_json['id']
        summoner_id[2] = summoner_response_json['puuid']
        update_platform_and_region(platform)
        return summoner_response_json, True

"""
    Below API calls are dynamic, i.e. will always be called with a user input.
    Assuming that the get_summoner_api method returns a status of 200, the below API calls should almost always work.
    Make a master function to asynchronously call these methods.  

    The count argument is provided early on since one of the api calls has the count parameter (# of matches to view)

    The return value will be a list
        1. An array of strings of size 3.  [Rank, LP, wins and losses] or default ['Unranked', None, None]
        2. A default list of 10 champions of the summoner's most 'mastered' champions. [{championName, championMasteryLevel, championMasteryPoints, championImageUrl}]
        3. A list of recent matches played by the user
"""
def make_async_api_calls(count):
    if count <= 0:
        count = 10;
    result = [];
    api_urls = [
        'https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{eid}/?api_key={api}'.format(platform=area[0], eid=summoner_id[1], api=api_key),
        #'https://{platform}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{eid}/top?count=7&api_key={api}'.format(platform=area[0], eid=summoner_id[1], api=api_key),
        'https://{platform}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{eid}?api_key={api}'.format(platform=area[0], eid=summoner_id[1], api=api_key),
        'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api}'.format(region=area[1], puuid=summoner_id[2], count=count, api=api_key),
    ];
    responses = list(grequests.map((grequests.get(url) for url in api_urls), size=3))

    # The first 2 results of the api calls can be put into the result array
    result.append(get_summoner_solo_queue_rank(responses[0].json()));
    result.append(get_champion_top_mastery(responses[1].json()));

    # The third result of the asynchronous call will have to be put into an array, and then pass that array onto the method
    match_api_url = ['https://{region}.api.riotgames.com/lol/match/v5/matches/{match}?api_key={api}'.format(region=area[1], match=match, api=api_key) for match in responses[2].json()];   
    match_history_responses = list(grequests.map((grequests.get(match_url) for match_url in match_api_url)));
    match_history_responses = [match.json()['info'] for match in match_history_responses]
    result.append(get_summoner_match_history(match_history_responses));

    # Finally, return the result
    return result;


# Get the rank of the summoner and output it on the summonerDetail page
def get_summoner_solo_queue_rank(summoner_rank_json):
    result = ['Unranked', None, None]
    #summoner_rank_information = requests.get('https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{eid}/?api_key={api}'.format(platform=area[0], eid=summoner_id[1], api=api_key[0]))
    #summoner_rank_json = summoner_rank_information.json()
    for data in summoner_rank_json:
        if data['queueType'] == 'RANKED_SOLO_5x5':
            result[0] = '{rank} {number}'.format(rank=data['tier'],number=data['rank'])
            result[1] = '{lp} LP'.format(lp=data['leaguePoints'])
            result[2] = '{win} wins, {loss} losses'.format(win=data['wins'],loss=data['losses'])
            break
    return result


# Get the top 10 mastery champions for the summoner
def get_champion_top_mastery(summoner_champion_mastery_json):
    #summoner_champion_mastery_response = requests.get('https://{platform}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{eid}/top?count=10&api_key={api}'.format(platform=area[0], eid=summoner_id[1], api=api_key[0]))
    #summoner_champion_mastery_json = summoner_champion_mastery_response.json()
    #print(summoner_champion_mastery_json);
    championMasteryObject = []
    counter = 0
    for champion in summoner_champion_mastery_json:
        championMasteryObject.append({
            'championName': champion_to_id_information[champion['championId']],
            'championLevel': champion['championLevel'],
            'championPoints': champion['championPoints'],
            'image': champion_image_url_information[champion_to_id_information[champion['championId']]],
        })

        # Only take the top 7 champions
        counter += 1
        if counter == 7:
            break
    return championMasteryObject


# Get match history for the player (default is 10)
def get_summoner_match_history(match_history_responses):
    #if count <= 0:  # In case the count input is bad, set it to 1 by default
        #count = 1
    #summoner_match_history_information = requests.get('https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api}'.format(region=area[1], puuid=summoner_id[2], count=count, api=api_key[0]))
    #summoner_match_history_json = summoner_match_history_information.json()
    matchList = []
    for match_data in match_history_responses:
        #match_data = requests.get('https://{region}.api.riotgames.com/lol/match/v5/matches/{match}?api_key={api}'.format(region=area[1], match=match, api=api_key[0])).json()['info']
        #match_data = match.json()['info']

        # There is so much data...  Process the relevant ones
        # Also create a Match object here
        matchObject = Match()
        matchObject.set_gameCreationTime(match_data['gameCreation'])
        matchObject.add_minutes(math.trunc(match_data['gameDuration'] / 60))
        matchObject.add_seconds(round(match_data['gameDuration'] % 60, 0))
        matchObject.add_queueType(queues[match_data['queueId']])
        matchObject.add_platform(area[0]);
        matchObject.add_version(version);

        for data in match_data['participants']:
            participant = Participant()

            # Add a bunch of data to the participant object
            participant.set_assists(data['assists'])
            participant.set_championName(champion_to_id_information[data['championId']])
            participant.set_championImage(champion_image_url_information[participant.get_championName()])
            participant.set_deaths(data['deaths'])
            participant.set_kills(data['kills'])
            participant.set_minionsKilled(data['totalMinionsKilled'] + data['neutralMinionsKilled'])
            participant.set_summonerName(data['summonerName'])
            participant.set_teamPosition('' if data['teamPosition'] == '' 'SUPPORT' else ('SUPPORT' if data['teamPosition'] == 'UTILITY' else data['teamPosition']))
            participant.set_teamSide('Blue' if data['teamId'] == 100 else 'Red')
            participant.set_win('Yes' if data['win'] else 'No')
            participant.set_items([
                {
                    data['item0']: item_to_id_information[data['item0']]['name']
                }, 
                {
                    data['item1']: item_to_id_information[data['item1']]['name']
                }, 
                {
                    data['item2']: item_to_id_information[data['item2']]['name']
                }, 
                {
                    data['item3']: item_to_id_information[data['item3']]['name']
                }, 
                {
                    data['item4']: item_to_id_information[data['item4']]['name']
                }, 
                {
                    data['item5']: item_to_id_information[data['item5']]['name']
                }, 
                {
                    data['item6']: item_to_id_information[data['item6']]['name']
                }
            ])

            # If the participant is a bot, then it has no summoner id information; skip this specific section.
            if data['puuid'] != 'BOT':
                participant.set_summonerSpells([summoner_spell_information[data['summoner1Id']], summoner_spell_information[data['summoner2Id']]])
            
            matchObject.add_participant(participant)
            if data['puuid'] == summoner_id[2]:
                if data['championName'] != 'MonkeyKing':
                    matchObject.add_championImageUrl(champion_image_url_information[data['championName']])
                    matchObject.add_championName(data['championName'])
                else:
                    matchObject.add_championImageUrl(champion_image_url_information['Wukong'])
                    matchObject.add_championName('Wukong')
                matchObject.set_isWinner('Winner' if data['win'] else 'Loser');

        matchList.append(matchObject)
    return matchList

"""
    Below API calls are automatically called as soon as the home page is loaded, i.e. these are static.
    todo: add these to the database
"""
# Make an api call to get the current version of the game
version_response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
version = version_response.json()[0]
try:
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Version (version) VALUES (%s)', [version])
except Exception as e:
    print('Error, version is already in the database.  Overriding version...')
    with connection.cursor() as cursor:
        cursor.execute('UPDATE Version set version = %s', [version])
finally:
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM Version WHERE version = %s', [version])
        version_retrieval = cursor.fetchone()
        print('Latest version: {0}'.format(version_retrieval))

# Make an api call to get ALL champions and create a mapping (id : champion)
champion_data_response = requests.get('http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json'.format(version=version))
champion_data_json = champion_data_response.json()
champion_data_json['data']['MonkeyKing']['id'] = 'Wukong'
champion_to_id_information = {int(champion_data_json['data'][champion]['key']) : champion_data_json['data'][champion]['id'] for champion in champion_data_json['data']}
champion_to_id_information[-1] = 'N/A'
for champion_id in champion_to_id_information:
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Champion (id, name) VALUES (%s, %s)', [champion_id, champion_to_id_information[champion_id]])
    except Exception as e:
        pass
        #print('Error, champion data is already in the database.\nDetails:', e)

# Make a series of API calls to get the images of each champion
champion_image_url_information = {
    champion_to_id_information[champion]: 'http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion}.png'.format(version=version, champion=champion_to_id_information[champion]) 
    for champion in champion_to_id_information.keys() if champion != -1
}
champion_image_url_information['Wukong'] = 'http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/MonkeyKing.png'.format(version=version)

# Make an api call to get summoner spell information
summoner_spell_data_response = requests.get('http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json'.format(version=version))
summoner_spell_json = summoner_spell_data_response.json()['data']
summoner_spell_information = {
    int(summoner_spell_json[spell]['key']): summoner_spell_json[spell]['name']
    for spell in summoner_spell_json
}

# Make an API call to retrieve item information
item_data_response = requests.get('http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json'.format(version=version))
item_json = item_data_response.json()['data']
item_to_id_information = {
    int(data): {
        'name': item_json[data]['name'],
        'gold': item_json[data]['gold']['total']
    }
    for data in item_json
    if item_json[data]['maps']['11'] is True or item_json[data]['gold']['total'] > 0 or 'Trinket' in item_json[data]['tags']
}
item_to_id_information[0] = {'name': 'Empty', 'gold': 0}
item_to_id_information[-1] = {'name': 'Empty', 'gold': 0}

# Make an API call to store queue information
queue_types = requests.get('https://static.developer.riotgames.com/docs/lol/queues.json')
queue_types_json = queue_types.json()
queues = {queue['queueId']: queue['description'] for queue in queue_types_json}

# Make an API call to store map information
map_types = requests.get('https://static.developer.riotgames.com/docs/lol/maps.json')
map_types_json = map_types.json()
maps = {map['mapId']: map['mapName'] for map in map_types_json}
