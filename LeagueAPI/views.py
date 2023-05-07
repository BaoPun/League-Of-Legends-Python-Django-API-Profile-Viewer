from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
from .models import Summoner
import LeagueAPI.api as api


# Create your views here.


# Home index page
def home_page(request):
    """
	template = loader.get_template('sample_index.html');
	return HttpResponse(template.render());
	"""
    #summoners = Summoner.objects.all().values()
    template = loader.get_template('main_index.html')
    """context = {
        'summoners': summoners,
    }"""

    return HttpResponse(template.render())


def summoner_redirect(request):
    dict = request.GET.dict()
    return redirect(
        reverse('summoner_profile', kwargs={'platform': dict['platform'], 'name': dict['summonerName']})
    )


# Get the region + username
def summoner_profile(request, platform, name):
    template = loader.get_template('summonerDetail.html')
    summoner_json, is_valid_json = api.get_summoner_api(platform, name)
    if not is_valid_json:
        if summoner_json['status']['status_code'] == 403:
            return redirect(summoner_forbidden_access)
        elif summoner_json['status']['status_code'] == 404:
            return redirect(summoner_not_found)
        else:
            return redirect(summoner_not_found)
    else:
        context = {
            'platform': platform,
            'name': summoner_json['name'],
            'level': summoner_json['summonerLevel'],
        }
        # Below method is just testing out the asynchronous calls from grequests.
        api_results = api.make_async_api_calls(10);

        rank_information = api_results[0];#api.get_summoner_solo_queue_rank()
        context['rank'] = rank_information[0]
        if rank_information[0] != 'Unranked':
            context['lp'] = rank_information[1]
            context['win_loss_data'] = rank_information[2]
        champion_mastery_info = api_results[1];#api.get_champion_top_mastery()
        context['championList'] = champion_mastery_info
        matchHistoryList = api_results[2];#api.get_summoner_match_history(10)
        context['matchList'] = matchHistoryList
        return HttpResponse(template.render(context, request))


# Direct to 403
def summoner_forbidden_access(request):
    template = loader.get_template('403.html')
    #print('Current api key: {api}'.format(api=api.api_key[0]))
    return HttpResponse(template.render())


# Direct to 404
def summoner_not_found(request):
    template = loader.get_template('404.html')
    return HttpResponse(template.render())


# After the 403 page when submitting the API key
def redirect_403(request):
    dict = request.GET.dict()
    # single value with key being 'apiKey'
    api.update_api_key(dict['apiKey'])
    return redirect('home_page')
