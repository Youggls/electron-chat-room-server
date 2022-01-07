# Protocol

- Protocol token: `**@@~~`

- Command patter: `**@@~~{Command}\r\n{param1}\r\n{param2}...`

## Client to Server

### user login

> User login

`**@@~~LOGIN\r\n{user name}`

- example: user name is Bob

    `**@@~~LOGIN\r\nBob`

### user send message

> User send a message to some people or every.

`**@@~~MESSAGE\r\n{sender name}\r\n{receiver name}\r\n{message detail}`

- example1: Bob send `hello` to Alice

    `**@@~~MESSAGE\r\nBob\r\nAlice\r\nhello`

- example2: Bob send `I am Bob` to all people

    `**@@~~MESSAGE\r\nBob\r\nPUBLIC\r\nI am Bob`

### Check status

> User check server status, every 30s.

`**@@~~CHECK\r\n{user name}`

## Server to Client

### Reply login

> Server reply client

`**@@~~LOGIN\r\n{isSuccess}\r\n{errMsg}`

- possible value for `isSuccess`: `TRUE`, `FALSE`

- possible value for `errMsg`: `Login successfully`, `Duplicate username`, `Unknown error`

- example1: Login successfully

    `**@@~~LOGIN\r\nTRUE\r\nLogin successfully`

- example2: Duplicate username

    `**@@~~LOGIN\r\nFALSE\r\nDuplicate username`

### Send message

> Server send message from A to B

`**@@~~MESSAGE\r\n{sender name}\r\n{chat type}\r\n{message detail}`

possible value for `chat type`: `PERSONAL`, `PUBLIC`

- example1: Bob send message to Alice, say hello

    `**@@~~MESSAGE\r\nBob\r\nPERSONAL\r\nhello`

- example2: Bob send message to all, say I am Bob

    `**@@~~MESSAGE\r\nBob\r\nPUBLIC\r\nI am Bob`

### Reply message

> A send a message to B, server reply A.

`**@@~~REPLYMSG\r\n{receiver name}\r\n{isSuccess}\r\n{errMsg}`

- possible value for `isSuccess`: `TRUE`, `FALSE`

- possible value for `errMsg`: `Send successfully`, `Receiver offline`, `Unknown error`

- example1: A send message to Bob, success

`**@@~~REPLYMSG\r\nBob\r\nTRUE\r\nSend successfully`

- example2: A send message to Bob, failed because of B offline

`**@@~~REPLYMSG\r\nBob\r\nFALSE\r\nReceiver offline`

### Reply check status

> Server reply server status

`**@@~~CHECK\r\n{isSuccess}\r\n{online people number}\r\n{errMsg}\r\n{people1\npeople2\n...peoplen}`

- possible value for `online people number`: integer

- possible value for `isSuccess`: 'TRUE', 'FALSE'

    If user list doesn't have current user name, return false, else return true

- parameter 3: the current user list, seperated by \n

- example: online people number is 123

    `**@@~~CHECK\r\n123`
