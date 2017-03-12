from flask import Flask
from flask_ask import Ask, statement, question, session
from messenger import *

app = Flask(__name__)
ask = Ask(app, "/messenger/")


@app.route('/')
def homepage():
  app.logger.info("homepage served")
  return "Get Off My Lawn"


@ask.on_session_started
def session_start():
  app.logger.debug("session start")
  return launch()


@ask.launch
def launch():
    app.logger.info("LaunchRequest registered")
    return check_unread()


def check_unread():
  if not login():
    return statement("I was unable to log you in. Please check your username and password configuration.")
  unread_threads = get_unread_threads()

  app.logger.debug("unread_threads retrieved")
  no_unread, unread_threads = empty_generator(unread_threads)
  if no_unread:
    return statement("You have no unread messages.")
    #      question("You have no unread messages. Would you like to write anyone?")
    #        .reprompt("Would you like to send a message?")

  response = ("You have "
              + ', '.join([(str(thread.unread_count)
                            + " unread messages in conversation "
                            + add_with(thread)
                            + get_thread_name(thread))
                           for thread in unread_threads])
              + ". ")
  app.logger.debug("response built")
  session.attributes['question'] = READ_MSGS
  session.attributes['read'] = []
  return (question(response + "Would you like to hear them?")
          .reprompt("Would you like to hear your unread messages?"))


@ask.intent("AMAZON.YesIntent")
def yes_intent():
  app.logger.info("YesIntent registered")
  if 'question' in session.attributes:
    if session.attributes['question'] == READ_MSGS:
      app.logger.info("Interpreted as ReadIntent")
      return read_msgs_intent()


@ask.intent("AMAZON.NoIntent")
def no_intent():
  app.logger.info("NoIntent registered")
  return session_end()


@ask.intent("ReadMsgsIntent")
def read_msgs_intent():
  app.logger.info("ReadIntent registered")

  unread_threads = filter(lambda thread: thread.thread_id not in session.attributes['read'],
                          get_unread_threads())

  empty, unread_threads = empty_generator(unread_threads)
  if empty:
    return statement("You have no more unread messages.")

  thread = next(unread_threads)
  response = ("In conversation " + add_with(thread)
              + get_thread_name(thread) + ". "
              + ". ".join(get_unread_msgs(thread)) + ".")

  session.attributes['read'].append(thread.thread_fbid)
  session.attributes['question'] = REPLY_CONTINUE
  return (question(response + "Would you like to reply or continue?")
          .reprompt("Alternatively, you can just mark as read and move on."))


@ask.intent("RepeatIntent")
def repeat_intent():
  dump = session.attributes['read'].pop(-1)
  return read_msgs_intent()


@ask.intent("ResetIntent")
def reset_intent():
  session.attributes['read'] = []
  return check_unread()


@ask.intent("MarkIntent")
def mark_intent():
  mark_read(client.markAsRead(session.attributes['read'][-1]))
  return read_msgs_intent()


@ask.intent("ReplyIntent", mapping={'msg': 'Message'})
def reply_intent(msg):
  if not msg or len(msg) == 0:
    return question("Sorry, what is your message?").reprompt("Could you repeat your message?")
  if send_msg(msg, session.attributes['read'][-1]):
    session.attributes['question'] = READ_MSGS
    return (question("Message: " + msg + ", was sent successfully. "
                     + "Would you like me to continue reading unread messages?")
            .reprompt("Would you like me to continue reading unread messages?"))
  return statement("I did something wrong, I am sorry")


#@ask.intent(AMAZON.)


@ask.session_ended
def session_end():
  return statement("Bye, bye!")


if __name__ == "__main__":
  app.run(debug=True)
