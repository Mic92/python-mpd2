========
Commands
========
.. note::

    Each command have a *send_* and a *fetch_* variant, which allows to send a
    MPD command and then fetch the result later. See :ref:`getting-started` for
    examples and more information.

Querying MPD's status
---------------------


.. function:: MPDClient.clearerror()

              Clears the current error message in status (this is also
              accomplished by any command that starts playback).


.. function:: MPDClient.currentsong()

              Displays the song info of the current song (same song that
              is identified in status).


.. function:: MPDClient.idle([subsystems])
 
              Waits until there is a noteworthy change in one or more
              of MPD's subsystems.  As soon as there is one, it lists
              all changed systems in a line in the format , where
              SUBSYSTEM is one of the following::

              While a client is waiting for idle 
              results, the server disables timeouts, allowing a client
              to wait for events as long as mpd runs.  The idle  command can be canceled by
              sending the command noidle  (no other
              commands are allowed). MPD will then leave idle  mode and print results
              immediately; might be empty at this time.

              If the optional SUBSYSTEMS  argument is used,
              MPD will only send notifications when something changed in
              one of the specified subsytems.


.. function:: MPDClient.status()

              Reports the current status of the player and the volume
              level.


.. function:: MPDClient.stats()

              Displays statistics.


Playback options
----------------


.. function:: MPDClient.consume(state)
 
              Sets consume state to STATE , STATE  should be 0 or 1.
	      When consume is activated, each song played is removed from playlist.


.. function:: MPDClient.crossfade(seconds)

              Sets crossfading between songs.


.. function:: MPDClient.mixrampdb(decibels)

              Sets the threshold at which songs will be overlapped. Like crossfading but doesn't fade the track volume, just overlaps. The songs need to have MixRamp tags added by an external tool. 0dB is the normalized maximum volume so use negative values, I prefer -17dB. In the absence of mixramp tags crossfading will be used. See http://sourceforge.net/projects/mixramp


.. function:: MPDClient.mixrampdelay(seconds)

              Additional time subtracted from the overlap calculated by mixrampdb. A value of "nan" disables MixRamp overlapping and falls back to crossfading.


.. function:: MPDClient.random(state)

              Sets random state to STATE , STATE  should be 0 or 1.


.. function:: MPDClient.repeat(state)

              Sets repeat state to STATE , STATE  should be 0 or 1.


.. function:: MPDClient.setvol(vol)

              Sets volume to VOL , the range of
              volume is 0-100.


.. function:: MPDClient.single(state)
 
              Sets single state to STATE , STATE  should be 0 or 1.
	      When single is activated, playback is stopped after current song, or
	      song is repeated if the 'repeat' mode is enabled.


.. function:: MPDClient.replay_gain_mode(mode)

              Sets the replay gain mode.  One of off , track , album , auto .

              Changing the mode during playback may take several
              seconds, because the new settings does not affect the
              buffered data.

              This command triggers the  idle event.


.. function:: MPDClient.replay_gain_status()

              Prints replay gain options.  Currently, only the
              variable replay_gain_mode  is
              returned.


.. function:: MPDClient.volume(change)

              Changes volume by amount CHANGE .


Controlling playback
--------------------


.. function:: MPDClient.next()

              Plays next song in the playlist.


.. function:: MPDClient.pause(pause)

              Toggles pause/resumes playing, PAUSE  is 0 or 1.


.. function:: MPDClient.play(songpos)

              Begins playing the playlist at song number SONGPOS .


.. function:: MPDClient.playid(songid)

              Begins playing the playlist at song SONGID .


.. function:: MPDClient.previous()

              Plays previous song in the playlist.


.. function:: MPDClient.seek(songpos, time)

              Seeks to the position TIME  (in
              seconds) of entry SONGPOS  in the
              playlist.


.. function:: MPDClient.seekid(songid, time)

              Seeks to the position TIME  (in
              seconds) of song SONGID .


.. function:: MPDClient.seekcur(time)

              Seeks to the position TIME  within the
              current song.  If prefixed by '+' or '-', then the time
              is relative to the current playing position.


