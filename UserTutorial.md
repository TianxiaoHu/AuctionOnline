# 网络拍卖行用户手册

胡天晓 	  14300240007	14保密管理

## 简介

### 概述

本软件可以实现网络拍卖功能，分为服务器端和客户端。只能同时运行一个服务器端，但可以运行多个客户端。

Github: https://github.com/TianxiaoHu/AuctionOnline

### 运行方式

#### Windows

为方便windows 平台使用，已使用pyinstaller打包为独立的exe可执行文件，用户双击server.exe或client.exe即可运行。

#### Mac/Linux

首先在终端中更改目录到当前目录：

```
$ cd directory/to/AuctionOnline
```

启动服务器端：

```
$ python server.py
```

启动客户端：

```
$ python client.py
```

要求电脑中已经安装python 2.7解释器，及相应python第三方库**Crypto**。

## 功能介绍

### 服务器端

程序启动后，如果初始化成功，则会弹出提示语，如果因为某些原因初始化失败（如端口占用等），程序将自动退出。

#### 显示帮助

点击页面上方的`Help`按钮即可显示支持的服务器端指令集及详细用法。

若用户输入了错误的指令或指令格式，页面上会出现*Invalid input*提示信息。

#### 指令集

- `/auctions`

  用于查看当前所有拍卖房间。

  可能出现的错误信息：

  - *No room available now, create one first.*

    若当前无房间，则会提示创建房间。

- `/opennewauction auctionname base gap`

  用于创建新的拍卖房间，`auctionname`为房间名，`base`为起拍价，`gap`为每次出价最低增加的价格。

  如：`/opennewauction car 10000 100`

  **所有在线用户会收到新拍卖房间开启的系统消息。**

  可能出现的错误信息：

  - *A room named `auctionname` already exist.*

    房间名重复，可更改房间名重新创建。

- `/users`

  用于列出当前所有在线用户。

  如果用户尚未加入任何房间，则会显示其尚未加入。

- `/list auctionname`

  用于列出某房间的拍卖信息。包括：房间名、起拍价、每次竞价最低增加价格、当前最高价出价者、房间内在线用户（不包括已经离开的拍卖者）及出价历史。

  可能出现的错误信息：

  - *No auction room fits input*

    没有符合要求的房间名，可用`/auctions`指令查看所有房间后重新查询。

- `/msg username1 username2 ... | message`

  用于对一个或多个用户发送消息，`username`为用户登录时的用户名。最后一个用户名和消息之间用`|`分隔。

  可能出现的错误信息：

  - *Fail to send message to `username_x`*

    向第x个用户发送消息失败，可能由端口被挤占（用户掉线）或用户名输入错误所致。

    其他用户会正常收到消息，不受影响。

- `/broadcast auctionname message`

  用于对某个拍卖房间进行房间广播，所有在房间中的用户会收到消息。

  可能出现的错误信息：

  - *Fail to broadcast to `auctionname`*

    广播失败，有可能由于网络原因或房间名输入错误导致，可用`/auctions`指令查看所有房间后重试。

- `/kickout username1 username2 ...`

  用于踢出房间内用户，支持同时踢出多人，但不能踢出当前出价最高的用户（拍卖已结束的房间除外）。

  **被踢出的用户及被踢出用户所的的房间内其他用户均会收到该用户已被踢出的消息。**

  可能出现的错误信息：

  - *`username_x` not in any room*

    第x个用户尚未加入任何房间，无法将其踢出。

  - *`username_X` doesn't exist*

    第x个用户不存在，可用`/users`指令查看所有在线用户后重试。

  - *`username_x`bid the highest price!*

    拍卖尚未结束且第x个用户当前出价最高，不能从房间中踢出，可用`/finish auctionname`指令结束拍卖后重试。

- `/finish auctionname`

  用于结束房间内拍卖。房间内拍卖结束后，房间相当于被锁定。用户无法继续出价，不在房间内的用户将无法再加入房间，房间内的所有用户都可被服务器踢出，用户可以使用`/leave`指令离开房间。

  **房间内用户都将收到*`user_x` wins the auction with price `current_highest_price`*的提示消息。**

  可能出现的错误信息：

  - *Auction room has been closed*

    该房间已经被关闭，不能再次关闭。

  - *No auction room fits input*

    没有符合要求的房间名，可用`/auctions`指令查看所有房间后重新查询。

- `/close auctionname`

  用于关闭拍卖房间并从服务器端删除该房间的历史信息。拍卖房间内必须没有任何用户。

  可能出现的错误信息：

  - *Users in auction room, can't close now*

    房间内依旧有用户在线，可在确认房间已经关闭后用`/kickout`指令踢出。

  - *No auction room fits input*

    没有符合要求的房间名，可用`/auctions`指令查看所有房间后重新查询。

