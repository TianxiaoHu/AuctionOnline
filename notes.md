# Auction Online Manual

## Server

- `/opennewauction roomname baseline`
  open a new auction room
  name represents auction room name
  baseline remarks the lowest auction price
  e.g. /opennewauction car 98

- `/msg message user1 user2 ...`
  send message to user(s)
  e.g. /msg testcase htx
- `/kickout user`
  force a user to leave auction room
  e.g. /kickout htx
- `/list`
  list the available auction rooms
  *Notice: the same to `/auctions`*
- `/auctions`
  list the available auction rooms
  *Notice: the same to `/list`*
- `/close`
  close an auction room(must exist)
  e.g. /close car

## Client

- `/login username`
  login as username(must be specific)
  e.g. /login htx
- `/auctions`
  list the available auction rooms
- `/list`
  check the bid history(must enter a room first)
- `/join roomname`
  join an auction room
  e.g. /join car
- `/bid price`
  bid a price in the auction room
  the price must be higher than the current highest price
  e.g. /bid 80
- `/leave`
  leave the auction room
  you can't be the highest-price bidder
- `/exit`
  shut down the client and clear the data related to current user in server

## BUG to fix:

- ~~duplicate `/login`~~
- ~~set a ceiling price and smallest price gap~~
- ~~`/close` no parameter **AND SO ON**~~ 

## New Function:

- ~~list bidders in room(Client)~~
- ~~chatting room mode(Client)~~
  - ~~room message `/pubmsg`~~
  - ~~private message `/primsg`~~
- ~~auction room broadcasting(Server)~~
- ~~restart auction(Server)~~
- ~~extend `/kickout` kickout many users at the same time(Server)~~
- ~~Encryption of data——in case of MITM attack~~
- ~~extend `/msg` and `/broadcast` : separated by space should be replaced(considering raw_input?)~~
- ~~Server `enter`~~
- ~~MODIFY Server `list`~~
- ~~How to deal with ceiling price **below** current + gap?~~
- ~~Broadcasting to all users —— when open a new auction~~
- ~~finish the 'help' reminder~~
- ~~request for current auction room info(current price、baseline、gap)~~
- ~~finish the auction and close the room~~

- ~~list all online users(with their room)~~
- ~~duplicate `join`~~


