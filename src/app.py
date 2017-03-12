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
  return check_unread()


@ask.launch
def check_unread():
  app.logger.info("Launch intent registered")
  unread_threads = get_unread_threads(NEW_CLIENT)
  if not unread_threads:
    return statement("You have no unread messages.")
    #      question("You have no unread messages. Would you like to write anyone?")
    #        .reprompt("Would you like to send a message?")

  response = ("You have"
              + ', '.join([(str(thread.unread_count)
                            + " unread messages in conversation "
                            + add_with(thread)
                            + get_thread_name(thread))
                           for thread in unread_threads()]))
  session.attributes['question'] = READ_MSGS
  session.attributes['read'] = []
  return (question(response + "Would you like to hear them?")
          .reprompt("Would you like to hear your unread messages?"))


@ask.intent("AMAZON.YesIntent")
def yes_intent():
  app.logger.info("Launch intent registered")
  if 'question' in session.attributes:
    if session.attributes['question'] == READ_MSGS:
      return read_msgs_intent()


@ask.intent("AMAZON.NoIntent")
def no_intent():
  app.logger.info("Launch intent registered")
  return session_end()


@ask.intent("ReadMsgsIntent")
def read_msgs_intent():
  app.logger.info("Read intent registered")

  unread_threads = filter(lambda thread: thread.thread_id not in session.attributes['read'],
                          get_unread_threads())

  response = []
  for thread in unread_threads:
    response.append("In conversation " + add_with(thread) + "."
                    + ". ".join(get_unread_msgs(thread) + "."))
    session.attributes['read'].append(thread.thread_id)
  if response:
    return statement(response)
  else:
    return statement("You have no unread messages.")


@ask.session_ended
def session_end():
  return statement("Bye, bye!")


if __name__ == "__main__":
  app.run(debug=True)