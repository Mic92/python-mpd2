========
Commands
========

Status Commands
---------------

===========  =======  =============
clearerror            fetch_nothing
currentsong           fetch_object
idle         [<str>]  fetch_list
noidle                None
status                fetch_object
stats                 fetch_object
===========  =======  =============

Playback Option Commands
------------------------
==================  ======  =============
consume             <bool>  fetch_nothing
crossfade           <int>   fetch_nothing
mixrampdb           <str>   fetch_nothing
mixrampdelay        <int>   fetch_nothing
random              <bool>  fetch_nothing
repeat              <bool>  fetch_nothing
setvol              <int>   fetch_nothing
single              <bool>  fetch_nothing
replay_gain_mode    <str>   fetch_nothing
replay_gain_status          fetch_item
==================  ======  =============

Playback Control Commands
-------------------------

========  ===========  =============
next                   fetch_nothing
pause     [<bool>]     fetch_nothing
play      [<int>]      fetch_nothing
playid    [<int>]      fetch_nothing
previous               fetch_nothing
seek      <int> <int>  fetch_nothing
seekid    <int> <int>  fetch_nothing
seekcur   <int>        fetch_nothing
stop                   fetch_nothing
========  ===========  =============

Playlist Commands
-----------------

==============  =============  =============
add             <str>          fetch_nothing
addid           <str> [<int>]  fetch_item
clear                          fetch_nothing
delete          <int>          fetch_nothing
deleteid        <int>          fetch_nothing
move            <int> <int>    fetch_nothing
moveid          <int> <int>    fetch_nothing
playlist                       fetch_playlist
playlistfind    <locate>       fetch_songs
playlistid      [<int>]        fetch_songs
playlistinfo    [<int>]        fetch_songs
playlistsearch  <locate>       fetch_songs
plchanges       <int>          fetch_songs
plchangesposid  <int>          fetch_changes
prio            <int> <str>    fetch_nothing
prioid          <int> <id>     fetch_nothing
shuffle         [<str>]        fetch_nothing
swap            <int> <int>    fetch_nothing
swapid          <int> <int>    fetch_nothing
==============  =============  =============

Stored Playlist Commands
------------------------

================  =================  ===============
listplaylist      <str>              fetch_list
listplaylistinfo  <str>              fetch_songs
listplaylists                        fetch_playlists
load              <str>              fetch_nothing
playlistadd       <str> <str>        fetch_nothing
playlistclear     <str>              fetch_nothing
playlistdelete    <str> <int>        fetch_nothing
playlistmove      <str> <int> <int>  fetch_nothing
rename            <str> <str>        fetch_nothing
rm                <str>              fetch_nothing
save              <str>              fetch_nothing
================  =================  ===============

Database Commands
-----------------

===========  ================  ==============
count        <locate>          fetch_object
find         <locate>          fetch_songs
findadd      <locate>          fetch_nothing
list         <str> [<locate>]  fetch_list
listall      [<str>]           fetch_database
listallinfo  [<str>]           fetch_database
lsinfo       [<str>]           fetch_database
search       <locate>          fetch_songs
searchadd    <locate>          fetch_songs
searchaddpl  <str> <locate>    fetch_songs
update       [<str>]           fetch_item
rescan       [<str>]           fetch_item
===========  ================  ==============

Sticker Commands
----------------

==============  =======================  =============
sticker get     <str> <str> <str>        fetch_item
sticker set     <str> <str> <str> <str>  fetch_nothing
sticker delete  <str> <str> [<str>]      fetch_nothing
sticker list    <str> <str>              fetch_list
sticker find    <str> <str> <str>        fetch_songs
==============  =======================  =============

Connection Commands
-------------------

========  =====  =============
close            None
kill             None
password  <str>  fetch_nothing
ping             fetch_nothing
========  =====  =============

Audio Output Commands
---------------------

=============  =====  =============
disableoutput  <int>  fetch_nothing
enableoutput   <int>  fetch_nothing
outputs               fetch_outputs
=============  =====  =============

Reflection Commands
-------------------

===========  =============
config       fetch_item
commands     fetch_list
notcommands  fetch_list
tagtypes     fetch_list
urlhandlers  fetch_list
decoders     fetch_plugins
===========  =============

Client To Client
----------------

============  ===========  ==============
subscribe     <str>        fetch_nothing
unsubscribe   <str>        fetch_nothing
channels                   fetch_list
readmessages               fetch_messages
sendmessage   <str> <str>  fetch_nothing
============  ===========  ==============
