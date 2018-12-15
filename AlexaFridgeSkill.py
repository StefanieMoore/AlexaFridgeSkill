from datetime import datetime
import copy

fileName = '/tmp/fridge.txt'
foods = {'Turkey': '12/01/2018', 'spaghetti': '12/02/2018', 'yogurt': '11/29/2018', 'chicken': '12/08/2018',
         'cake': '12/06/2018', 'soup': '12/07/2018', 'milk': '12/01/2018'}
CardTitlePrefix = "My Fridge"  # this is what will show up on the title for the Alexa user interface when using the skill


# code for the build responses and event handlers was borrowed from the following tutorial blueprint:
# http://www.auctoris.co.uk/2017/04/21/simple-python-hello-world-with-alexa/
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """
    Build a speechlet JSON representation of the title, output text,
    reprompt text & end of session
    """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': CardTitlePrefix + " - " + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    """
    Build the full response JSON from the speechlet response
    """
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

# function that is called on_launch when the user says the skill's invocation name, "my fridge."
def get_welcome_response():
    session_attributes = copy.deepcopy(foods)
    print("session attributes: \n")
    for attribute in session_attributes.keys():
        print(attribute + ":" + session_attributes.get(attribute))
    card_title = "Hello"
    speech_output = "Your fridge is open...Ask me what's in your fridge or how old the food is.."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should ask me what's in your fridge or how old a food is..."
    should_end_session = False
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# function that is called during SessionEndRequest, but is not currently being used
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# function that is called on_launch and reads food:date from a file into a dictionary
def open_fridge():
    print("Opening " + fileName)
    with open(fileName, 'w+') as f:
        for f_contents in f.readlines():
            fridge_item = f_contents.split(":")
            if fridge_item.__len__() == 2:
                food = fridge_item[0]
                date = fridge_item[1]
                formatted_date = date.rstrip()
                foods.update({food: formatted_date})
    print("Loaded the following foods from " + fileName + "\n")
    for food in foods:
        print(food + ": " + str(foods.get(food)) + "\n")


# function that reads from foods dictionary into dictionary session_attributes and outputs the contents.
def whats_in_fridge():
    session_attributes = copy.deepcopy(foods)
    card_title = "Fridge Contents"
    speech_output = ""
    print("number of foods: " + str(len(foods)))
    if len(foods) == 0:
        speech_output = "Your fridge is empty. Would you like to add some food?"
    elif len(foods) >= 1:
        speech_output = "Your fridge has "
        for food in foods.keys():
            speech_output += food + ", "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should ask me what's in your fridge or how old a food is..."
    should_end_session = False
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# function that modifies the contents of foods dictionary and copies to session_attributes dictionary, when the user adds a food to their fridge
def put_food_in(food, date):
    foods.update({food: date})
    session_attributes = copy.deepcopy(foods)
    card_title = "Put Food In"
    speech_output = "Okay, I have added the " + food + " to your fridge...Is there anything else I can help you with?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should ask me what's in your fridge or how old a food is..."
    should_end_session = False
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# function that modifies the contents of foods dictionary and copies to session_attributes dictionary, when user removes a food item
def take_food_out(food):
    if food in foods:
        del foods[food]
        speech_output = "Okay, I have removed the " + food + " from your fridge."
    else:
        speech_output = "You don't have any " + food + " in your fridge...Perhaps I misunderstood?"
    session_attributes = copy.deepcopy(foods)
    card_title = "Take Food Out"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should ask me what's in your fridge or how old a food is..."
    should_end_session = False
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# this function outputs the age of the food in days
def how_old(food):
    card_title = "Food Age"
    if food in foods:  # first verify the food is in the fridge
        today = datetime.now()  # variable created to store current date
        day_added = datetime.strptime(foods.get(food), "%m/%d/%Y")  # variable created to store date when food was added
        delta_days = today - day_added  # calculates days since food was added
        age = str(delta_days.days)  # stores age of the food into string variable
        if delta_days.days == 0:  # food stored today
            speech_output = "The " + food + " was stored today. "
        else:
            if (delta_days.days <= 7):  # food is fresh
                speech_output = "The " + food + " is " + age + " days old."
            else:  # else yuck, the food is old
                speech_output = "The " + food + " is " + age + " days old. That might not be safe to eat. I recommend you throw it away."
    else:
        speech_output = "You do not have any " + food + " stored in your fridge...Perhaps I misunderstood?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should ask me what's in your fridge or how old a food is..."
    should_end_session = False
    session_attributes = copy.deepcopy(foods)
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# this function updates the file with any changes made to the foods dictionary during the program, and also ends the session when called
def close_fridge():
    with open(fileName, 'w+') as f:
        for food, date in foods.items():
            print(str(food) + ":" + str(date) + "\n")
            f.write(str(food) + ":" + str(date) + "\n")
    session_attributes = {}
    card_title = "Close Fridge"
    speech_output = "Okay, your fridge is closed...Have a nice day!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should ask me what's in your fridge or how old a food is..."
    should_end_session = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    open_fridge()
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent_name = intent_request['intent']['name']
    if 'sessionAttributes' in session:
        foods = copy.deepcopy(session['sessionAttributes'])
    # Dispatch to the skill's intent handlers
    if intent_name == "how_old":
        food = intent_request['intent']['slots']['food']['value']
        return how_old(food)
    elif intent_name == "whats_in_fridge":
        return whats_in_fridge()
    elif intent_name == "put_food_in":
        date = datetime.strftime(datetime.today(), "%m/%d/%Y")
        food = intent_request['intent']['slots']['food']['value']
        return put_food_in(food, date)
    elif intent_name == "take_food_out":
        food = intent_request['intent']['slots']['food']['value']
        return take_food_out(food)
    elif intent_name == "close_fridge":
        return close_fridge()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session. Is not called when the skill returns should_end_session=true """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'],
                                event['session'])