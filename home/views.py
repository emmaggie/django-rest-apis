from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from social.apps.django_app.default.models import UserSocialAuth
import twitter

def login(request):
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
def home(request):
    
    status = request.REQUEST.get("status", None)
    
    api = get_twitter(request.user)
    if status:
        api.PostUpdates(status)
    
    statuses = api.GetUserTimeline(screen_name=request.user.username, count=10)
    
    context = {"request": request, 'statuses': statuses}
    return render_to_response('home.html', context, context_instance=RequestContext(request))

from django.contrib.auth import logout as auth_logout
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')

def get_twitter(user):

    access_token_key=settings.TWITTER_ACCESS_TOKEN
    access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET

    usa = UserSocialAuth.objects.get(user=user, provider='twitter')
    if usa:
        access_token = usa.extra_data['access_token']
        if access_token:
            access_token_key = access_token['oauth_token']
            access_token_secret = access_token['oauth_token_secret']

    if not access_token_key or not access_token_secret:
        raise Exception('No user for twitter API call')

    api = twitter.Api(
        # base_url='https://api.twitter.com/1.1?include_cards=1&include_entities=1',
        base_url='https://api.twitter.com/1.1',
        consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
        consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
        access_token_key=access_token_key,
        access_token_secret=access_token_secret)

    return api