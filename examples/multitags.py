#Multi tag files
#
#Some tag formats (such as ID3v2 and VorbisComment) support defining the same tag multiple times, mostly for when a song has multiple artists. MPD supports this, and sends each occurrence of a tag to the client.
#
#When python-mpd encounters the same tag more than once on the same song, it uses a list instead of a string.
#Function to get a string only song object.


def collapse_tags(song):
   for tag, value in song.iteritems():
       if isinstance(value, list):
           song[tag] = ", ".join(set(value))


