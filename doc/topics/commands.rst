========
Commands
========
.. note::

    Each command have a *send_* and a *fetch_* variant, which allows to send a
    MPD command and then fetch the result later. See :ref:`getting-started` for
    examples and more information.

Querying 
---------


.. function:: MPDClient.clearerror()


    Clears the current error message in status (this is also
    accomplished by any command that starts playback).


.. function:: MPDClient.currentsong()


    Returns the song info of the current song (same song that is
    identified in status).


.. function:: MPDClient.idle([subsystems])


    (Introduced with MPD 0.14) Waits until there is a noteworthy
    change in one or more of MPD's subsystems. As soon as there is
    one, it lists all changed systems in a line in the format changed::
    SUBSYSTEM, where SUBSYSTEM is one of the following::

    While a client is waiting for idle results, the server disables
    timeouts, allowing a client to wait for events as long as mpd
    runs. The idle command can be canceled by sending the command
    noidle (no other commands are allowed). MPD will then leave idle
    mode and print results immediately; might be empty at this time.

    If the optional *SUBSYSTEMS* argument is used, MPD will only send
    notifications when something changed in one of the specified
    subsytems.


    * database: the song database has been modified after update.


    * update: a database update has started or finished. If the
      database was modified during the update, the database event is
      also emitted.


    * stored_playlist: a stored playlist has been modified, renamed,
      created or deleted


    * playlist: the current playlist has been modified


    * player: the player has been started, stopped or seeked


    * mixer: the volume has been changed


    * output: an audio output has been enabled or disabled


    * options: options like


    * partition: a partition was added, removed or changed


    * sticker: the sticker database has been modified.


    * subscription: a client has subscribed or unsubscribed to a
      channel


    * message: a message was received on a channel this client is
      subscribed to; this event is only emitted when the queue is
      empty


.. function:: MPDClient.status()


    Returns the current status of the player and the volume level.


    * *partition*: the name of the current partition


    * *volume*: 0-100


    * *repeat*: 0 or 1


    * *random*: 0 or 1


    * *single*: (Introduced with MPD 0.15) 0 or 1


    * *consume*: 0 or 1


    * *playlist*: 31-bit unsigned integer, the playlist version number


    * *playlistlength*: integer, the length of the playlist


    * *state*: play, stop, or pause


    * *song*: playlist song number of the current song stopped on or
      playing


    * *songid*: playlist songid of the current song stopped on or
      playing


    * *nextsong*: playlist song number of the next song to be played


    * *nextsongid*: playlist songid of the next song to be played


    * *time*: total time elapsed (of current playing/paused song)


    * *elapsed*: (Introduced with MPD 0.16) Total time elapsed within
      the current song, but with higher resolution.


    * *duration*: (Introduced with MPD 0.20) Duration of the current
      song in seconds.


    * *bitrate*: instantaneous bitrate in kbps


    * *xfade*: crossfade in seconds


    * *mixrampdb*: mixramp threshold in dB


    * *mixrampdelay*: mixrampdelay in seconds


    * *audio*: sampleRate:bits:channels


    * *updating_db*: job id


    * *error*: if there is an error, returns message here


.. function:: MPDClient.stats()


    Displays statistics.


    * *artists*: number of artists


    * *albums*: number of albums


    * *songs*: number of songs


    * *uptime*: daemon uptime in seconds


    * *db_playtime*: sum of all song times in the db


    * *db_update*: last db update in UNIX time


    * *playtime*: time length of music played


Playback options
----------------


.. function:: MPDClient.consume(state)


    Sets consume state to *STATE*, *STATE* should be 0 or 1. When
    consume is activated, each song played is removed from playlist.


.. function:: MPDClient.crossfade(seconds)


    Sets crossfading between songs.


.. function:: MPDClient.mixrampdb(decibels)


    Sets the threshold at which songs will be overlapped. Like
    crossfading but doesn't fade the track volume, just overlaps. The
    songs need to have MixRamp tags added by an external tool. 0dB is
    the normalized maximum volume so use negative values, I prefer
    -17dB. In the absence of mixramp tags crossfading will be used.
    See http://sourceforge.net/projects/mixramp


