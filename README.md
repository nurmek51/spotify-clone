# Music Streaming Application

**Live Demo:** [nurmek.site](https://spotify.nurmek.site)

## Overview

This is a music streaming web application that allows users to discover and preview music tracks, browse artists, and explore popular songs. The application integrates with the Deezer API to provide a rich music catalog, including artist information, top tracks, albums, and music previews.

## Features

- **User Authentication**: Secure login and registration system
- **Music Discovery**: Browse top charts and trending music
- **Search Functionality**: Find your favorite artists and tracks
- **Artist Profiles**: View artist information, top tracks, and discography
- **Music Player**: Preview tracks directly in the browser

## Technology Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Deezer API for music data
- **Authentication**: Django's built-in authentication system
- **Deployment**: Hosted at nurmek.site

## Getting Started

### Prerequisites

- Python 3.6+
- Django 3.0+
- Requests library

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/music-streaming-app.git
cd music-streaming-app
```

2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages
```bash
pip install -r requirements.txt
```

4. Apply migrations
```bash
python manage.py migrate
```

5. Run the development server
```bash
python manage.py runserver
```

6. Open your browser and go to `http://localhost:8000`

## Project Structure

- **views.py**: Contains the core functionality for handling requests and API interactions
- **templates/**: HTML templates for rendering pages
  - **index.html**: Main homepage with top charts
  - **artist_profile.html**: Displays artist information, popular tracks, and albums
  - **music.html**: Music player page
  - **login.html** and **signup.html**: Authentication pages
- **static/**: CSS, JavaScript, and image files

## API Integration

The application leverages the Deezer API to fetch music data:
- Search functionality for artists and tracks
- Retrieving artist information, top tracks, and albums
- Accessing chart information for trending music
- Track previews for streaming

## Future Enhancements

- User playlists and favorites
- Enhanced music player with additional controls
- Social features (sharing, commenting)
- Music recommendations based on listening history
- Mobile application


## Acknowledgments

- [Deezer API](https://developers.deezer.com/api) for providing music data
- [Django Documentation](https://docs.djangoproject.com/) for the comprehensive guides
- All contributors who have helped improve this project
