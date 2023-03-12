async def main(message, client):
    ROWS = 6
    COLUMNS = 7


    async def printboard():
        boardstr = ""
        for row in board:
            for col in row:
                boardstr += col + " "
            boardstr += "\n"
        await message.channel.send("```" + boardstr + "```")


    async def placecoin():  # return True/False to indicate success in placing the coin
        # find the first unfilled row/hole in the specified column
        rowin = len(board) - 1
        while board[rowin][colin] != "🟦":
            rowin -= 1
            if rowin < 0:
                return False

        if rowin >= 0:
            if pnum == "1":
              board[rowin][colin] = "🔴"
            elif pnum == "2":
              board[rowin][colin] = "🟡"
            return True


    async def fourinarow():  # checks for 4-in-a-rows on the board
        # loop from bottom to top, left to right
        for r in range(len(board)-1, -1, -1):  # 5, 4, 3, 2, 1, 0
            for c in range(COLUMNS):
                if c <= 3:  # coin is in left half of board
                    if await checkforline(r, c, 0, 1) or await checkforline(r, c, -1, 1):  # checks for horiz & bltr line
                        return True
                if c >= 3:  # coin is in right half of board
                    if await checkforline(r, c, -1, -1):  # checks for brtl line
                        return True
                if r >= 3:  # coin is in bottom half of board
                    if await checkforline(r, c, -1, 0):  # checks for vert line
                        return True
        return False


    async def checkforline(r, c, rinc, cinc):  # row increment & column increment
        if board[r][c] != "🟦":
            if board[r][c] == board[r+rinc][c+cinc] == board[r+2*rinc][c+2*cinc] == board[r+3*rinc][c+3*cinc]:
                return True
        return False


    board = [["🟦" for i in range(COLUMNS)] for j in range(ROWS)]  # create 7x6 connect-4 board
    await printboard()

    turnnum = 0
    while await fourinarow() is False:
        pnum = str(turnnum % 2 + 1)  # player number
        if turnnum > 41:  # if the board is full (i.e. there have already been 42 turns)
            await message.channel.send("It's a draw!")
            break

        def check(msg):
          return msg.author == message.author

        await message.channel.send("Player " + pnum + ", type the column (1-7) you want to place your coin in: ")
        colinstr = await client.wait_for('message', check=check)
        colinstr = colinstr.content
        if colinstr in (str(n) for n in range(1, 8)):  # proceed if the input is a number from 1-7
            colin = int(colinstr) - 1  # the actual integer for the column input
            if await placecoin() is True:  # place the coin; procceed if successful (if the column isn't full)
                await printboard()
                if turnnum >= 6 and await fourinarow() is True:  # only check for 4-in-a-row if there have been at least 7 turns
                    await message.channel.send("Player " + pnum + " wins!")
                turnnum += 1
            else:
                await message.channel.send("That column is full.")
        else:
            await message.channel.send("Make sure it's one number from 1 to 7.")


if __name__ == "__main__":
  main()