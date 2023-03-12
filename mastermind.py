import random

async def main(message, client, args):
  # defaults
  CODE_LEN = 4
  TURNS = 10

  
  async def play():
    # make code & start game
    digits = [str(n+1) for n in range(6)]
    code = ""
    for x in range(CODE_LEN):
      rd = random.choice(digits)
      code += str(rd)
      digits.remove(rd)
    digits = [str(n+1) for n in range(6)]  # reset digits
    await message.channel.send("The " + str(CODE_LEN) + "-digit code has been made!\nThe options for digits are 1, 2, 3, 4, 5, and 6.\n'x' represents a correct number and location; 'o' represents a correct number; '-' represents an incorrect number.\nYou get " + str(TURNS) + " guesses.")
  
    # run through 10 trials
    record = "{.author.display_name}'s mastermind game\n".format(message)
    trialnum = 1
    correct = False
    while trialnum <= TURNS and correct is False:
      def onlyNums(msg):
        if msg.channel == message.channel and msg.author == message.author:
          try: 
            int(msg.content.replace(" ", ""))  # remove spaces, then check if msg only contains numbers
          except:
            return False
          return True
            
      await message.channel.send("{.author.mention} Input guess #".format(message) + str(trialnum) + ": ")
      resp = await client.wait_for('message', check=onlyNums)
      guess = resp.content.replace(" ", "")  # remove spaces
  
      def hasInvalidNums():
        for i in range(CODE_LEN):
          if guess[i] not in digits:
            return True
        return False
  
      # check string for length and numbers out of range, before grading
      if len(guess) != CODE_LEN:
        await message.channel.send("Your guess should be " + str(CODE_LEN) + " digits long.")
      elif hasInvalidNums():
        await message.channel.send("Your guess should only consist of numbers 1-6.")
      else:  # grade the guess and output appropriate marks
        grade = ""
        digitsAlreadyChecked = set()
        numMarksPlaced = 0
  
        if guess == code:
          correct = True
          await message.channel.send("Correct!")
        else:
          for h in range(CODE_LEN):  # check for correct number & location
            if guess[h] == code[h]:
              grade += "x"
              numMarksPlaced += 1
              digitsAlreadyChecked.add(guess[h])
          for i in range(CODE_LEN):  # check for correct number
            if guess[i] not in digitsAlreadyChecked:
              for j in range(CODE_LEN):
                if guess[i] == code[j]:
                  grade += "o"
                  numMarksPlaced += 1
            digitsAlreadyChecked.add(guess[i])
          grade += "-" * (CODE_LEN - numMarksPlaced)
          await message.channel.send(grade)
          record += str(trialnum) + ".\t" + guess + "\t" + grade + "\n"
          await message.channel.send("```\n" + record + "```")
        
        trialnum += 1
  
    await message.channel.send("The code was: " + code + "\nThanks for playing!")

    
  # process arguments
  if len(args) > 0:
    if len(args) > 1:
      TURNS = int(args[1])
      
    CODE_LEN = int(args[0])
    if CODE_LEN > 6:
      await message.channel.send("The code length should be no greater than 6.")
      CODE_LEN = 4
    else:
      await play()
  else:
    await play()


if __name__ == "__main__":
  main()
