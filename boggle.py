import asyncio
import random
import re

# dice sets
DICE_CLASSIC = ('AACIOT', 'ABILTY', 'ABJMO1', 'ACDEMP', 'ACELRS', 'ADENVZ', 'AHMORS', 'BIFORX', 'DENOSW', 'DKNOTU', 'EEFHIY', 'EGKLUY', 'EGINTV', 'EHINPS', 'ELPSTU', 'GILRUW')
DICE_NEW = ('AAEEGN', 'ABBJOO', 'ACHOPS', 'AFFKPS', 'AOOTTW', 'CIMOTU', 'DEILRX', 'DELRVY', 'DISTTY', 'EEGHNW', 'EEINSU', 'EHRTVW', 'EIOSST', 'ELRTTY', 'HIMNU1', 'HLNNRZ')
DICE_BIG = ('AAAFRS', 'AAEEEE', 'AAFIRS', 'ADENNN', 'AEEEEM', 'AEEGMU', 'AEGMNN', 'AFIRSY', 'BJK1XZ', 'CCENST', 'CEIILT', 'CEIPST', 'DDHNOT', 'DHHLOR', 'DHHLOR', 'DHLNOR', 'EIIITT', 'CEILPT', 'EMOTTT', 'ENSSSU', 'FIPRSY', 'GORRVW', 'IPRRRY', 'NOOTUW', 'OOOTTU')
DICE_SUPER_BIG = ('AAAFRS', 'AAEEEE', 'AAEEOO', 'AAFIRS', 'ABDEIO', 'ADENNN', 'AEEEEM', 'AEEGMU', 'AEGMNN', 'AEILMN', 'AEINOU', 'AFIRSY', '123456', 'BBJKXZ', 'CCENST', 'CDDLNN', 'CEIITT', 'CEIPST', 'CFGNUY', 'DDHNOT', 'DHHLOR', 'DHHNOW', 'DHLNOR', 'EHILRS', 'EIILST', 'EILPST', 'EIO000', 'EMTTTO', 'ENSSSU', 'GORRVW', 'HIRSTV', 'HOPRST', 'IPRSYY', 'JK1WXZ', 'NOOTUW', 'OOOTTU')
SPECIALS = ('_ ', 'Qu', 'In', 'Th', 'Er', 'He', 'An')


