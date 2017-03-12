import fbchat as fb
from config import *
from utils import *


class Client(fb.Client):
  def markAsRead(self, userID):
    data = {"ids[%s]" % userID: 'true'}
    r = self._post(fb.client.ReadStatusURL, data)
    return r.ok


client = None


def get_unread_threads(new_client=False):
  global client
  if new_client:
    client = Client(USERNAME, PASSWORD, debug=DEBUG, max_retries=LOGIN_RETRIES)

  for thread in client.getThreadList(0):
    if not thread.mute_until and thread.unread_count:
      yield thread


def get_unread_msgs(thread):
  is_group = thread.thread_type == 2
  msgs = client.getThreadInfo(thread.thread_fbid, 0,
                              end=thread.unread_count - 1,
                              thread_type='group' if is_group else 'user')
  messages = []
  if is_group:
    last_poster = None
    for msg in reversed(msgs):
      message = ""
      if is_user_msg(msg):
        if msg.author != last_poster:
          last_poster = msg.author
          message += polish(msg.author) + " said: "
        message += msg.body + ("." if not msg.has_attachment else ". This message has an attachment.")
      else:
        message = msg.log_message_body
      messages.append(message)
  else:
    for msg in reversed(msgs):
      if is_user_msg(msg):
        message = msg.body + ("." if not msg.has_attachment else ". This message has an attachment.")
      else:
        message = msg.log_message_body
      messages.append(message)
  return messages


def get_thread_name(thread):
  if thread.name:
    return polish(thread.name)

  members = []  # Names
  for member_uid in map(lambda fbid: int(clean_fbid(fbid)),
                        thread.participants):
    if member_uid != client.uid:
      members.append(get_user_name(member_uid))

  if len(members) == 1:
    return members[0]

  return ', '.join(members[:-1]) + ' and ' + members[-1]  # Names already polished


def get_user_name(uid):
  return polish(client.getUserInfo(uid)['name'])
