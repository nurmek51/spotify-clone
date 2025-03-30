from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
import json
import os
import logging


# Create your views here.

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'error': 'Empty query'}, status=400)

    try:
        results = {'artists': [], 'tracks': []}

        # Search for artists
        artist_response = requests.get(f"https://api.deezer.com/search/artist?q={query}&limit=5")
        if artist_response.status_code == 200:
            artist_data = artist_response.json()
            if 'data' in artist_data:
                for artist in artist_data['data']:
                    results['artists'].append({
                        'name': artist['name'],
                        'id': artist['id'],
                        'cover': artist.get('picture_medium', '')
                    })

        # Search for tracks
        track_response = requests.get(f"https://api.deezer.com/search/track?q={query}&limit=10")
        if track_response.status_code == 200:
            track_data = track_response.json()
            if 'data' in track_data:
                for track in track_data['data']:
                    results['tracks'].append({
                        'title': track['title'],
                        'artist': track['artist']['name'],
                        'artist_id': track['artist']['id'],
                        'track_id': track['id'],
                        'cover': track.get('album', {}).get('cover_medium', ''),
                        'preview_url': track.get('preview', '')
                    })

        return JsonResponse(results)

    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def get_charts(request):
    try:
        # Get top tracks from Deezer chart
        response = requests.get("https://api.deezer.com/chart/0/tracks?limit=30")
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch charts'}, status=500)

        data = response.json()
        chart_list = []

        if 'data' in data:
            for track in data['data']:
                track_data = {
                    'title': track['title'],
                    'artist': track['artist']['name'],
                    'artist_id': track['artist']['id'],
                    'cover': track['album']['cover_medium'],
                    'track_id': track['id'],
                    'preview_url': track.get('preview', '')
                }
                chart_list.append(track_data)

        return JsonResponse(chart_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def play_track(request, track_id):
    try:
        # Get track details from Deezer
        response = requests.get(f"https://api.deezer.com/track/{track_id}")
        if response.status_code != 200:
            return JsonResponse({'status': 'error', 'message': 'Failed to fetch track'}, status=500)

        track = response.json()

        track_info = {
            'title': track['title'],
            'artist': track['artist']['name'],
            'artist_id': track['artist']['id'],
            'cover': track['album']['cover_big'],
            'preview_url': track.get('preview', None)
        }

        return JsonResponse({'status': 'success', 'track_info': track_info})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def music_page(request):
    return render(request, 'music.html')


def artist_profile(request, artist_id):
    try:
        # Get artist data
        artist_response = requests.get(f"https://api.deezer.com/artist/{artist_id}")
        if artist_response.status_code != 200:
            return HttpResponse(status=500, content="Failed to fetch artist")

        artist_data = artist_response.json()

        # Get artist's top tracks
        top_tracks_response = requests.get(f"https://api.deezer.com/artist/{artist_id}/top?limit=10")
        tracks = []

        if top_tracks_response.status_code == 200:
            top_tracks_data = top_tracks_response.json()
            if 'data' in top_tracks_data:
                for track in top_tracks_data['data']:
                    track_info = {
                        'title': track['title'],
                        'track_id': track['id'],
                        'artist': artist_data['name'],
                        'artist_id': artist_id,
                        'cover': track['album']['cover_medium'],
                        'preview_url': track.get('preview', None)
                    }
                    tracks.append(track_info)

        # Get artist's albums
        albums_response = requests.get(f"https://api.deezer.com/artist/{artist_id}/albums?limit=20")
        albums = []

        if albums_response.status_code == 200:
            albums_data = albums_response.json()
            if 'data' in albums_data:
                for album in albums_data['data']:
                    albums.append({
                        'title': album['title'],
                        'year': album.get('release_date', '').split('-')[0] if album.get('release_date') else 'N/A'
                    })

        artist_info = {
            'artist_name': artist_data['name'],
            'artist_image': artist_data.get('picture_xl', ''),
            # Deezer doesn't provide artist description, so we'll use a default message
            'artist_description': 'No description available for this artist.',
            'tracks': tracks,
            'albums': albums,
        }

        return render(request, 'artist_profile.html', {'artist_info': artist_info})
    except Exception as e:
        logging.error(f"Artist profile error: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Credentials invalid")
            return redirect('login')

    return render(request, 'login.html')


def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Password not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')