import random
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from .config import SPOTIFY_API_KEY, PEXELS_API_KEY


class RandomData(APIView):
    renderer_classes = [JSONRenderer]  

    def get(self, request):
        # Initialize empty response data
        response_data = {}

        # Call Spotify API to get a random song
        try:
            spotify_response = self.get_random_spotify_song()
            response_data['spotify_song'] = spotify_response.data
        except Exception as e:
            response_data['spotify_error'] = str(e)

        # Call Pexels API to get a random photo
        try:
            pexels_response = self.get_random_photo()
            response_data['photo'] = pexels_response.data
        except Exception as e:
            response_data['photo_error'] = str(e)

        # Call local guitars API to get a random guitar
        try:
            guitar_response = self.get_random_guitar()
            response_data['guitar'] = guitar_response.data
        except Exception as e:
            response_data['guitar_error'] = str(e)

        # Return the combined response
        return Response(response_data)

    def get_random_spotify_song(self):
        headers = {
            'Authorization': f'Bearer {SPOTIFY_API_KEY}',
        }
        categories_response = requests.get('https://api.spotify.com/v1/browse/categories', headers=headers)
        categories_data = categories_response.json()
        random_category = random.choice(categories_data['categories']['items'])
        category_id = random_category['id']
        playlists_response = requests.get(f'https://api.spotify.com/v1/browse/categories/{category_id}/playlists', headers=headers)
        playlists_data = playlists_response.json()
        random_playlist = random.choice(playlists_data['playlists']['items'])
        playlist_id = random_playlist['id']
        tracks_response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers)
        tracks_data = tracks_response.json()
        random_track = random.choice(tracks_data['items'])
        track_name = random_track['track']['name']
        track_artists = ', '.join(artist['name'] for artist in random_track['track']['artists'])
        response_data = {
            'track_name': track_name,
            'artists': track_artists
        }
        return Response(response_data)

    def get_random_photo(self):
        headers = {'Authorization': PEXELS_API_KEY}
        response = requests.get('https://api.pexels.com/v1/curated', headers=headers)
        if response.status_code == 200:
            photos = response.json()['photos']
            random_photo = random.choice(photos)
            photo_url = random_photo['src']['original']
            response_data = {
                'photo_url': photo_url
            }
            return Response(response_data)
        else:
            return Response({'error': f'Failed to fetch photos. Pexels API returned status code {response.status_code}: {response.text}'}, status=response.status_code)

    def get_random_guitar(self):
        try:
            response = requests.get('http://localhost:8080/guitars')
            if response.status_code == 200:
                guitars = response.json()['data']
                random_guitar = random.choice(guitars)
                return Response(random_guitar)
            else:
                return Response({'error': f'Failed to fetch guitars. Local API returned status code {response.status_code}: {response.text}'}, status=response.status_code)
        except Exception as e:
            return Response({'error': f'An error occurred while fetching random guitar: {str(e)}'}, status=500)

