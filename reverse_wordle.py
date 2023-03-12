import random

async def main(message, client, args):
  WORD_LEN = 5  # default
  guesses = []
  grades = []

  # set word length, if specified
  if len(args) > 0:
    try:
      WORD_LEN = int(args[0])
    except ValueError:
      await message.channel.send("Make sure the word length is a number.")
      # to-do: word_len must be between 1 and 20
  
  # create a list of words with WORD_LEN letters & choose one randomly
  with open("english_words.txt") as english_words:
    words = [line.rstrip('\n') for line in english_words if len(line.rstrip('\n')) == WORD_LEN]
  answer = random.choice(words)
  possible_answers = words

  def grade_guess(guess: str, answer: str):
    grade = [0] * WORD_LEN

    letter_occurrences = {}
    for letter in answer:
      if letter not in letter_occurrences.keys():
        letter_occurrences[letter] = answer.count(letter)

    for i in range(WORD_LEN):
      if guess[i] == answer[i]:
        grade[i] = 2
        letter_occurrences[answer[i]] -= 1
    for i in range(WORD_LEN):
      try:
        if letter_occurrences[guess[i]] > 0 and grade[i] != 2:
          grade[i] = 1
          letter_occurrences[guess[i]] -= 1
      except KeyError:
        pass

    return grade

  def uses_all_info(test_word: str, guess: str, grade: list):
    for i in range(WORD_LEN):
      if grade[i] == 2:
        return guess[i] == test_word[i]
      elif grade[i] == 1:
        return guess[i] in test_word and guess[i] != test_word[i]
      else:  # grade[i] == 0
        return guess[i] not in test_word

  def emojify(line):    
    string = ""
    if type(line) == str:
      for letter in string:
        string += ":regional_indicator_" + letter.lower() + ": "
    elif type(line) == list:
      for num in list:
        if num == 0:
          string += '⬛ '
        elif num == 1:
          string += '🟨 '
        elif num == 2:
          string += '🟩 '
    return string
          
  guess = random.choice(possible_answers)
  while guess != answer:
    grade = grade_guess(guess, answer)
    guesses.append(guess)
    grades.append(grade)
    for word in possible_answers:
      if not uses_all_info(word, guess, answer):
        possible_answers.remove(word)
    guess = random.choice(possible_answers)
  guesses.append(answer)
  grades.append(['🟩'] * WORD_LEN)

  output = ""
  for i in range(len(guesses)):
    output += emojify(grades[i]) + '\n'
    output += emojify(guesses[i]) + '\n'
  await message.channel.send(output)
  
  
  # register a guess when it's in the same channel, by the same author, and a valid word
  def check(m):
    return m.channel == message.channel and m.author == message.author and len(m.content) == WORD_LEN


if __name__ == "__main__":
  main()
