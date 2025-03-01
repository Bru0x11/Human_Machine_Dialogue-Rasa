import logging
import json
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Optional, List, Dict, Any

from rasa.core.channels.channel import UserMessage, OutputChannel
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import CollectingOutputChannel

logger = logging.getLogger(__name__)


class AlexaConnector(InputChannel):
    """A custom http input channel for Alexa.
    You can find more information on custom connectors in the 
    Rasa docs: https://rasa.com/docs/rasa/user-guide/connectors/custom-connectors/
    """

    @classmethod
    def name(cls):
        return "alexa_assistant"

    # Sanic blueprint for handling input. The on_new_message
    # function pass the received message to Rasa Core
    # after you have parsed it
    def blueprint(self, on_new_message):

        alexa_webhook = Blueprint("alexa_webhook", __name__)

        # required route: use to check if connector is live
        @alexa_webhook.route("/", methods=["GET"])
        async def health(request):
            return response.json({"status": "ok"})

        # required route: defines
        @alexa_webhook.route("/webhook", methods=["POST"])
        async def receive(request):
            # get the json request sent by Alexa
            payload = request.json
            # check to see if the user is trying to launch the skill
            intenttype = payload["request"]["type"]

            # if the user is starting the skill, let them know it worked & what to do next
            if intenttype == "LaunchRequest":
                message = "Hello! Welcome to this Rasa-powered Alexa skill. You can start by saying 'hi'."
                session = "false"
            else:
                # get the Alexa-detected intent
                intent = payload["request"]["intent"]["name"]
        
                # makes sure the user isn't trying to end the skill
                if intent == "AMAZON.StopIntent":
                    session = "true"
                    message = "Talk to you later"
                elif intent == "AMAZON.FallbackIntent":
                    session = "false"
                    message = "I'm sorry I did not understand what you said"
                else:
                    # get the user-provided text from the slot named "text"
                    text = payload["request"]["intent"]["slots"]["text"]["value"]
                    print(text)
                    # initialize output channel
                    out = CollectingOutputChannel()
                    
                    # send the user message to Rasa & wait for the
                    # response to be sent back
                    await on_new_message(UserMessage(text, out))
                    # extract the text from Rasa's response
                    responses = [m["text"] for m in out.messages]
                    message = ' '.join(responses)
                    #message = responses[0]
                    print(message)
                    session = "false"
            # Send the response generated by Rasa back to Alexa to
            # pass on to the user. For more information, refer to the
            # Alexa Skills Kit Request and Response JSON Reference:
            # https://developer.amazon.com/en-US/docs/alexa/custom-skills/request-and-response-json-reference.html
            r = {
                "version": "1.0",
                "sessionAttributes": {"status": "test"},
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": message,
                        "playBehavior": "REPLACE_ENQUEUED",
                    },
                    "reprompt": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": message,
                            "playBehavior": "REPLACE_ENQUEUED",
                        }
                    },
                    "shouldEndSession": session,
                },
            }

            return response.json(r)

        return alexa_webhook