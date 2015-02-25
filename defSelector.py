import re
import subprocess

from dictionary import dictionary
# from sentenceArranger import verbInPrepPhrase

########################################################			
#Central interface for selecting right dictionary entry,
#given the original sentence, index of target word,
#selected option ("baseline" or "optimized")
########################################################

def defSelector(index, sentence, option="optimized"):

	word = getWord(sentence[index])
	tag = getTag(sentence[index])
	
	if option == "baseline": 
		return getFirstDictEntry(word)

	elif option == "optimized":
		if tag == "NN" or tag == "NR" or tag == "NT": return chooseNoun(word, index, sentence)
		elif tag == "M": return chooseMeasureWord(word, index, sentence)
		elif tag == "VV" or tag == "VC" or tag == "VE": return chooseVerb(word, index, sentence)
		elif tag == "AD": return chooseAdverb(word, index, sentence)
		elif tag == "P": return choosePreposition(word, index, sentence)
		elif tag == "CC" or tag == "CS": return chooseConjunction(word, index, sentence) 
		elif tag == "LC": return chooseLocalizer(word, index, sentence)
		elif tag == "VA" or tag == "JJ": return chooseAdjective(word, index, sentence)
		elif tag == "PN" or tag == "DT": return choosePronoun(word, index, sentence)
		elif tag == "SP": return chooseSentenceFinalParticle(word, index,sentence)
		elif tag == "AS": return chooseAspectParticle(word, index, sentence)
		elif tag == "DEV": return chooseMannerParticle(word, index, sentence)
		elif tag == "MSP": return chooseOtherParticle(word, index, sentence)
		else: return getFirstDictEntry(word)


#############################################			
#Helper functions for choosing the right word
#############################################

def chooseOtherParticle(word, index, sentence):
	return getDictEntryByPrecedence(word, ['pron'])

def chooseMannerParticle(word, index, sentence):
	return ''

def chooseAspectParticle(word, index, sentence):
	return ''

def chooseSentenceFinalParticle(word, index, sentence):
	return ''

def choosePronoun(word, index, sentence):
	return getDictEntryByPrecedence(word, ['pron'])

def chooseAdjective(word, index, sentence):
	return getDictEntryByPrecedence(word, ['adj'])

def chooseLocalizer(word, index, sentence):
	return getDictEntryByPrecedence(word, ['adj', 'prep'])

def chooseConjunction(word, index, sentence):
	return getDictEntryByPrecedence(word, ['conj', 'adv'])

def choosePreposition(word, index, sentence):
	return getDictEntryByPrecedence(word, ['prep', 'v'])

def chooseNoun(word, index, sentence):
	return getDictEntryByPrecedence(word, ['n', 'npl'])

def chooseMeasureWord(word, index, sentence):
	return getDictEntryByPrecedence(word, ['measure word', 'n'])

#Only helper to return tuple of two items (return word, tense)
#tense returned in all caps as second item present, past, future, progressive, perfective ("have done something"), infinitive
def chooseVerb(word, index, sentence):
	verb = getDictEntryByPrecedence(word, ['v'])
	if index == 0: case = "PROGRESSIVE"
	elif verbInPrepPhrase(index, sentence): case = "INFINITIVE"
	elif verbFollowingVerb(index, sentence): case = "INFINITIVE"
	elif verbHasProgressiveModifier(index, sentence): case = "PROGRESSIVE"
	elif verbHasPerfectiveModifier(index, sentence): case = "PERFECTIVE"
	else: case = "PRESENT"

	return verb, case

def chooseAdverb(word, index, sentence):

	bestOption = getFirstDictEntryofType(word, 'adv')
	if bestOption != None: return bestOption

	bestOption = getFirstDictEntryofType(word, 'adj')
	if bestOption != None: 
		if bestOption == "good": return 'well'
		elif bestOption[-1] == 'y': return bestOption[:-1] + "ily"
		elif bestOption == "major": return "mainly"
		elif bestOption == "big": return "greatly" 
		else: return bestOption + "ly"

	bestOption = getFirstDictEntryofType(word, 'v')
	if bestOption != None:
		if bestOption == "look": return "seemingly"
		else: return bestOption + "ingly"

	return getFirstDictEntry(word)


def verbHasProgressiveModifier(index, sentence):
	demarcation = set(["VV", "VC", "VE"])
	index -= 1
	while index >= 0 and getTag(sentence[index]) not in demarcation:
		if getWord(sentence[index]) == "正" or getWord(sentence[index]) == "在":
			return True
		index -= 1
	return False


def verbHasPerfectiveModifier(index, sentence):
	demarcation = set(["VV", "VC", "VE"])
	index += 1
	while index < len(sentence) and getTag(sentence[index]) not in demarcation:
		if getWord(sentence[index]) == "了": return True
		index += 1
	return False

def verbFollowingVerb(index, sentence):
	if index < 1: return False
	if getTag(sentence[index - 1]) != "VV": return False
	return True

def verbInPrepPhrase(index, sentence):
	if index < 2: return False
	if getTag(sentence[index - 1]) != "NN": return False
	if getTag(sentence[index - 2]) != "P": return False
	return True

#############################################
# Useful utility functions
#############################################

def getTag(token):
	if token.split("#")[0] == "\n": return "\n"
	else: return token.split("#")[1]

def getWord(token):
	return token.split("#")[0]

def isType(token, type):
	if getTag(token) == type: return True
	return False

def getDictEntryByPrecedence(word, typelist):
	for t in typelist:
		bestOption = getFirstDictEntryofType(word, t)
		if bestOption != None: return bestOption
	return getFirstDictEntry(word)

def getFirstDictEntryofType(word, type):
	for entry in dictionary[word]:
		if entry[1] == type: return entry[0]
	return None

def getFirstDictEntry(word):
	return dictionary[word][0][0]