- `/restart auctionname`

  用于重新启动某房间内的拍卖。房间内所有拍卖历史将被清空，拍卖信息被还原为初始信息。

  **房间内所有用户将收到拍卖已重启的提示信息。**已经在房间内的用户不会被踢出。重启后其他用户依然可以正常加入拍卖房间。

  可能出现的错误信息：

  - *No auction room fits input*

    没有符合要求的房间名，可用`/auctions`指令查看所有房间后重新查询。

#### 传输日志

为方便历史追溯及客户端动作记录与核对，服务器端设置了传输日志窗口，可以显示出每个用户的网络地址及与服务器交互的详细动作信息。

当传输日志窗口信息过多时，可以点击`Clear log`按钮清空日志。

#### 退出程序

点击`Exit`按钮即可退出程序，释放内存。

### 客户端

#### 显示帮助

点击页面上方的`Help`按钮即可显示支持客户端指令集及详细用法。

若用户输入了错误的指令或指令格式，服务器端会反馈用户*Invalid input*提示信息。

#### 指令集

- `/login username`

  用于以`username`身份登录到服务器端。

  可能出现的错误信息：

  - *You have already logged in! Exit first..*

    当用户已经用另一`username`登录到服务器且尚未使用`/exit`指令退出时，则双重登录被拒绝。

  - *Username occupied, try another..*

    已经有另一用户占用了此用户名，需要更换用户名登录。


- `/auctions`

  用于查看当前所有拍卖房间。

- `/join auctionname`

  用于加入某个拍卖房间，注意每个用户只能同时在一个房间内。

  **房间内所有在线用户将会收到有人加入的信息。**

  可能出现的错误信息：

  - *You have joined an auction, leave it first*

    用户已经加入了一个房间（包括当前房间），必须先用`/leave`指令离开房间才能再次加入。

  - *No this room..try another*

    房间不存在，可用`/auctions`指令查看所有房间后重试。

  - *Room have been closed..try another*

    拍卖已经结束，用户无法加入房间。

- `/list`

  用于查看当前房间价格信息及出价历史。

  可能出现的错误信息：

  - *You must join a room first..*

    用户尚未加入任何房间，因此无法查看房间信息。

- `/bidders`

  用于查看当前房间的所有在线用户。

  可能出现的错误信息：

  - *You must join a room first..*

    用户尚未加入任何房间，因此无法查看房间在线用户。

- `/bid price`

  用于为当前房间拍卖物品出价。

  **房间内所有用户将会收到出价信息。**

  可能出现的错误信息：

  - *You must join a room first..*

    用户尚未加入任何房间，因此无法为物品出价。

  - *Price refused! Please bid higher than `least_price`*

    用户出价过低，必须出价高于当前价格 + 每次出价最低增加的价格，可以用`/list`指令查看当前房间信息。

  - *Auction closed*

    本次拍卖已经结束（被server端用`/finish`指令关闭），用户无法继续出价。

- `/pubmsg message`

  用于向当前房间内所有在线用户统一发送房间内公开消息。

  可能出现的错误信息：

  - *You must join a room first..*

    用户尚未加入任何房间，因此无法发布房间内公开消息。

- `/primsg username1 username2 ... | message`

  用于向任意个当前房间内的用户发送私人消息。注意最后一个`username`和`message`之间需要用`|`分隔。

  可能出现的错误信息：

  - *You must join a room first..*

    用户尚未加入任何房间，因此无法对房间内用户发送私人消息。

  - *No user `username_x` in the room*

    第x个用户不在房间内，无法发送私人消息。

  - *The user `username_x` may not exist.. try again*

    第x个用户不存在，可用`/bidders`指令查看当前房间在线用户后重试。

- `/leave`

  用于退出当前房间，但在当前房间拍卖未结束且当前用户出价最高时无法退出。

  **房间内所有用户将会收到有人离开房间的消息。**

  可能出现的错误信息：

  - *You must join a room first..*

    用户尚未加入任何房间，因此无法离开。

  - *You can't leave now!*

    当前房间拍卖未结束且出价最高，此时无法退出。

- `/exit`

  用于退出登录并永久清除服务器端所有用户信息。若用户在房间内则会自动执行`/leave`指令，**房间内所有用户将会收到其退出的消息，服务器端也会收到用户退出登录的消息**。

  在当前房间拍卖未结束且当前用户出价最高时无法退出。

  可能出现的错误信息：

  - *You can't leave now!*

    当前房间拍卖未结束且出价最高，此时无法退出。

#### 退出程序

当用户执行完`/exit`指令后，点击`Exit`按钮即可退出程序，释放内存。