.. function:: MPDClient.mixrampdelay(seconds)


    Additional time subtracted from the overlap calculated by
    mixrampdb. A value of "nan" disables MixRamp overlapping and falls
    back to crossfading.


.. function:: MPDClient.random(state)


    Sets random state to *STATE*, *STATE* should be 0 or 1.


.. function:: MPDClient.repeat(state)


    Sets repeat state to *STATE*, *STATE* should be 0 or 1.


.. function:: MPDClient.setvol(vol)


    Sets volume to *VOL*, the range of volume is 0-100.

.. function:: MPDClient.volume(vol_change)

   Changes volume by amount *VOL_CHANGE*, the range is -100 to +100.
   A negative value decreases volume, positive value increases volume.


.. function:: MPDClient.single(state)


    Sets single state to *STATE*, *STATE* should be 0 or 1. When
    single is activated, playback is stopped after current song, or
    song is repeated if the 'repeat' mode is enabled.


.. function:: MPDClient.replay_gain_mode(mode)


    Sets the replay gain mode. One of *off*, *track*, *album*, *auto*
    (added in MPD 0.16) .

    Changing the mode during playback may take several seconds,
    because the new settings does not affect the buffered data.

    This command triggers the options idle event.


.. function:: MPDClient.replay_gain_status()


    Returns replay gain options. Currently, only the variable
    *replay_gain_mode* is returned.


Controlling playback
--------------------


.. function:: MPDClient.next()


    Plays next song in the playlist.


.. function:: MPDClient.pause(pause)


    Toggles pause/resumes playing, *PAUSE* is 0 or 1.


.. function:: MPDClient.play(songpos)


    Begins playing the playlist at song number *SONGPOS*.


.. function:: MPDClient.playid(songid)


    Begins playing the playlist at song *SONGID*.


.. function:: MPDClient.previous()


    Plays previous song in the playlist.


.. function:: MPDClient.seek(songpos, time)


    Seeks to the position *TIME* (in seconds; fractions allowed) of
    entry *SONGPOS* in the playlist.


.. function:: MPDClient.seekid(songid, time)


    Seeks to the position *TIME* (in seconds; fractions allowed) of
    song *SONGID*.


.. function:: MPDClient.seekcur(time)


    Seeks to the position *TIME* (in seconds; fractions allowed)
    within the current song. If prefixed by '+' or '-', then the time
    is relative to the current playing position.


.. function:: MPDClient.stop()


    Stops playing.


The current playlist
--------------------


.. function:: MPDClient.add(uri)


    Adds the file *URI* to the playlist (directories add recursively).
    *URI* can also be a single file.


.. function:: MPDClient.addid(uri, position)


    Adds a song to the playlist (non-recursive) and returns the song
    id.

    *URI* is always a single file or URL. For example::


        
        addid "foo.mp3"
        Id: 999
        OK
                    
.. function:: MPDClient.clear()


    Clears the current playlist.


.. function:: MPDClient.delete(index_or_range)


    Deletes a song, or a range of songs, from the playlist based on the song's
    position in the playlist.

    A range can be specified by passing a tuple.


.. function:: MPDClient.deleteid(songid)


    Deletes the song *SONGID* from the playlist


.. function:: MPDClient.move(to)


    Moves the song at *FROM* or range of songs at *START:END* to *TO*
    in the playlist. (Ranges are supported since MPD 0.15)


.. function:: MPDClient.moveid(from, to)


    Moves the song with *FROM* (songid) to *TO* (playlist index) in
    the playlist. If *TO* is negative, it is relative to the current
    song in the playlist (if there is one).


.. function:: MPDClient.playlist()


    Displays the current playlist.


.. function:: MPDClient.playlistfind(tag, needle)


    Finds songs in the current playlist with strict matching.


.. function:: MPDClient.playlistid(songid)


    Returns a list of songs in the playlist. *SONGID* is optional and
    specifies a single song to display info for.


