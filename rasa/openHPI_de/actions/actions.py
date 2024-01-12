from enum import auto
from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted
from rasa_sdk.executor import CollectingDispatcher

import requests
import json

class CourseSet(Action):
	def name(self):
		return "action_course_set"

	def run(self, dispatcher, tracker, domain):
		currentCourse = tracker.get_slot('current_course_title')
		if currentCourse:
			return [SlotSet('course-set', True)]
		else:
			return [SlotSet('course-set', False)]



class ActionGetCoursesButtons(Action):
	def name(self) -> Text:
		return "action_get_courses_buttons"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		current_state = tracker.current_state()
		token = current_state['sender_id']
		r = requests.get('https://open.hpi.de/bridges/chatbot/my_courses',
		headers={
			"content-type": "application/json",
			"Authorization": 'Bearer {0}'.format(token)
		})
		status = r.status_code
		if status == 200:
			response = json.loads(r.content)
			if len(response) < 1:
				dispatcher.utter_message("Du bist derzeit in keinem Kurs eingeschrieben.")
				return [SlotSet('courses_available', False)]
			else:
				dispatcher.utter_message("Du bist derzeit in diesen Kursen eingeschrieben:")
				courseTitle = "{0}"
				buttonGroup = []
				for course in response:
					title = course['title']
					buttonGroup.append({"title": courseTitle.format(title), "payload": '/courses{{"Course": "{0}"}}'.format(title)})
				dispatcher.utter_message(buttons = buttonGroup)
				return [SlotSet('all_courses', response), SlotSet('courses_available', True)]
		elif status == 401:  # Status-Code 401 None
			dispatcher.utter_message("Du bist derzeit in keinem Kurs eingeschrieben.")
			return [SlotSet('courses_available', False)]
		else:
			return []


class ActionGetCourses(Action):
	def name(self) -> Text:
		return "action_get_courses"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		current_state = tracker.current_state()
		token = current_state['sender_id']
		r = requests.get('https://open.hpi.de/bridges/chatbot/my_courses',
		headers={
			"content-type": "application/json",
			"Authorization": 'Bearer {0}'.format(token)
		})
		status = r.status_code
		if status == 200:
			response = json.loads(r.content)
			if len(response) < 1:
				dispatcher.utter_message("Du bist derzeit in keinem Kurs eingeschrieben.")
				return [SlotSet('courses_available', False)]
			else:
				dispatcher.utter_message("Du bist derzeit in diesen Kursen eingeschrieben:")
				courseTitle = "{0}"
				for course in response:
					title = courseTitle.format(course['title'])
					dispatcher.utter_message(title)
				return [SlotSet('all_courses', response), SlotSet('courses_available', True)]
		elif status == 401:  # Status-Code 401 None
			dispatcher.utter_message("Du bist derzeit in keinem Kurs eingeschrieben.")
			return [SlotSet('courses_available', False)]
		else:
			return []


class ActionGetAchievements(Action):
	def name(self) -> Text:
		return "action_get_achievements"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		course_achieved = False
		currentCourse = []
		courseId = 0
		currentAchievements = []
		current_state = tracker.current_state()
		token = current_state['sender_id']
		currentCourseTitle = tracker.slots['current_course_title']
		allCourses = tracker.slots['all_courses']
		for course in allCourses:
			if currentCourseTitle in course['title']:
				courseId = course['id']
				currentCourse = course
				break
		if courseId != 0:
			req_lang = "de"
			r = requests.get('https://open.hpi.de/bridges/chatbot/my_courses/{0}/achievements'.format(courseId),
			headers={
				"content-type": "application/json",
				"Authorization": 'Bearer {0}'.format(token),
				"Accept-Language": "{0}".format(req_lang)
			})
			status = r.status_code
			if status == 200:
				response = json.loads(r.content)
				currentAchievements = response['certificates']
				for achievement in currentAchievements:
					dispatcher.utter_message("{0}".format(achievement['description']))
					if achievement['achieved'] and not course_achieved:
						course_achieved = True
			return [SlotSet('current_course_achieved', course_achieved),
				SlotSet('current_course', currentCourse),
				SlotSet('current_achievements', currentAchievements),
				SlotSet('current_course_title', None)]
		else:
			dispatcher.utter_message("Es tut mir sehr leid! Ich konnte den Kurs, den du suchst, nicht finden. Bitte versuche es erneut, in dem du mir den Kurstitel nennst.")
			return[SlotSet('current_course_achieved', course_achieved), 
			SlotSet('current_course', currentCourse), 
			SlotSet('current_achievements', currentAchievements), 
			SlotSet('current_course_title', None)]


class ActionGetCertificate(Action):
	def name(self) -> Text:
		return "action_download_certificate"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		currentAchievements = tracker.slots['current_achievements']
		for achievement in currentAchievements:
			if achievement['achieved']:
				if achievement['download']['available']:
					dispatcher.utter_message("Hier kannst du {0}: { 1 } herunterladen!".format(achievement['name'], achievement['download']['url']))
				else:
					dispatcher.utter_message("Es tut mir sehr leid! Das {0} ist nicht mehr verfügbar und kann leider nicht mehr heruntergeladen werden!".format(achievement['name']))
		return []

	def name(self):
		return 'action_fallback_buttons'

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		
        # select the top two intents from the tracker        
        # ignore the first one - nlu fallback
		predicted_intents = tracker.latest_message["intent_ranking"][1:4]
		text = "Das habe ich nicht ganz verstanden. Meintest du ..."

		print(predicted_intents, text)
