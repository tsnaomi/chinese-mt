import re
import subprocess

from dictionary import dictionary
# from sentenceArranger import verbInPrepPhrase

########################################################			
#Central interface for selecting right dictionary entry,
#given the original sentence, index of target word,
#selected option ("baseline" or "optimized")
########################################################

def defSelector(index, sentence, baseline=False):

	word = getWord(sentence[index])
	tag = getTag(sentence[index])
	
	if baseline:
		return getFirstDictEntry(word)

	else:
		if tag == "NN" or tag == "NR": return chooseNoun(word, index, sentence)
		elif tag == "NT": return chooseTimeNoun(word, index, sentence)
		elif tag == "M": return chooseMeasureWord(word, index, sentence)
		elif tag == "VV" or tag == "VC": return chooseVerb(word, index, sentence)
		elif tag == "VE": return chooseVE(word, index, sentence)
		elif tag == "AD": return chooseAdverb(word, index, sentence)
		elif tag == "P": return choosePreposition(word, index, sentence)
		elif tag == "CC" or tag == "CS": return chooseConjunction(word, index, sentence) 
		elif tag == "LC": return chooseLocalizer(word, index, sentence)
		elif tag == "VA": return choosePredAdjective(word, index, sentence)
                elif tag == "JJ": return chooseAttrAdjective(word, index, sentence)
		elif tag == "PN" or tag == "DT": return choosePronoun(word, index, sentence)
		elif tag == "SP": return chooseSentenceFinalParticle(word, index,sentence)
		elif tag == "AS": return chooseAspectParticle(word, index, sentence)
		elif tag == "DEV": return chooseMannerParticle(word, index, sentence)
		elif tag == "MSP": return chooseOtherParticle(word, index, sentence)
		elif tag == "DEC": return complementizerDE(word, index, sentence)
		elif tag == "DEG": return genitiveDE(word, index, sentence)
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

def choosePredAdjective(word, index, sentence):
  # predicative adjectives; add copula before
	base = chooseAttrAdjective(word, index, sentence)
	if index < len(sentence) and getWord(sentence[index+1]) == "的":
		return base
	base = base.split('/')
	base = ["be " + word for word in base]
	return '/'.join(base)

def chooseAttrAdjective(word, index, sentence):
  # attributive adjectives; no copula before
	base = getDictEntryByPrecedence(word, ['adj'])
	if index < len(sentence) and getWord(sentence[index+1]) == "地":
		base = base.split('/')
		base = [word + "ly" for word in base]
		return '/'.join(base)
	return base 

def chooseLocalizer(word, index, sentence):
	return getDictEntryByPrecedence(word, ['adj', 'prep'])

def chooseConjunction(word, index, sentence):
	return getDictEntryByPrecedence(word, ['conj', 'adv'])

def choosePreposition(word, index, sentence):
	return getDictEntryByPrecedence(word, ['prep', 'v'])

def chooseNoun(word, index, sentence):
	return getDictEntryByPrecedence(word, ['n', 'npl'])

def chooseTimeNoun(word, index, sentence):
	base = getDictEntryByPrecedence(word, ['n', 'npl'], result="first")
	return "in "+base     #  +'/' + base +'/' + "on "+base+'/' + "at "+base+'/'

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

def chooseVE(word, index, sentence):
	verb = getDictEntryByPrecedence(word, ['v'])
	if index == 0: case = "PROGRESSIVE"
	elif verbInPrepPhrase(index, sentence): case = "INFINITIVE"
	elif verbFollowingVerb(index, sentence): case = "INFINITIVE"
	elif verbHasProgressiveModifier(index, sentence): case = "PROGRESSIVE"
	elif verbHasPerfectiveModifier(index, sentence): case = "PERFECTIVE"
	else: case = "PRESENT"

	return "have/there be", case


def adj2Adv(word):
	if word[-1] == 'y': return word[:-1] + "ily" 
	else: return word + "ly"

def v2Adv(word):
	return word + "ingly"

def chooseAdverb(word, index, sentence):

	bestOption = getDictEntryByPrecedence(word, ['adv'], default=[])
	if bestOption: return bestOption

        
	bestOption = getDictEntryByPrecedence(word, ['adj'], default=[])
	if bestOption: 
		return '/'.join([adj2Adv(w) for w in bestOption.split('/')])
			

	bestOption = getDictEntryByPrecedence(word, ['v'], default=[])
	if bestOption:
		return '/'.join([v2Adv(w) for w in bestOption.split('/')])

	return getFirstDictEntry(word)

def complementizerDE(word, index, sentence):

	return "that" # /which/who

def genitiveDE(word, index, sentence):
	if index > 0 and getTag(sentence[index-1]) in ["VA", "JJ"]:
		return ""

	return "'s"

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

def getDictEntryByPrecedence(word, typelist, result="multiple", default=None):
	if result == "all":
		return '/'.join(getAllDictEntries(word))
	for t in typelist:
		bestOption = getDictEntriesofType(word, t)
		if bestOption: 
			if result == "multiple": 
				return '/'.join(bestOption)
			else: return bestOption[0]
	if default is None:
		return getFirstDictEntry(word)
	return default

def getFirstDictEntryofType(word, type):
	for entry in dictionary[word]:
		if entry[1] == type: return entry[0]
	return None

def getDictEntriesofType(word, type):
	return [entry[0] for entry in dictionary[word] if entry[1] == type]

def getFirstDictEntry(word):
	return dictionary[word][0][0]

def getAllDictEntries(word):
	return [entry[0] for entry in dictionary[word]]