.. function:: MPDClient.playlistinfo()


    Returns a list of all songs in the playlist, or if the optional
    argument is given, displays information only for the song
    *SONGPOS* or the range of songs *START:END*


.. function:: MPDClient.playlistsearch(tag, needle)


    Returns case-insensitive search results for partial matches in the 
    current playlist.


.. function:: MPDClient.plchanges(version, start:end)


    Returns changed songs currently in the playlist since *VERSION*.
    Start and end positions may be given to limit the output to
    changes in the given range.

    To detect songs that were deleted at the end of the playlist, use
    playlistlength returned by status command.


.. function:: MPDClient.plchangesposid(version, start:end)


    Returns changed songs currently in the playlist since *VERSION*.
    This function only returns the position and the id of the changed
    song, not the complete metadata. This is more bandwidth efficient.

    To detect songs that were deleted at the end of the playlist, use
    playlistlength returned by status command.


.. function:: MPDClient.prio(priority, start:end)


    Set the priority of the specified songs. A higher priority means
    that it will be played first when "random" mode is enabled.

    A priority is an integer between 0 and 255. The default priority
    of new songs is 0.


.. function:: MPDClient.prioid(priority, id)


    Same as prio, but address the songs with their id.


.. function:: MPDClient.rangeid(id, start:end)


    (Since MPD 0.19) Specifies the portion of the song that shall be
    played. *START* and *END* are offsets in seconds (fractional
    seconds allowed); both are optional. Omitting both (i.e. sending
    just ":") means "remove the range, play everything". A song that
    is currently playing cannot be manipulated this way.


.. function:: MPDClient.shuffle(start:end)


    Shuffles the current playlist. *START:END* is optional and
    specifies a range of songs.


.. function:: MPDClient.swap(song1, song2)


    Swaps the positions of *SONG1* and *SONG2*.


.. function:: MPDClient.swapid(song1, song2)


    Swaps the positions of *SONG1* and *SONG2* (both song ids).


.. function:: MPDClient.addtagid(songid, tag, value)


    Adds a tag to the specified song. Editing song tags is only
    possible for remote songs. This change is volatile: it may be
    overwritten by tags received from the server, and the data is gone
    when the song gets removed from the queue.


.. function:: MPDClient.cleartagid(songid[, tag])


    Removes tags from the specified song. If *TAG* is not specified,
    then all tag values will be removed. Editing song tags is only
    possible for remote songs.


