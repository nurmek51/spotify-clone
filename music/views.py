from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
import json
from yandex_music import Client
import yandex_music
import os
import logging

client = yandex_music.Client(os.getenv('TOKEN')).init()

# Create your views here.

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'error': 'Пустой запрос'}, status=400)

    try:
        search_result = client.search(text=query)
        results = {'artists': [], 'tracks': []}

        # Обработка артистов
        if search_result.artists and search_result.artists.results:
            for artist in search_result.artists.results[:5]:
                try:
                    cover_url = ''
                    if hasattr(artist, 'cover'):
                        cover_url = f"https://{artist.cover.uri.replace('%%', '200x200')}"

                    results['artists'].append({
                        'name': artist.name,
                        'id': artist.id,
                        'cover': cover_url
                    })
                except Exception as artist_error:
                    logging.error(f"Ошибка обработки артиста: {artist.name}. Ошибка: {str(artist_error)}")

        # Обработка треков
        if search_result.tracks and search_result.tracks.results:
            for track in search_result.tracks.results[:10]:
                try:
                    download_info_list = track.get_download_info()
                    preview_url = None
                    if download_info_list:
                        preview_url = download_info_list[0].get_direct_link()

                    cover_url = ''
                    if track.cover_uri:
                        cover_url = f"https://{track.cover_uri.replace('%%', '200x200')}"

                    results['tracks'].append({
                        'title': track.title,
                        'artist': track.artists[0].name if track.artists else 'Unknown',
                        'artist_id': track.artists[0].id if track.artists else None,
                        'track_id': track.id,
                        'cover': cover_url,
                        'preview_url': preview_url
                    })
                except Exception as track_error:
                    logging.error(f"Ошибка обработки трека: {track.title}. Ошибка: {str(track_error)}")

        return JsonResponse(results)

    except Exception as e:
        logging.error(f"Ошибка поиска: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
def get_charts(request):
    try:
        charts = client.chart().chart.tracks[:30]
        chart_list = []

        for track in charts:
            track_info = track.track
            track_data = {
                'title': track_info.title,
                'artist': track_info.artists[0].name if track_info.artists else "Unknown",
                'artist_id': track_info.artists[0].id if track_info.artists else None,
                'cover': f"https://{track_info.cover_uri.replace('%%', '300x300')}" if track_info.cover_uri else None,
                'track_id': track.id,
                'preview_url': track_info.get_download_info()[0].direct_link if track_info.get_download_info() else None
            }
            chart_list.append(track_data)

        return JsonResponse(chart_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def play_track(request, track_id):
    try:
        track = client.tracks(track_id)[0]

        track_info = {
            'title': track.title,
            'artist': track.artists[0].name,
            'artist_id': track.artists[0].id,
            'cover': f"https://{track.og_image.replace('%%', '300x300')}" if track.og_image else None,
            'preview_url': None
        }

        download_info_list = track.get_download_info()

        if download_info_list:
            for download_info in download_info_list:
                if download_info.codec == 'mp3':
                    track_info['preview_url'] = download_info.get_direct_link()
                    break

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
        artist_data = client.artists(artist_id)[0]
        description = artist_data.description.get('text',
                                                  'Описание недоступно.') if artist_data.description else 'Описание недоступно.'

        artist_albums = client.artists_direct_albums(artist_id).albums
        albums = [{'title': album.title, 'year': album.year} for album in artist_albums]

        artist_tracks = client.artists_tracks(artist_id).tracks
        tracks = []
        for track in artist_tracks:
            track_info = {
                'title': track.title,
                'track_id': track.id,
                'artist': artist_data.name,
                'artist_id': artist_id,
                'cover': f"https://{track.og_image.replace('%%', '300x300')}" if track.og_image else "https://via.placeholder.com/300",
                'preview_url': track.get_download_info()[0].direct_link if track.get_download_info() else None
            }
            tracks.append(track_info)

        artist_info = {
            'artist_name': artist_data.name,
            'artist_image': f"https://{artist_data.og_image.replace('%%', '300x300')}" if artist_data.og_image else "https://via.placeholder.com/300",
            'artist_description': description,
            'albums': albums,
            'tracks': tracks,
        }

        return render(request, 'artist_profile.html', {'artist_info': artist_info})

    except Exception as e:
        return HttpResponse(status=500, content={'error_message': str(e)})

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Credientals invalid ")
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