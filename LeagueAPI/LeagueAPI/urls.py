from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),  # this is the default path, taken from LeagueApi\views
    path('resubmit_api_key/', views.redirect_403, name='redirect_403'),
	#
    path('403',views.summoner_forbidden_access,name='summoner_forbidden_access'),
    path('404', views.summoner_not_found, name='summoner_not_found'),
	#
    path('ICANT_KEKW/', views.summoner_redirect, name='summoner_redirect'),  # take in the region and summoner name here (use as redirect)
    path('platform/<platform>/summoner/<name>', views.summoner_profile, name='summoner_profile'),
]