Stored playlists
----------------
    Playlists are stored inside the configured playlist directory.
    They are addressed with their file name (without the directory and
    without the

    Some of the commands described in this section can be used to run
    playlist plugins instead of the hard-coded simple

.. function:: MPDClient.listplaylist(name)


    Returns a list of the songs in the playlist. Playlist plugins are supported.


.. function:: MPDClient.listplaylistinfo(name)


    Returns a list of the songs with metadata in the playlist. Playlist plugins
    are supported.


.. function:: MPDClient.listplaylists()


    Returns a list of the playlist in the playlist directory.

    After each playlist name the server sends its last modification
    time as attribute "Last-Modified" in ISO 8601 format. To avoid
    problems due to clock differences between clients and the server,
    clients should not compare this value with their local clock.


.. function:: MPDClient.load(name[, start:end])


    Loads the playlist into the current queue. Playlist plugins are
    supported. A range may be specified to load only a part of the
    playlist.


.. function:: MPDClient.playlistadd(name, uri)


    Adds *URI* to the playlist




.. function:: MPDClient.playlistclear(name)


    Clears the playlist


.. function:: MPDClient.playlistdelete(name, songpos)


    Deletes *SONGPOS* from the playlist


.. function:: MPDClient.playlistmove(name, from, to)


    Moves the song at position *FROM* in the playlist


.. function:: MPDClient.rename(name, new_name)


    Renames the playlist


.. function:: MPDClient.rm(name)


    Removes the playlist


.. function:: MPDClient.save(name)


    Saves the current playlist to


The music database
------------------

.. function:: MPDClient.albumart(uri)


    Returns the album art image for the given song.

    *URI* is always a single file or URL.

    The returned value is a dictionary containing the album art image in its
    ``'binary'`` entry. If the given URI is invalid, or the song does not have
    an album cover art file that MPD recognizes, a CommandError is thrown.
.. function:: MPDClient.count(tag, needle[, ..., "group", grouptype])


    Returns the counts of the number of songs and their total playtime in 
    the db matching *TAG* exactly.

    The *group* keyword may be used to group the results by a tag. The
    following prints per-artist counts::


        count group artist
.. function:: MPDClient.find(type, what[, ..., startend])


    Returns songs in the db that are exactly *WHAT*. *TYPE* can be any
    tag supported by MPD, or one of the special parameters::

    *WHAT* is what to find.

    *window* can be used to query only a portion of the real response.
    The parameter is two zero-based record numbers; a start number and
    an end number.


    * *any* checks all tag values


    * *file* checks the full path (relative to the music directory)


    * *base* restricts the search to songs in the given directory
      (also relative to the music directory)


    * *modified-since* compares the file's time stamp with the given
      value (ISO 8601 or UNIX time stamp)


.. function:: MPDClient.findadd(type, what[, ...])


    Returns songs in the db that are exactly *WHAT* and adds them to
    current playlist. Parameters have the same meaning as for find.


.. function:: MPDClient.list(type[, filtertype, filterwhat, ..., "group", grouptype, ...])


    Returns a list of unique tag values of the specified type. 
    *TYPE* can be any tag supported by MPD or *file*.

    Additional arguments may specify a filter like the one in the find
    command.

    The *group* keyword may be used (repeatedly) to group the results
    by one or more tags. The following example lists all album names,
    grouped by their respective (album) artist::


        list album group albumartist
.. function:: MPDClient.listall(uri)


    Returns a lists of all songs and directories in *URI*.

    Do not use this command. Do not manage a client-side copy of MPD's
    database. That is fragile and adds huge overhead. It will break
    with large databases. Instead, query MPD whenever you need
    something.


.. function:: MPDClient.listallinfo(uri)

    Returns a lists of all songs and directories with their metadata 
    info in *URI*.

    Same as listall, except it also returns metadata info in the same
    format as lsinfo.

    Do not use this command. Do not manage a client-side copy of MPD's
    database. That is fragile and adds huge overhead. It will break
    with large databases. Instead, query MPD whenever you need
    something.


.. function:: MPDClient.listfiles(uri)


    Returns a list of the contents of the directory *URI*, including files 
    are not recognized by MPD. *URI* can be a path relative to the music
    directory or an URI understood by one of the storage plugins. The
    response contains at least one line for each directory entry with
    the prefix "file: " or "directory: ", and may be followed by file
    attributes such as "Last-Modified" and "size".

    For example, "smb://SERVER" returns a list of all shares on the
    given SMB/CIFS server; "nfs://servername/path" obtains a directory
    listing from the NFS server.


.. function:: MPDClient.lsinfo(uri)


    Returns a list of the contents of the directory *URI*.

    When listing the root directory, this currently returns the list
    of stored playlists. This behavior is deprecated; use
    "listplaylists" instead.

    This command may be used to list metadata of remote files (e.g.
    URI beginning with "http://" or "smb://").

    Clients that are connected via UNIX domain socket may use this
    command to read the tags of an arbitrary local file (URI is an
    absolute path).


.. function:: MPDClient.readcomments(uri)


    Returns "comments" (i.e. key-value pairs) from the file specified by
    "URI". This "URI" can be a path relative to the music directory or
    an absolute path.

    This command may be used to list metadata of remote files (e.g.
    URI beginning with "http://" or "smb://").

    The response consists of lines in the form "KEY: VALUE". Comments
    with suspicious characters (e.g. newlines) are ignored silently.

    The meaning of these depends on the codec, and not all decoder
    plugins support it. For example, on Ogg files, this lists the
    Vorbis comments.


.. function:: MPDClient.readpicture(uri)


    Returns the embedded cover image for the given song.

    *URI* is always a single file or URL.

    The returned value is a dictionary containing the embedded cover image in its
    ``'binary'`` entry, and potentially the picture's MIME type in its ``'type'`` entry.
    If the given URI is invalid, a CommandError is thrown. If the given song URI exists,
    but the song does not have an embedded cover image that MPD recognizes, an empty
    dictionary is returned.


.. function:: MPDClient.search(type, what[, ..., startend])


    Returns results of a search for any song that contains *WHAT*. 
    Parameters have the same meaning as for find, except that search 
    is not case sensitive.


.. function:: MPDClient.searchadd(type, what[, ...])

    
    Searches for any song that contains *WHAT* in tag *TYPE* and adds
    them to current playlist.

    Parameters have the same meaning as for find, except that search
    is not case sensitive.


.. function:: MPDClient.searchaddpl(name, type, what[, ...])


    Searches for any song that contains *WHAT* in tag *TYPE* and adds
    them to the playlist named *NAME*.

    If a playlist by that name doesn't exist it is created.

    Parameters have the same meaning as for find, except that search
    is not case sensitive.


.. function:: MPDClient.update([uri])


    Updates the music database: find new files, remove deleted files,
    update modified files.

    *URI* is a particular directory or song/file to update. If you do
    not specify it, everything is updated.

    Prints "updating_db: JOBID" where *JOBID* is a positive number
    identifying the update job. You can read the current job id in the
    status response.


.. function:: MPDClient.rescan([uri])


    Same as update, but also rescans unmodified files.


Mounts and neighbors
--------------------
    A "storage" provides access to files in a directory tree. The most
    basic storage plugin is the "local" storage plugin which accesses
    the local file system, and there are plugins to access NFS and SMB
    servers.

    Multiple storages can be "mounted" together, similar to the mount
    command on many operating systems, but without cooperation from
    the kernel. No superuser privileges are necessary, beause this
    mapping exists only inside the MPD process

.. function:: MPDClient.mount(path, uri)


    Mount the specified remote storage URI at the given path. Example::


        mount foo nfs://192.168.1.4/export/mp3
.. function:: MPDClient.unmount(path)


    Unmounts the specified path. Example::


        unmount foo
.. function:: MPDClient.listmounts()


    Returns a list of all mounts. By default, this contains just the
    configured *music_directory*. Example::


        listmounts
        mount: 
        storage: /home/foo/music
        mount: foo
        storage: nfs://192.168.1.4/export/mp3
        OK
        
.. function:: MPDClient.listneighbors()


    Returns a list of "neighbors" (e.g. accessible file servers on the
    local net). Items on that list may be used with the mount command.
    Example::


        listneighbors
        neighbor: smb://FOO
        name: FOO (Samba 4.1.11-Debian)
        OK
        
Stickers
--------
    "Stickers" are pieces of information attached to existing MPD
    objects (e.g. song files, directories, albums). Clients can create
    arbitrary name/value pairs. MPD itself does not assume any special
    meaning in them.

    The goal is to allow clients to share additional (possibly
    dynamic) information about songs, which is neither stored on the
    client (not available to other clients), nor stored in the song
    files (MPD has no write access).

    Client developers should create a standard for common sticker
    names, to ensure interoperability.

    Objects which may have stickers are addressed by their object type
    ("song" for song objects) and their URI (the path within the
    database for songs).

.. function:: MPDClient.sticker_get(type, uri, name)


    Reads and returns a sticker value for the specified object.


.. function:: MPDClient.sticker_set(type, uri, name, value)


    Adds a sticker value to the specified object. If a sticker item
    with that name already exists, it is replaced.


.. function:: MPDClient.sticker_delete(type, uri[, name])


    Deletes a sticker value from the specified object. If you do not
    specify a sticker name, all sticker values are deleted.


.. function:: MPDClient.sticker_list(type, uri)


    Lists the stickers for the specified object.


.. function:: MPDClient.sticker_find(type, uri, name)


    Searches the sticker database for stickers with the specified
    name, below the specified directory (URI). For each matching song,
    it prints the URI and that one sticker's value.


.. function:: MPDClient.sticker_find(type, uri, name, "=", value)


    Returns the results of a search for stickers with the given value.

    Other supported operators are: "<", ">"


Connection settings
-------------------


.. function:: MPDClient.close()


    Closes the connection to MPD. MPD will try to send the remaining
    output buffer before it actually closes the connection, but that
    cannot be guaranteed. This command will not generate a response.


.. function:: MPDClient.kill()


    Kills MPD.


.. function:: MPDClient.password(password)


    This is used for authentication with the server. *PASSWORD* is
    simply the plaintext password.


.. function:: MPDClient.ping()


    Does nothing but return "OK".


Partition commands
------------------

    These commands allow a client to inspect and manage
    "partitions".  A partition is one frontend of a multi-player
    MPD process: it has separate queue, player and outputs.  A
    client is assigned to one partition at a time.


.. function:: MPDClient.partition(name)
    Switch the client to a different partition.


.. function:: MPDClient.listpartitions()
    Return a list of partitions.


.. function:: MPDClient.newpartition(name)
    Create a new partition.


.. function:: MPDClient.delpartition(name)
    Delete a partition.  The partition must be empty (no connected
    clients and no outputs).


.. function:: MPDClient.moveoutput(output_name)
    Move an output to the current partition.


Audio output devices
--------------------


.. function:: MPDClient.disableoutput(id)


    Turns an output off.


.. function:: MPDClient.enableoutput(id)


    Turns an output on.


.. function:: MPDClient.toggleoutput(id)


    Turns an output on or off, depending on the current state.


.. function:: MPDClient.outputs()


    Returns information about all outputs::


        
        outputid: 0
        outputname: My ALSA Device
        outputenabled: 0
        OK
                    
    * *outputid*: ID of the output. May change between executions


    * *outputname*: Name of the output. It can be any.


    * *outputenabled*: Status of the output. 0 if disabled, 1 if
      enabled.


Reflection
----------


.. function:: MPDClient.config()


    Returns a dump of all configuration values that may be interesting 
    for the client. This command is only permitted to "local" clients 
    (connected via UNIX domain socket).

    The following response attributes are available::


.. function:: MPDClient.commands()


    Returns which commands the current user has access to.


.. function:: MPDClient.notcommands()


    Returns which commands the current user does not have access to.


.. function:: MPDClient.tagtypes()


    Returns a list of available song metadata.


.. function:: MPDClient.urlhandlers()


    Returns a list of available URL handlers.


.. function:: MPDClient.decoders()


    Returns a list of decoder plugins, followed by their supported
    suffixes and MIME types. Example response::


        plugin: mad
        suffix: mp3
        suffix: mp2
        mime_type: audio/mpeg
        plugin: mpcdec
        suffix: mpc
Client to client
----------------
    Clients can communicate with each others over "channels". A
    channel is created by a client subscribing to it. More than one
    client can be subscribed to a channel at a time; all of them will
    receive the messages which get sent to it.

    Each time a client subscribes or unsubscribes, the global idle
    event *subscription* is generated. In conjunction with the
    channels command, this may be used to auto-detect clients
    providing additional services.

    New messages are indicated by the *message* idle event.

.. function:: MPDClient.subscribe(name)


    Subscribe to a channel. The channel is created if it does not
    exist already. The name may consist of alphanumeric ASCII
    characters plus underscore, dash, dot and colon.


.. function:: MPDClient.unsubscribe(name)


    Unsubscribe from a channel.


.. function:: MPDClient.channels()


    Obtains and returns a list of all channels. The response is a list of
    "channel:" lines.


.. function:: MPDClient.readmessages()


    Reads messages for this client. The response is a list of
    "channel:" and "message:" lines.


.. function:: MPDClient.sendmessage(channel, text)


    Send a message to the specified channel.


