# (q1w*q1g + q2w*q2g + sew*seg) / 100 = finalgrade

Q1W_DEFAULT = 40
Q2W_DEFAULT = 40
SW_DEFAULT = Q1W_DEFAULT + Q2W_DEFAULT
SEW_DEFAULT = 100 - SW_DEFAULT


async def main(message, client, args):
  try:
    args = [float(arg) for arg in args]  # ValueError if there are non-numerical values
    
    seg = None  # semester exam grade needed
    if len(args) == 2:
      sg = args[0]
      goal = args[1]
      seg = (100*goal - SW_DEFAULT*sg) / SEW_DEFAULT
    elif len(args) == 3:
      q1g = args[0]
      q2g = args[1]
      goal = args[2]
      seg = (100*goal - Q1W_DEFAULT*q1g - Q2W_DEFAULT*q2g) / SEW_DEFAULT
    elif len(args) == 4:
      sw = args[0]
      sg = args[1]
      sew = args[2]
      goal = args[3]
      seg = (100*goal - sw*sg) / sew
    elif len(args) == 6:
      q1w = args[0]
      q1g = args[1]
      q2w = args[2]
      q2g = args[3]
      sew = args[4]
      goal = args[5]
      seg = (100*goal - q1w*q1g - q2w*q2g) / sew
    else:
      await send_err_message(message)

    if seg is not None:
      await message.channel.send("You need " + str(seg) + "% on the semester exam to get a final grade of " + str(goal) + "%.")

  except ValueError:
    await send_err_message(message)


async def send_err_message(msg):
  await msg.channel.send("Enter 2, 3, 4, or 6 numbers after the command.")
  await msg.channel.send("Command format:\n`[semexam sem-grade goal`\n`[semexam q1-grade q2-grade goal`\n`[semexam sem-weight sem-grade exam-weight goal`\n`[semexam q1-weight q1-grade q2-weight q2-grade exam-weight goal`")


if __name__ == "__main__":
  main()