async def main(message, client, args):
  channel = message.channel
  
  # default settings
  DICE = list(DICE_NEW)
  ROWS = 4
  COLS = 4
  TIME = "3m"
  TIMER_FREQ = 5
  TIMEOUT = 30
  play = True
  
  # process args, if any
  if len(args) > 0:
    # identify arg types
    arg_order = []
    for arg in args:
      try:  # if arg is a number
        int(arg)
        arg_order.append("dimension")
      except ValueError:
        if valid_time(arg):
          arg_order.append("time")
        elif arg == "classic" or arg == "c" or arg == "old" or arg == "o":
          arg_order.append("classic")
        else:
          arg_order.append("invalid")

    # modify rows, cols, and time based on arg types
    if arg_order == ["dimension"]:
      ROWS = COLS = int(args[0])
    elif arg_order == ["dimension", "time"]:
      ROWS = COLS = int(args[0])
      TIME = args[1]
    elif arg_order == ["dimension", "dimension"]:
      ROWS, COLS = int(args[0]), int(args[1])
    elif arg_order == ["dimension", "dimension", "time"]:
      ROWS, COLS, TIME = int(args[0]), int(args[1]), args[2]
    elif arg_order == ["time"] or arg_order == ["time", "classic"]:
      TIME = args[0]
    elif arg_order == ["time", "dimension"]:
      TIME = args[0]
      ROWS = COLS = int(args[1])
    elif arg_order == ["time", "dimension", "dimension"]:
      TIME, ROWS, COLS = args[0], int(args[1]), int(args[2])
    elif arg_order == ["classic"]:
      pass
    elif arg_order == ["classic", "time"]:
      TIME = args[1]
    else:  # invalid command format
      await channel.send("Command format:\n```[b\n[b rows (square board)\n[b rows time (square board)\n[b rows columns\n[b rows columns time\n[b time\n[b time rows (square board)\n[b time rows columns\n[b time classic\n[b classic\n[b classic time```\nDefault: 4 rows, 4 columns, 3m time\nExample time formats: `5m`, `45s`, `4m30s`\n`classic`, `c`, `old`, or `o` can be used for classic dice.")
      play = False

    # modify dice set based on board size/"classic"
    if "classic" in arg_order:
      DICE = list(DICE_CLASSIC)
    else:
      size = ROWS * COLS
      if 16 < size <= 25:
        DICE = list(DICE_BIG)
      elif size > 25:
        DICE = list(DICE_SUPER_BIG)

  # play, if valid command format
  if play:
    # generate board
    dice = DICE.copy()
    board = "Time ({}) starts now! React with <:neat:770893766264356864> to participate.\n```".format(TIME)
    for r in range(ROWS):
      for c in range(COLS):
        die = random.choice(dice)
        letter = die[random.randrange(len(die))]  # random die face
        try:  # if letter is a number representing a special die face
          board += SPECIALS[int(letter)] + ' '
        except ValueError:
          board += letter + '  '
        dice.remove(die)
        if len(dice) == 0:
          dice = DICE.copy()  # reset dice
      board += '\n'
    board += "```"
    board_msg = await channel.send(board)
    await board_msg.add_reaction(':neat:770893766264356864>')

    # timer
    time_remaining = time_to_secs(TIME)
    extra = time_remaining % TIMER_FREQ
    await asyncio.sleep(extra)
    time_remaining -= extra  # start countdown at a multiple of TIMER_FREQ
    timer = await channel.send(secs_to_time(time_remaining) + " remaining...")
    while time_remaining > 0:  # update timer every TIMER_FREQ seconds
      await asyncio.sleep(TIMER_FREQ)
      time_remaining -= TIMER_FREQ
      await timer.edit(content=secs_to_time(time_remaining) + " remaining...")
    
    # identify players
    # the next 2 lines of inefficient, circular code work, but board_msg.reactions doesn't ¯\_(ツ)_/¯
    board_msg2 = await channel.fetch_message(board_msg.id)
    players = await board_msg2.reactions[0].users().flatten()
    players.remove(client.user)  # remove bot from players
    
    # if people participated (reacted), take responses and score
    num_players = len(players)
    if num_players == 0:
      await channel.send("I guess no one wanted to play :(")
    else:
      await channel.send("Time ({}) is up! Send your words below.".format(TIME))
      responses = [None] * num_players
      
      # take responses from all players
      def check(m):
        return m.channel == channel and m.author in players_wo_response
  
      if message.guild.name == "Bot Testing":
        TIMEOUT = None

      players_wo_response = players.copy()
      while len(players_wo_response) > 0:
        try:
          response = await client.wait_for('message', check=check, timeout=TIMEOUT)
          player = response.author
          
          # remove non-word characters, split into unique words, add to responses; match player index
          responses[players.index(player)] = set(re.sub('[^A-Za-z-\']+', ' ', response.content).split())
          
          players_wo_response.remove(player)
        except asyncio.TimeoutError:  # timeout
          timeout_msg = ""
          for player in players_wo_response:
            timeout_msg += player.mention + ", "
          timeout_msg = timeout_msg[:-2]  # exclude last comma
          timeout_msg += " took too long."
          await channel.send(timeout_msg)
          break
  
      # remove responseless players and empty responses
      players = [p for p in players if p not in players_wo_response]
      responses = [r for r in responses if r is not None]
      num_players = len(players)
            
      # score
      scores = []
      word_lists = []
      if num_players == 1:
        shared_words = set()
      else:
        shared_words = responses[0].intersection(*responses)
      
      for i in range(num_players):
        score = 0
        word_list = ""
        unique_words = responses[i].difference(shared_words)
        
        # go through unique words in alphabetical order
        for word in sorted(list(unique_words)):
          length = len(re.sub('[-\']', '', word))  # length without apostrophes & hyphens
          points = 0

          # assign points based on length
          if length == 3 or length == 4:
            points = 1
          elif length == 5:
            points = 2
          elif length == 6:
            points = 3
          elif length == 7:
            points = 5
          elif length >= 8:
            points = 11
          
          score += points
          word_list += "{} ({}), ".format(word, points)
        
        scores.append(score)
        word_lists.append(word_list[:-2])  # exclude last comma
    
      # add info to scoreboard in descending score order
      scoreboard = ""
      order = sorted(range(num_players), key=lambda i: scores[i], reverse=True)  # indices in descending score order
      for i in order:
        scoreboard += "**{}: {}**\n".format(players[i].mention, scores[i])
        word_list = word_lists[i]
        if word_list == "":
          scoreboard += "\n"
        else:
          scoreboard += word_list + "\n\n"
    
      # add shared words to scoreboard, if any
      if len(shared_words) > 0:
        shared = ""
        for word in sorted(list(shared_words)):  # go through shared words in alphabetical order
          shared += word + ", "
        shared = shared[:-2]  # exclude last comma
        scoreboard += "__Shared words:__ " + shared
      
      await channel.send(scoreboard)


def valid_time(time: str):
  try:
    int(re.sub('[ms]', '', time))
    return True
  except ValueError:
    return False
    

def time_to_secs(time: str):
  secs = 0
  m_index = time.find('m')
  s_index = time.find('s')
  if m_index >= 0:
    secs += int(time[:m_index]) * 60
  if s_index >= 0:
    secs += int(time[m_index + 1 : s_index])
  return secs


def secs_to_time(secs: int):
  time = ""
  m = secs // 60
  s = secs % 60
  if m > 0:
    time += str(m) + 'm'
  if s > 0 or (m == 0 and s == 0):
    time += str(s) + 's'
  return time


if __name__ == "__main__":
  main()
