from dataloader import extract_zip, load

# download tracks from Google Drive link above:
# week3tracks_tiny.zip       mp3 format, 92 MB
# week3tracks.zip           flac format, 1 GB

# extract zip archive (can do this from your file manager also)
extract_zip(zip_file="./week3tracks_tiny.zip", audio_directory = "./tracks")

# load track information as a list of dictionaries
tracks_info = load(audio_directory = "./tracks")

print(tracks_info[0])
#{
    #'youtube_url': 'https://www.youtube.com/watch?v=pWIx2mz0cDg',
    #'title': 'Plastic Beach (feat. Mick Jones and Paul Simonon)',
    #'artist': 'Gorillaz',
    #'artwork_url': 'https://i.scdn.co/image/ab67616d0000b273661d019f34569f79eae9e985',
    #'audio_path': 'tracks/audio/Gorillaz_PlasticBeachfeatMickJonesandPaulSimonon_pWIx2mz0cDg.mp3'
#}