.. function:: MPDClient.stop()

              Stops playing.


The current playlist
--------------------


.. function:: MPDClient.add(uri)

              Adds the file URI  to the playlist
              (directories add recursively). URI 
              can also be a single file.


.. function:: MPDClient.addid(uri, position)

              Adds a song to the playlist (non-recursive) and returns the song id.
 URI  is always a single file or
              URL.  For example::


                
                addid "foo.mp3"
                Id: 999
                OK
                            
.. function:: MPDClient.clear()

              Clears the current playlist.


.. function:: MPDClient.delete()

              Deletes a song from the playlist.


.. function:: MPDClient.deleteid(songid)

              Deletes the song SONGID  from the
              playlist


.. function:: MPDClient.move(to)

              Moves the song at FROM  or range of songs
              at START:END  to TO 
              in the playlist. 


.. function:: MPDClient.moveid(from, to)

              Moves the song with FROM  (songid) to TO  (playlist index) in the
              playlist.  If TO  is negative, it
              is relative to the current song in the playlist (if
              there is one).


.. function:: MPDClient.playlist()

              Displays the current playlist.


.. function:: MPDClient.playlistfind(tag, needle)

              Finds songs in the current playlist with strict
              matching.


.. function:: MPDClient.playlistid(songid)

              Displays a list of songs in the playlist. SONGID  is optional and specifies a
              single song to display info for.


.. function:: MPDClient.playlistinfo()

              Displays a list of all songs in the playlist, or if the optional
              argument is given, displays information only for the song SONGPOS  or the range of songs START:END  


.. function:: MPDClient.playlistsearch(tag, needle)

              Searches case-sensitively for partial matches in the
              current playlist.


.. function:: MPDClient.plchanges(version)

              Displays changed songs currently in the playlist since VERSION .

              To detect songs that were deleted at the end of the
              playlist, use playlistlength returned by status command.


.. function:: MPDClient.plchangesposid(version)

              Displays changed songs currently in the playlist since VERSION .  This function only
              returns the position and the id of the changed song, not
              the complete metadata. This is more bandwidth efficient.

              To detect songs that were deleted at the end of the
              playlist, use playlistlength returned by status command.


.. function:: MPDClient.prio(priority, start:end)

              Set the priority of the specified songs.  A higher
              priority means that it will be played first when
              "random" mode is enabled.

              A priority is an integer between 0 and 255.  The default
              priority of new songs is 0.


.. function:: MPDClient.prioid(priority, id)

              Same as ,
              but address the songs with their id.


.. function:: MPDClient.shuffle(start:end)

              Shuffles the current playlist. START:END  is optional and specifies
              a range of songs.


.. function:: MPDClient.swap(song1, song2)

              Swaps the positions of SONG1  and SONG2 .


.. function:: MPDClient.swapid(song1, song2)

              Swaps the positions of SONG1  and SONG2  (both song ids).


.. function:: MPDClient.addtagid(songid, tag, value)

              Adds a tag to the specified song.  Editing song tags is
              only possible for remote songs.  This change is
              volatile: it may be overwritten by tags received from
              the server, and the data is gone when the song gets
              removed from the queue.


.. function:: MPDClient.cleartagid(songid[, tag])

              Removes tags from the specified song.  If TAG  is not specified, then all tag
              values will be removed.  Editing song tags is only
              possible for remote songs.


