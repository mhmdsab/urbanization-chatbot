# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



import random
import rasa_sdk
import requests

from rasa_sdk.types import DomainDict
from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, EventType, ActionExecuted


#simple actions
class Action_greet(Action):
    def __init__(self):
        self.answers = ["Hi, I am your smart assistant. \nI can help you finding the capital and population of different countries",
                        "Hi there, I hope you are doing great!, How can I help you"]

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=random.choice(self.answers))

        return []

class Action_goodbye(Action):
    def __init__(self):
        self.answers = ["See you soon",
                        "Goodbye friend",
                        "I enjoyed chatting with you, see you soon"]

    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=random.choice(self.answers))

        return []

class Action_default_fallback(Action):
    def __init__(self):
        self.answers = ["Sorry, I did not understand you. I am still learning",
                        "It seems I did not get exactly what you mean, please rephrase"]

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        counter = 0
        tracker_intents = []
        events = tracker.events
        
        for i in range(len(events)-1, -1, -1):
            if events[i].get("event") == "user":
                counter+=1
                tracker_intents.append(events[i]["parse_data"].get("intent")["name"])
                if counter>=3:
                    break

        tracker_intents = list(set(tracker_intents))

        if len(tracker_intents)==1:
            text = "It seems I failed to understand what you need, but I can help you with the following"
            buttons = [
                        {
                            "title": "Check Capital" , 
                            "payload": "Check Capital"
                        },
                        {
                            "title": "Check Population" , 
                            "payload": "Check Population"
                        }
            ]

            dispatcher.utter_message(text=text, buttons=buttons)
        
        else:
            dispatcher.utter_message(text=random.choice(self.answers))

        return []


#capital form actions
class AskForSlot_capital_slot(rasa_sdk.Action):
    def name(self) -> Text:
        return "action_ask_capital_slot"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        returned_events = []

        if tracker.get_slot("form_validated"):
            text = "It seems you entered invalid country, please select from the following."
            returned_events.append(SlotSet("form_validated", None))
            
        else:
            text = "I can get the capital of the following countries. Please select one."

        buttons = [
                        {
                            "title": "USA" , 
                            "payload": "USA"
                        },
                        {
                            "title": "Greece" , 
                            "payload": "Greece"
                        },
                        {
                            "title": "Sweden" , 
                            "payload": "Sweden"
                        },
                        {
                            "title": "Australia" , 
                            "payload": "Australia"
                        },
                        {
                            "title": "Finland" , 
                            "payload": "Finland"
                        },
                        {
                            "title": "Japan" , 
                            "payload": "Japan"
                        },
                        {
                            "title": "Russia" , 
                            "payload": "Russia"
                        },
                        {
                            "title": "India" , 
                            "payload": "India"
                        }
                ]

        dispatcher.utter_message(text = text, buttons = buttons)
        return returned_events

