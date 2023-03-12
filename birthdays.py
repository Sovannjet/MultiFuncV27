import re
import os

all_bdays = {}
SEP = '/'
FORMAT = "Command format:\n```i'm too lazy rn```"


async def main(message, client, args):
  try:
    bdays = all_bdays[message.guild]
    
    if len(args) == 0:
      bday_list = to_string(bdays, "{}: {}\n")
      if len(bdays) > 0:
        await message.channel.send(bday_list)
      else:
        await message.channel.send("This server's birthday list is empty. You can add a birthday with `[bd add @user date`.")
    
    elif len(args) == 1 and is_user(args[0]):
      user = message.mentions[0]
      await message.channel.send("{}'s birthday: {}".format(user.mention, bdays[user]))
    
    elif len(args) == 2 and args[0] in ('remove', 'rmv', 'r', 'delete', 'del', 'd', '-') and is_user(args[1]):
      user = message.mentions[0]
      try:
        del bdays[user]
        await message.add_reaction('✅')
        # if len(bdays) > 0:
          # await message.guild.fetch_member(os.environ['vari_id']).create_dm().send(to_string(bdays, "[bd add {} {}\n"))
      except KeyError:
        await message.channel.send("{}'s birthday is not in the list.".format(user.mention))
    
    elif len(args) == 3 and args[0] in ('add', 'a', '+', 'update', 'u', 'change', 'c', 'modify', 'mod', 'm'):
      ud = is_user(args[1]) and is_date(args[2])
      du = is_date(args[1]) and is_user(args[2])
      if ud or du:
        user = message.mentions[0]
        if ud:
          bday = format_date(args[2])
        elif du:
          bday = format_date(args[1])
        bdays[user] = bday
        await message.channel.send("✅ {}'s birthday added as {}.".format(user.mention, bday))
        # if len(bdays) > 0:
          # await message.guild.fetch_member(os.environ['vari_id']).create_dm().send(to_string(bdays, "[bd add {} {}\n"))
      
      else:
        await message.channel.send(FORMAT)
    else:
      await message.channel.send(FORMAT)
  
  except KeyError:  # server doesn't have a bday dict yet
    bdays = all_bdays[message.guild] = {}
    await message.channel.send("This server didn't have a birthday list... until now. You can now add a birthday with `[bd add @user date`.")


def is_user(string: str):
  return re.match('<@!?[0-9]{18}>', string) is not None


def is_date(string: str):
  return format_date(string) is not None  


def format_date(string: str):
  date = string.replace('-', '/').replace('.', '/').split('/')
  try:
    date = [int(num) for num in date]
  except ValueError:
    return None
  
  days = range(1, 32)
  months = range(1, 13)
  d = m = y = None
  
  if len(date) == 2:
    if date[0] in months and date[1] in days:  # MD (American) format
      m, d = date[0], date[1]
    elif date[0] in days and date[1] in months:  # DM (European) format
      d, m = date[0], date[1]
    else:
      return None
  elif len(date) == 3:
    if date[0] in months and date[1] in days:  # MDY (American) format
      m, d, y = date[0], date[1], date[2]
    elif date[0] in days and date[1] in months:  # DMY (European) format
      d, m, y = date[0], date[1], date[2]
    elif date[1] in months and date[2] in days:  # YMD (Chinese) format
      y, m, d = date[0], date[1], date[2]
    else:
      return None
  else:
    return None

  if y is None:
    return str(m) + SEP + str(d)
  else:
    return str(m) + SEP + str(d) + SEP + str(y).zfill(2)


def to_string(bdays: dict, format: str):
  bday_list = ""
  for user in sorted(bdays, key=lambda user: bdays[user]):
    bday_list += format.format(user.mention, bdays[user])
  return bday_list


if __name__ == "__main__":
  main()


# comments
# command format
# sending dm