Stored playlists
----------------

        Playlists are stored inside the configured playlist directory.
        They are addressed with their file name (without the directory
        and without the

        Some of the commands described in this section can be used to
        run playlist plugins instead of the hard-coded simple

.. function:: MPDClient.listplaylist(name)

              Lists the songs in the playlist.  Playlist plugins are
              supported.


.. function:: MPDClient.listplaylistinfo(name)

              Lists the songs with metadata in the playlist.  Playlist
              plugins are supported.


.. function:: MPDClient.listplaylists()

              Prints a list of the playlist directory.

              After each playlist name the server sends its last
              modification time as attribute "Last-Modified" in ISO
              8601 format.  To avoid problems due to clock differences
              between clients and the server, clients should not
              compare this value with their local clock.


.. function:: MPDClient.load(name[, start:end])

              Loads the playlist into the current queue.  Playlist
              plugins are supported.  A range may be specified to load
              only a part of the playlist.


.. function:: MPDClient.playlistadd(name, uri)

              Adds URI  to the playlist .
  will be created if it does
             not exist.


.. function:: MPDClient.playlistclear(name)

              Clears the playlist .


.. function:: MPDClient.playlistdelete(name, songpos)

              Deletes SONGPOS  from the
              playlist .


.. function:: MPDClient.playlistmove(name, songid, songpos)

              Moves SONGID  in the playlist  to the position SONGPOS .


.. function:: MPDClient.rename(name, new_name)

              Renames the playlist  to .


.. function:: MPDClient.rm(name)

              Removes the playlist  from
              the playlist directory.


.. function:: MPDClient.save(name)

              Saves the current playlist to  in the playlist directory.


The music database
------------------


.. function:: MPDClient.count(tag, needle)

              Counts the number of songs and their total playtime in
              the db matching TAG  exactly.


.. function:: MPDClient.find(type, what[, ...])

              Finds songs in the db that are exactly WHAT . TYPE  can
              be any tag supported by MPD, or one of the three special
              parameters — file  to search by

              full path (relative to the music directory), in  to restrict the search to
              songs in the given directory (also relative to the music
              directory) and any  to match against all
              available tags. WHAT  is what to find.


.. function:: MPDClient.findadd(type, what[, ...])

              Finds songs in the db that are exactly WHAT  and adds them to current playlist.
              Parameters have the same meaning as for find .


.. function:: MPDClient.list(type, artist)

              Lists all tags of the specified type. TYPE  can be any tag supported by MPD or file .
 ARTIST  is an optional parameter when
              type is album, this specifies to list albums by an
              artist.


.. function:: MPDClient.listall(uri)

              Lists all songs and directories in URI .


.. function:: MPDClient.listallinfo(uri)

              Same as listall , except it also
              returns metadata info in the same format as lsinfo .


.. function:: MPDClient.lsinfo(uri)

              Lists the contents of the directory URI .

              When listing the root directory, this currently returns
              the list of stored playlists.  This behavior is
              deprecated; use "listplaylists" instead.

              This command may be used to list metadata of remote
              files (e.g. URI beginning with "http://" or "smb://").

              Clients that are connected via UNIX domain socket may
              use this command to read the tags of an arbitrary local
              file (URI beginning with "file:///").


.. function:: MPDClient.readcomments(uri)

              Read "comments" (i.e. key-value pairs) from the file
              specified by "URI".  This "URI" can be a path relative
              to the music directory or a URL in the form
              "file:///foo/bar.ogg".

              This command may be used to list metadata of remote
              files (e.g. URI beginning with "http://" or "smb://").

              The response consists of lines in the form "KEY: VALUE".
              Comments with suspicious characters (e.g. newlines) are
              ignored silently.

              The meaning of these depends on the codec, and not all
              decoder plugins support it.  For example, on Ogg files,
              this lists the Vorbis comments.


.. function:: MPDClient.search(type, what[, ...])

              Searches for any song that contains WHAT . Parameters have the same meaning
              as for find , except that search is not
              case sensitive.


.. function:: MPDClient.searchadd(type, what[, ...])

              Searches for any song that contains WHAT 
              in tag TYPE  and adds them to current playlist.

              Parameters have the same meaning as for find ,
              except that search is not case sensitive.


.. function:: MPDClient.searchaddpl(name, type, what[, ...])

              Searches for any song that contains WHAT 
              in tag TYPE  and adds them to the playlist
              named NAME .

              If a playlist by that name doesn't exist it is created.

              Parameters have the same meaning as for find ,
              except that search is not case sensitive.


.. function:: MPDClient.update([uri])

              Updates the music database: find new files, remove
              deleted files, update modified files.
 URI  is a particular directory or
              song/file to update.  If you do not specify it,
              everything is updated.

              Prints "updating_db: JOBID" where JOBID  is a positive number
              identifying the update job.  You can read the current
              job id in the status  response.


.. function:: MPDClient.rescan([uri])

              Same as update , but also rescans
              unmodified files.


Stickers
--------

        "Stickers"

        The goal is to allow clients to share additional (possibly
        dynamic) information about songs, which is neither stored on
        the client (not available to other clients), nor stored in the
        song files (MPD has no write access).

        Client developers should create a standard for common sticker
        names, to ensure interoperability.

        Objects which may have stickers are addressed by their object
        type ("song" for song objects) and their URI (the path within
        the database for songs).

.. function:: MPDClient.sticker(type, uri, name)

              Reads a sticker value for the specified object.


.. function:: MPDClient.sticker(type, uri, name, value)

              Adds a sticker value to the specified object.  If a
              sticker item with that name already exists, it is
              replaced.


.. function:: MPDClient.sticker(type, uri[, name])

              Deletes a sticker value from the specified object.  If
              you do not specify a sticker name, all sticker values
              are deleted.


.. function:: MPDClient.sticker(type, uri)

              Lists the stickers for the specified object.


.. function:: MPDClient.sticker(type, uri, name)

              Searches the sticker database for stickers with the
              specified name, below the specified directory (URI).
              For each matching song, it prints the URI and that one
              sticker's value.


Connection settings
-------------------


.. function:: MPDClient.close()

              Closes the connection to MPD.  MPD will try to send the
              remaining output buffer before it actually closes the
              connection, but that cannot be guaranteed.  This command
              will not generate a response.


.. function:: MPDClient.kill()

              Kills MPD.


.. function:: MPDClient.password(password)

              This is used for authentication with the server. PASSWORD  is simply the plaintext
              password.


.. function:: MPDClient.ping()

              Does nothing but return "OK".


Audio output devices
--------------------


.. function:: MPDClient.disableoutput(id)

              Turns an output off.


.. function:: MPDClient.enableoutput(id)

              Turns an output on.


.. function:: MPDClient.toggleoutput(id)

              Turns an output on or off, depending on the current
              state.


.. function:: MPDClient.outputs()

              Shows information about all outputs.

              Return information::


                
                outputid: 0
                outputname: My ALSA Device
                outputenabled: 0
                OK
                            
Reflection
----------


.. function:: MPDClient.config()

              Dumps configuration values that may be interesting for
              the client.  This command is only permitted to "local"
              clients (connected via UNIX domain socket).

              The following response attributes are available::


.. function:: MPDClient.commands()

              Shows which commands the current user has access to.


.. function:: MPDClient.notcommands()

              Shows which commands the current user does not have
              access to.


.. function:: MPDClient.tagtypes()

              Shows a list of available song metadata.


.. function:: MPDClient.urlhandlers()

              Gets a list of available URL handlers.


.. function:: MPDClient.decoders()

              Print a list of decoder plugins, followed by their
              supported suffixes and MIME types.  Example response::


                plugin: mad
                suffix: mp3
                suffix: mp2
                mime_type: audio/mpeg
                plugin: mpcdec
                suffix: mpc
Client to client
----------------

        Clients can communicate with each others over "channels".  A
        channel is created by a client subscribing to it.  More than
        one client can be subscribed to a channel at a time; all of
        them will receive the messages which get sent to it.

        Each time a client subscribes or unsubscribes, the global idle
        event subscription is generated.  In
        conjunction with the channels command, this
        may be used to auto-detect clients providing additional
        services.

        New messages are indicated by the message
        idle event.

.. function:: MPDClient.subscribe(name)

              Subscribe to a channel.  The channel is created if it
              does not exist already.  The name may consist of
              alphanumeric ASCII characters plus underscore, dash, dot
              and colon.


.. function:: MPDClient.unsubscribe(name)

              Unsubscribe from a channel.


.. function:: MPDClient.channels()

              Obtain a list of all channels.  The response is a list
              of "channel:" lines.


.. function:: MPDClient.readmessages()

              Reads messages for this client.  The response is a list
              of "channel:" and "message:" lines.


.. function:: MPDClient.sendmessage(channel, text)

              Send a message to the specified channel.