class Validate_check_capital_form(FormValidationAction):
    def name(self) -> Text:
        return "validate_check_capital_form"

    def validate_capital_slot(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate capital slot value."""
        # message_intent = tracker.get_intent_of_latest_message(skip_fallback_intent=False)
        try:
            countries_list = requests.get("https://qcooc59re3.execute-api.us-east-1.amazonaws.com/dev/getCountries").json()
        except:
            countries_list = None

        country = next(tracker.get_latest_entity_values("country"), None)

        if country:
            return {"capital_slot": country.capitalize()}

        elif countries_list:
            if countries_list["success"] == "1":
                if slot_value.lower() in [x.lower() for x in countries_list["body"]]:
                    return {"capital_slot": slot_value.capitalize()}
                
                else:
                    return {"capital_slot": None,
                            "form_validated":"form_validated"}
            
            else:
                manual_countries_list = ["usa","greece","sweden","australia","finland","japan","russia","india"]
                if slot_value.lower() in manual_countries_list:
                    return {"capital_slot": slot_value.capitalize()}

                else:
                    return {"capital_slot": None,
                            "form_validated":"form_validated"}

        else:
            return {"capital_slot": None,
                    "form_validated":"form_validated"}
        
class Action_action_submit_check_capital_form(Action):
    def name(self) -> Text:
        return "action_submit_check_capital_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        returned_events = [SlotSet("capital_slot", None)]
        country = tracker.get_slot("capital_slot").capitalize()
        if country=="Usa":
            country = "USA"
        try:
            requested_capital = requests.post("https://qcooc59re3.execute-api.us-east-1.amazonaws.com/dev/getCapital", 
                                              json = {"country": country}, timeout=5).json()
            text = "The capital of {} is {}".format(country, requested_capital["body"]["capital"])
        except:
            text = "It seems I am currently not able to provide the capital of {}, please try again later".format(country)

        dispatcher.utter_message(text = text)
        return returned_events


#population form actions
class AskForSlot_population_slot(rasa_sdk.Action):
    def name(self) -> Text:
        return "action_ask_population_slot"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        returned_events = []

        if tracker.get_slot("form_validated"):
            text = "It seems you entered invalid country, please select from the following."
            returned_events.append(SlotSet("form_validated", None))

        else:
            text = "I can get the population of the following countries. Please select one."

        buttons = [
                        {
                            "title": "USA" , 
                            "payload": "USA"
                        },
                        {
                            "title": "Greece" , 
                            "payload": "Greece"
                        },
                        {
                            "title": "Sweden" , 
                            "payload": "Sweden"
                        },
                        {
                            "title": "Australia" , 
                            "payload": "Australia"
                        },
                        {
                            "title": "Finland" , 
                            "payload": "Finland"
                        },
                        {
                            "title": "Japan" , 
                            "payload": "Japan"
                        },
                        {
                            "title": "Russia" , 
                            "payload": "Russia"
                        },
                        {
                            "title": "India" , 
                            "payload": "India"
                        }
                ]

        dispatcher.utter_message(text = text, buttons = buttons)
        return returned_events

class Validate_check_population_form(FormValidationAction):
    def name(self) -> Text:
        return "validate_check_population_form"

    def validate_population_slot(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate population slot value."""

        try:
            countries_list = requests.get("https://qcooc59re3.execute-api.us-east-1.amazonaws.com/dev/getCountries").json()
        except:
            countries_list = None

        country = next(tracker.get_latest_entity_values("country"), None)

        if country:
            return {"population_slot": country.capitalize()}

        elif countries_list:
            if countries_list["success"] == "1":
                if slot_value.lower() in [x.lower() for x in countries_list["body"]]:
                    return {"population_slot": slot_value.capitalize()}
                
                else:
                    return {"population_slot": None,
                            "form_validated":"form_validated"}
            
            else:
                manual_countries_list = ["USA","Greece","Sweden","Australia","Finland","Japan","Russia","India"]
                if slot_value.capitalize() in manual_countries_list:
                    return {"population_slot": slot_value.capitalize()}

                else:
                    return {"population_slot": None,
                            "form_validated":"form_validated"}

        else:
            return {"population_slot": None,
                    "form_validated":"form_validated"}

class Action_action_submit_check_population_form(Action):
    def name(self) -> Text:
        return "action_submit_check_population_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        returned_events = [SlotSet("population_slot", None)]
        country = tracker.get_slot("population_slot").capitalize()
        if country=="Usa":
            country = "USA"

        try:
            requested_population = requests.post("https://qcooc59re3.execute-api.us-east-1.amazonaws.com/dev/getPopulation", 
                                                json = {"country": country}, timeout=5).json()

            text = "The population of {} is {}".format(country, requested_population["body"]["population"])
        except Exception as e:
            text = "It seems I currently not able to provide the population of {}, please try again later".format(country)

        dispatcher.utter_message(text = text)
        return returned_events








