import module
import tutor
import ReaderWriter
import timetable
import random
import math

class Scheduler:



	def __init__(self,tutorList, moduleList):
		self.tutorList = tutorList
		self.moduleList = moduleList
		self.weekDay = 0
		self.slotNumber = 0

		self.qwertyList = list()
		self.qwertyList1 = list()
		self.qwertyList2 = list()
		self.tempTimeTable = [[] for i in range(5)]

		self.tutorCreditCount = dict()
		self.tutorAssignedCount = dict()
		self.tutorAssignedCount1 = dict()
		for x in self.tutorList:
			self.tutorAssignedCount[x.name] = 0
		for y in self.tutorList:
			self.tutorAssignedCount1[y.name] = 4
		for z in self.tutorList:
			self.tutorCreditCount[z.name] = [0, 0, 0, 0, 0]

	#This function checks if the tutor can teach the particular module or Lab
	def canTeach(self, tutor, mod, isLab):
		#if its not a lab, we make sure every one of modules topics matches an expertise of the tutor
		if not isLab:
			topics = mod.topics

			i = 0
			for top in topics:
				if top not in tutor.expertise:
					#print(str(mod.name) + " module session error.")
					return False

			return True

		else:
			topics = mod.topics

			i = 0
			for top in topics:
				if top in tutor.expertise:

					return True

			#print(str(mod.name) + " lab session error.")
			return False


	#In this function for each module we go through the list of tutors and
	#check if the tutor can teach the module. We make a list of such tutors
	#who can teach this module and then store this list along with the module
	#in another list.
	def moduleTutorList(self, tutorList, moduleList):
		mtList = list()
		for module in self.moduleList:
			tempTutorList = list()
			for tutor in self.tutorList:
				if self.canTeach(tutor, module, False):
					tempTutorList.append(tutor)
			if len(tempTutorList) == 0:
				return None
			mtList.append([module, tempTutorList])
		mtList.sort(key=lambda t:len(t[1]))
		return mtList

	#Implementation is the same as moduleTutorList but instead of modules
	#we store the lab and the list of tutors who can teach it
	def labTutorList(self, tutorList, moduleList):
		ltList = list()
		for lab in self.moduleList:
			tutList = list()
			for tutor in self.tutorList:
				if self.canTeach(tutor, lab, True):
					tutList.append(tutor)
			if len(tutList) == 0:
				return None
			ltList.append([lab, tutList])
		ltList.sort(key=lambda t:len(t[1]))
		return ltList


	#In this function we go through the moduleTutorList and assign each module
	#a tutor from its list of possible tutors. A dictionary has been used to
	#make sure that the tutor doesn't teach more than 2 modules. The output
	#is a list of modules and their assigned tutor.
	def backTrackTask1(self, moduleTutorList):
		if len(moduleTutorList) == 0:
			return self.qwertyList
		for tuple in moduleTutorList:
			[module, mlist] = tuple
			for tutor in mlist:
				if module in tuple:
					if  self.tutorAssignedCount[tutor.name] < 2:
						self.tutorAssignedCount[tutor.name] = self.tutorAssignedCount[tutor.name] + 1
						moduleTutorList.pop(0)
						self.qwertyList.append([module, tutor])
						result = self.backTrackTask1(moduleTutorList)
						if result != None:
							return result
						self.tutorAssignedCount[tutor.name] = self.tutorAssignedCount[tutor.name] - 1
						moduleTutorList.insert(0, tuple)
						self.qwertyList.pop()
		return None

	#This function takes the list of modules and its assigned tutors and feeds
	#them into the time table.
	def timeTableIt(self, qwertyList, timetableObj1):
		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		qwertyList.sort(key=lambda t:t[1].name)
		for tuple in self.qwertyList:
			[module, tutor] = tuple
			timetableObj1.addSession(days[dayNumber], sessionNumber, tutor, module, "module")
			dayNumber = dayNumber + 1

			if dayNumber == 5:
				dayNumber = 0
				sessionNumber = sessionNumber + 1

	#Implementation is very similar to backTrackTask1. This function is
	#ran twice. Once with moduleTutorList and then with labTutorList.
	#The output is a list of modules or labs depending on the input list and
	#their assigned tutor.
	def backTrackTask2(self, genericList, myList, creditValue):
		if len(genericList) == 0:
			return myList
		for tuple in genericList:
			[modOrLab, list] = tuple
			for tutor in list:
				if modOrLab in tuple:
					if self.tutorAssignedCount1[tutor.name] > 0:
						self.tutorAssignedCount1[tutor.name] = self.tutorAssignedCount1[tutor.name] - creditValue
						genericList.pop(0)
						myList.append([modOrLab, tutor])
						result = self.backTrackTask2(genericList, myList, creditValue)
						if result != None:
							return result
						self.tutorAssignedCount1[tutor.name] = self.tutorAssignedCount1[tutor.name] + creditValue
						genericList.insert(0, tuple)
						myList.pop()
		return None

	#In this function we insert the respective types in each of the list.
	#Afterwards we combine both the lists and sort them by tutor name.
	#Finaly we take the final list and feed the valus into the time table.
	def timeTableThat(self, timetableObj2):
		for muple in self.qwertyList1:
			muple.append("module")
		for duple in self.qwertyList2:
			duple.append("lab")
		finalList = list()
		finalList = self.qwertyList1 + self.qwertyList2
		finalList.sort(key=lambda t:t[1].name)
		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		for tuple in finalList:
			[modOrLab, tutor, type] = tuple
			timetableObj2.addSession(days[dayNumber], sessionNumber, tutor, modOrLab, type)
			dayNumber = dayNumber + 1

			if dayNumber == 5:
				dayNumber = 0
				sessionNumber = sessionNumber + 1

	#In this function we take the list of possible tutors for each module.
	#And then based on the creditValue and the days at which the particular
	#module or lab was taught before we assign them priorities
	def tutPriority(self, tutorCredits, tutList, assignedSession, type, day):
		if type == "module" and day > 0:
			tutList.sort(key = lambda tut:tutorCredits[tut][day - 1])
			prevDay = list()
			for tuple in assignedSession[day - 1]:
				[modOrLab, tutor, type] = tuple
				if type == "module" and tutor in tutList:
					tutList.remove(tutor)
					prevDay.append(tutor)
			tutList = prevDay + tutList

		elif type == "lab":
			tut_0 = list()
			tut_1_Or_3 = list()
			tut_2 = list()
			for tutor in tutList:
				if tutorCredits[tutor.name][day] == 0:
					tut_0.append(tutor)
				elif tutorCredits[tutor.name][day] == 1:
					tut_1_Or_3.append(tutor)
				else:
					tut_2.append(tutor)
			tut_1_Or_3.sort(key = lambda tut:sum(tutorCredits[tut]), reverse = True)
			tut_0.sort(key = lambda tut:sum(tutorCredits[tut]), reverse = True)
			tutList = tut_1_Or_3 + tut_0 + tut_2
		return tutList

	#This function takes a list of modules and labs with their possible tutors.
	#For each module or lab, it takes their list of possible tutors and then
	#assigns them priority using the tutPriority function. And then based on the
	#priority, the tutors are assigned to the modules or labs which are then
	#added to the slots in the sessionAssigned list as long as none of the
	#constraints are violated.
	def backTrackTask3(self, moduleLabList, sessionAssigned):
		if len(moduleLabList) == 0:
			return sessionAssigned
		for tuple in moduleLabList:
			[modOrLab, listTut, type] = tuple
			listTut = self.tutPriority(self.tutorCreditCount, listTut, sessionAssigned, type, self.weekDay)
			for tutor in listTut:
				if self.tutorAssignedCount1[tutor.name] > 0:
					if type == "module":
						self.tutorAssignedCount1[tutor.name] = self.tutorAssignedCount1[tutor.name] - 2
						self.tutorCreditCount[tutor.name][self.weekDay] = self.tutorCreditCount[tutor.name][self.weekDay] + 2
					elif type == "lab":
						self.tutorAssignedCount1[tutor.name] = self.tutorAssignedCount1[tutor.name] - 1
						self.tutorCreditCount[tutor.name][self.weekDay] = self.tutorCreditCount[tutor.name][self.weekDay] + 1
					if self.tutorCreditCount[tutor.name][self.weekDay] < 3:
						sessionAssigned[self.weekDay].append([modOrLab, tutor, type])
						self.slotNumber = self.slotNumber + 1
						if self.slotNumber == 11:
							self.weekDay = self.weekDay + 1
							self.slotNumber = 1
						moduleLabList.pop(0)
						result = self.backTrackTask3(moduleLabList, sessionAssigned)
						if result != None:
							return result
						if type == "module":
							self.tutorAssignedCount1[tutor.name] = self.tutorAssignedCount1[tutor.name] + 2
							self.tutorCreditCount[tutor.name][self.weekDay] = self.tutorCreditCount[tutor.name][self.weekDay] - 2
						elif type == "lab":
							self.tutorAssignedCount1[tutor.name] = self.tutorAssignedCount1[tutor.name] + 1
							self.tutorCreditCount[tutor.name][self.weekDay] = self.tutorCreditCount[tutor.name][self.weekDay] - 1
						moduleLabList.insert(0, tuple)
						sessionAssigned.pop()
		return None

	#In this function, the list outputted by the backTrackTask3 function is
	#used to feed valus in the time table.
	def theTimeTable(self, timetableObj3):
		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		for tuple in self.tempTimeTable[dayNumber]:
			[modOrLab, tutor, type] = tuple
			timetableObj3.addSession(days[dayNumber], sessionNumber, tutor, modOrLab, type)
			sessionNumber = sessionNumber + 1

			if sessionNumber == 11:
				dayNumber = dayNumber + 1
				sessionNumber = 0


	#Using the tutorlist and modulelist, create a timetable of 5 slots for each of the 5 work days of the week.
	#The slots are labelled 1-5, and so when creating the timetable, they can be assigned as such:
	#	timetableObj.addSession("Monday", 1, Smith, CS101, "module")
	#This line will set the session slot '1' on Monday to the module CS101, taught by tutor Smith.
	#Note here that Smith is a tutor object and CS101 is a module object, they are not strings.
	#The day (1st argument) can be assigned the following values: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
	#The slot (2nd argument) can be assigned the following values: 1, 2, 3, 4, 5 in task 1 and 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 in tasks 2 and 3.
	#Tutor (3rd argument) and module (4th argument) can be assigned any value, but if the tutor or module is not in the original lists,
	#	your solution will be marked incorrectly.
	#The final, 5th argument, is the session type. For task 1, all sessions should be "module". For task 2 and 3, you should assign either "module" or "lab" as the session type.
	#Every module needs one "module" and one "lab" session type.

	#moduleList is a list of Module objects. A Module object, 'm' has the following attributes:
	# m.name  - the name of the module
	# m.topics - a list of strings, describing the topics that module covers e.g. ["Robotics", "Databases"]

	#tutorList is a list of Tutor objects. A Tutor object, 't', has the following attributes:
	# t.name - the name of the tutor
	# t.expertise - a list of strings, describing the expertise of the tutor.

	#For Task 1:
	#Keep in mind that a tutor can only teach a module if the module's topics are a subset of the tutor's expertise.
	#Furthermore, a tutor can only teach one module a day, and a maximum of two modules over the course of the week.
	#There will always be 25 modules, one for each slot in the week, but the number of tutors will vary.
	#In some problems, modules will cover 2 topics and in others, 3.
	#A tutor will have between 3-8 different expertise fields.

	#For Task 2 and 3:
	#A tutor can only teach a lab if they have at least one expertise that matches the topics of the lab
	#Tutors can only manage a 'credit' load of 4, where modules are worth 2 and labs are worth 1.
	#A tutor can not teach more than 2 credits per day.

	#You should not use any other methods and/or properties from the classes, these five calls are the only methods you should need.
	#Furthermore, you should not import anything else beyond what has been imported above.

	#This method should return a timetable object with a schedule that is legal according to all constraints of task 1.
	def createSchedule(self):
		#Do not change this line
		timetableObj = timetable.Timetable(1)
		tommy = list()
		tommy = self.moduleTutorList(self.tutorList, self.moduleList)
		self.backTrackTask1(tommy)
		self.timeTableIt(self.qwertyList, timetableObj)
		self.moduleTutorList(self.tutorList, self.moduleList)
		#Here is where you schedule your timetable
		#Do not change this line
		return timetableObj

	#Now, we have introduced lab sessions. Each day now has ten sessions, and there is a lab session as well as a module session.
	#All module and lab sessions must be assigned to a slot, and each module and lab session require a tutor.
	#The tutor does not need to be the same for the module and lab session.
	#A tutor can teach a lab session if their expertise includes at least one topic covered by the module.
	#We are now concerned with 'credits'. A tutor can teach a maximum of 4 credits. Lab sessions are 1 credit, module sessiosn are 2 credits.
	#A tutor cannot teach more than 2 credits a day.
	def createLabSchedule(self):
		#Do not change this line
		timetableObj = timetable.Timetable(2)
		#Here is where you schedule your timetable
		#This line generates a random timetable, that may not be valid. You can use this or delete it.
		list1 = list()
		list1 = self.moduleTutorList(self.tutorList, self.moduleList)
		list2 = list()
		list2 = self.labTutorList(self.tutorList, self.moduleList)
		self.backTrackTask2(list1, self.qwertyList1, 2)
		self.backTrackTask2(list2, self.qwertyList2, 1)
		self.timeTableThat(timetableObj)

		#Do not change this line
		return timetableObj

	#It costs £500 to hire a tutor for a single module.
	#If we hire a tutor to teach a 2nd module, it only costs £300. (meaning 2 modules cost £800 compared to £1000)
	#If those two modules are taught on consecutive days, the second module only costs £100. (meaning 2 modules cost £600 compared to £1000)

	#It costs £250 to hire a tutor for a lab session, and then £50 less for each extra lab session (£200, £150 and £100)
	#If a lab occurs on the same day as anything else a tutor teaches, then its cost is halved.

	#Using this method, return a timetable object that produces a schedule that is close, or equal, to the optimal solution.
	#You are not expected to always find the optimal solution, but you should be as close as possible.
	#You should consider the lecture material, particular the discussions on heuristics, and how you might develop a heuristic to help you here.
	def createMinCostSchedule(self):
		#Do not change this line
		timetableObj = timetable.Timetable(3)
		modTutList = list()
		modTutList = self.moduleTutorList(self.tutorList, self.moduleList)
		for muple in modTutList:
			muple.append("module")

		labTutList = list()
		labTutList = self.labTutorList(self.tutorList, self.moduleList)
		for duple in labTutList:
			duple.append("lab")

		modLabList = modTutList + labTutList
		modLabList.sort(key = lambda t:len(t[1]))
		self.backTrackTask3(modLabList, self.tempTimeTable)
		self.theTimeTable(timetableObj)
		#Here is where you schedule your timetable

		#This line generates a random timetable, that may not be valid. You can use this or delete it.
		#self.randomModAndLabSchedule(timetableObj)

		#Do not change this line
		return timetableObj


	#This simplistic approach merely assigns each module to a random tutor, iterating through the timetable.
	def randomModSchedule(self, timetableObj):

		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		for module in self.moduleList:
			tut = self.tutorList[random.randrange(0, len(self.tutorList))]

			timetableObj.addSession(days[dayNumber], sessionNumber, tut, module, "module")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 6:
				sessionNumber = 1
				dayNumber = dayNumber + 1

	#This simplistic approach merely assigns each module and lab to a random tutor, iterating through the timetable.
	def randomModAndLabSchedule(self, timetableObj):

		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		for module in self.moduleList:
			tut = self.tutorList[random.randrange(0, len(self.tutorList))]

			timetableObj.addSession(days[dayNumber], sessionNumber, tut, module, "module")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 11:
				sessionNumber = 1
				dayNumber = dayNumber + 1

		for module in self.moduleList:
			tut = self.tutorList[random.randrange(0, len(self.tutorList))]

			timetableObj.addSession(days[dayNumber], sessionNumber, tut, module, "lab")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 11:
				sessionNumber = 1
				dayNumber = dayNumber + 1
