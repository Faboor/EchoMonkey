from unidecode import unidecode as udc
from itertools import chain

# Session States
READ_MSGS = 0
REPLY_CONTINUE = 1

# Flags
NEW_CLIENT = True


def polish(s):
  return udc(s).replace('&', ' and ') \
               .replace('"', '') \
               .replace('','')


def clean_fbid(fbid_string):
  return fbid_string[5:]  # 'fbid:0123456' -> '0123456'


def add_with(thread):
  return "with " if thread.thread_type == 1 else ""


def is_user_msg(msg):
  return msg.action_type == "ma-type:user-generated-message"


def empty_generator(gen):
  try:
    first = next(gen)
  except StopIteration:
    return True, gen
  return False, chain([first], gen)
