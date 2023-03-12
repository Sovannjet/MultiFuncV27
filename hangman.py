import random
import re

async def main(message, client, cmd):
  english_words = open("english_words.txt").readlines()
  english_letters = {chr(i) for i in range(97, 123)}  # lowercase letters

  ### INITIALIZE THE SETTINGS BASED ON THE COMMAND'S PARAMETERS ###
  word = ""
  word_by_user = False
  category = ""
  turns = 10

  spoiler1_index = cmd.find("||")
  c_index = -1
  t_index = -1
  c_tag = "category:"
  t_tag = "turns:"

  flags = re.findall('c(?:ategory)?[:;]', cmd)  # matches category:, category;, c:, or c;
  if len(flags) > 0:
    c_tag = flags[0]
    c_index = cmd.find(flags[0])
  flags = re.findall('t(?:urns)?[:;]', cmd)  # matches turns:, turns;, t:, or t;
  if len(flags) > 0:
    t_tag = flags[0]
    t_index = cmd.find(t_tag)
  flags = [spoiler1_index, c_index, t_index]
  flags.sort()

  # isolate word
  if spoiler1_index >= 0:
    word = cmd[spoiler1_index + 2 :]  # from after spoiler1 onward
    spoiler2_index = word.find("||")
    if spoiler2_index >= 0:
      word = word[: spoiler2_index].strip()  # assign word to variable
      word_by_user = True

      # check for category (only if there is a spoilered word)
      if c_index >= 0:
        start = c_index + len(c_tag)
        try:
          end = flags[flags.index(c_index) + 1]
        except IndexError:
          end = len(cmd)
        category = cmd[start:end].strip()
  
  else: # no spoilered-word parameter
    word = random.choice(english_words).rstrip('\n')
  
  # check for turns
  if t_index >= 0:
    start = t_index + len(t_tag)
    try:
      end = flags[flags.index(t_index) + 1]
    except IndexError:
      end = len(cmd)
    try:
      turns = int(cmd[start:end].strip())
    except ValueError:
      await message.channel.send("Your number of turns isn't a number; turns defaulted to 10.")
  
  

  ### PREPARE THE LISTS AND DEFINE PRINTBLANKS() ###
  record = []
  wrongguesses = []
  remainingguesses = turns

  # fill the record with blanks and, if needed, special characters
  for i in range(len(word)):
    if word[i] in english_letters:
      record.append("_")
    else:
      record.append(word[i].upper())

  async def printblanks():
    display = "```\n"  # open code block formatting

    # print category if needed
    if len(category) > 0:
      display += "Category: " + category + "\n\n"

    # print blanks
    wordslist = "".join(record).split()
    currlinelen = 0
    for i in range(len(wordslist)):
      if i > 0 and currlinelen + len(wordslist[i]) > 10:  # wrap text if a line that isn't the first line will be longer than 10 letters
        display += "\n"
        currlinelen = 0
      display += " ".join(wordslist[i]) + "   "  # add word, with appropriate spacing, to display
      currlinelen += len(wordslist[i])
    display += "\n"

    # print letters already guessed
    if len(wrongguesses) > 0:
      display += "\nAlready guessed: "
      for i in range(len(wrongguesses)):
        display += wrongguesses[i]
        if i < len(wrongguesses)-1:
          display += ", "

    # print tries left
    if remainingguesses == 1:
      display += "\n" + str(remainingguesses) + " try left."
    else:
      display += "\n" + str(remainingguesses) + " tries left."
    
    display += "\n```"  # close code block formatting
    await message.channel.send(display)



  ### PLAY THE GAME ###
  await message.channel.send("Hangman game started!")
  await printblanks()

  while "_" in record and remainingguesses > 0:
    def check(m):
      # only accept guesses from a user that made a word if it's in Bot Testing
      if word_by_user and message.guild.name != 'Bot Testing' and m.author == message.author:
        return False
      msg = m.content.lower()
      return m.channel == message.channel and (msg == word or (len(msg) == 1 and msg in english_letters))

    guess = await client.wait_for('message', check=check)
    guess = guess.content.lower()
    
    # check guess
    if guess in wrongguesses or guess.upper() in record:
      await message.channel.send("That has already been guessed.")
    else:
      if len(guess) > 1:  # if true, the guess must be the correct word
        for i in range(len(word)):
          record[i] = word[i].upper()
      else:
        if guess in word:
          for i in range(len(word)):
            if guess == word[i]:
              record[i] = word[i].upper()
        else:
          wrongguesses.append(guess)
          remainingguesses -= 1
      
      await printblanks()

  if "_" not in record:
    await message.channel.send("Correct!")
  else:
    await message.channel.send("The word/phrase was: " + word)



if __name__ == "__main__":
  main()
