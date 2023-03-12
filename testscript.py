async def main(message, client):
  await message.channel.send('type something')
  msg = await client.wait_for('message')
  await message.channel.send('{.content}!'.format(msg))

if __name__ == "__main__":
  main()