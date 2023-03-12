import random
import bisect

async def main(message, client, args):
  # default settings
  WORD_LEN = 5
  TURNS = 6

  # variables
  guess = ""
  guesses = 0
  gay = []
  feedback = message.author.mention + "'s wordle:\n"
  won = False
  in_word = []
  not_in_word = []
  not_yet_guessed = [chr(i) for i in range(97, 123)]  # lowercase letters

  # register a guess when it's in the same channel, by the same author, and a valid word
  def check(m):
    return m.channel == message.channel and m.author == message.author and len(m.content) == WORD_LEN
   
  # assign values for word length and # turns, if specified
  if len(args) > 0:
    try:
      WORD_LEN = int(args[0])
    except ValueError:
      await message.channel.send("Make sure the word length is a number.")
      # to-do: word_len must be between 1 and 20
    if len(args) > 1:
      try:
        TURNS = int(args[1])
        # to-do: calculate the max number of turns for n-letter long words (use 2k char limit)
      except ValueError:
        await message.channel.send("Make sure the number of turns is a number.")
  
  # create a list of words with WORD_LEN letters & choose one randomly
  with open("english_words.txt") as english_words:
    words = [line.rstrip('\n') for line in english_words if len(line.rstrip('\n')) == WORD_LEN]
  word = random.choice(words)
  await message.channel.send(str(WORD_LEN) + "-letter word created.")

  while guesses < TURNS and not won:
    guess_msg = await client.wait_for('message', check=check)
    guess = guess_msg.content.lower()
    if guess not in words:
      await guess_msg.add_reaction('❌')
    else:
      guesses += 1
      gay = ['⬛']*WORD_LEN

      letter_occurrences = {}
      for letter in word:
        if letter not in letter_occurrences.keys():
          letter_occurrences[letter] = word.count(letter)

      for i in range(WORD_LEN):
        if guess[i] == word[i]:
          gay[i] = '🟩'
          letter_occurrences[word[i]] -= 1
          if guess[i] not in in_word:
            bisect.insort(in_word, guess[i])  # alphabetical insert
        try:
          not_yet_guessed.remove(guess[i])
        except ValueError:  # the current letter, guess[i], has already been previously guessed
          pass
      for i in range(WORD_LEN):
        try:
          if letter_occurrences[guess[i]] > 0 and gay[i] != '🟩':
            gay[i] = '🟨'
            letter_occurrences[guess[i]] -= 1
            if guess[i] not in in_word:
              bisect.insort(in_word, guess[i])  # alphabetical insert
          elif gay[i] != '🟩':
            if guess[i] not in not_in_word:
              bisect.insort(not_in_word, guess[i])  # alphabetical insert
        except KeyError:
          if guess[i] not in not_in_word:
            bisect.insort(not_in_word, guess[i])  # alphabetical insert
      
      won = '🟨' not in gay and '⬛' not in gay
      
      for color in gay:
        feedback += color + ' '
      feedback += '\n'
      for letter in guess:
        feedback += ':regional_indicator_' + letter + ': '
      feedback += '\n' 
      lives = '❤ ' * (TURNS - guesses + 1)
      letter_info = '```in word: ' + ''.join([l.upper() for l in in_word]) + '\nnot in word: ' + ''.join([l.upper() for l in not_in_word]) + '\nnot yet guessed: ' + ''.join([l.upper() for l in not_yet_guessed]) + '```'
      await message.channel.send(feedback + lives + letter_info)
  
  if won:
    await guess_msg.add_reaction('<:partyingdodo:846820422946914365>')
  else:
    await message.channel.send("The word was: " + word.upper())


if __name__ == "__main__":
  main()

# to-do: add comments explaining stuff