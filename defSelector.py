# coding=utf-8

import re
import subprocess

from dictionary import dictionary
from pattern.en import conjugate
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
		if tag == "NN": return chooseNoun(word, index, sentence)
		elif tag == "NR": return chooseNameNoun(word, index, sentence)
		elif tag == "NT": return chooseTimeNoun(word, index, sentence)
		elif tag == "OD": return chooseOrdinalNumber(word, index, sentence)
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
		else: return getDictEntryByPrecedence(word, [], result="all")


#############################################			
#Helper functions for choosing the right word
#############################################

def chooseOtherParticle(word, index, sentence):
	return ''         #getDictEntryByPrecedence(word, ['pron'])

def chooseMannerParticle(word, index, sentence):
	return ''

def chooseAspectParticle(word, index, sentence):
	return ''

def chooseSentenceFinalParticle(word, index, sentence):
	return ''


def pron2poss(word):
	if word == "I": return "my"
	if word == "you" or word == "You": return "you"
	if word == "he" or word == "He": return "his"
	if word == "she" or word == "She": return "her"
	if word == "it" or word == "It": return "its"
	if word == "we" or word == "We": return "our"
	if word == "they" or word == "They": return "their"

	return word

def choosePronoun(word, index, sentence):
	base = getDictEntryByPrecedence(word, ['pron'])
	demarcation = set(["NN", "NR", "NT"])
	index += 1
	while index < len(sentence) and getTag(sentence[index]) not in demarcation:
		if getTag(sentence[index]) == "DEG":
			base = base.split('/')
			base = [pron2poss(w) for w in base]
			return '/'.join(base)
		index += 1
	return base

def choosePredAdjective(word, index, sentence):
  # predicative adjectives; add copula before
	base = chooseAttrAdjective(word, index, sentence)
	if index < len(sentence) and getTag(sentence[index+1]) in ["DEG", "DEV"]:
		return base
	base = base.split('/')
	base = ["be " + word for word in base]
	return '/'.join(base)

def chooseAttrAdjective(word, index, sentence):
  # attributive adjectives; no copula before
	base = getDictEntryByPrecedence(word, ['adj'])
	if index < len(sentence) and getTag(sentence[index+1]) == "DEV":
		base = base.split('/')
		base = [word + "ly" for word in base]
		return '/'.join(base)
	return base 

def chooseLocalizer(word, index, sentence):
	return getDictEntryByPrecedence(word, ['adj', 'prep'])

def chooseConjunction(word, index, sentence):
	return getDictEntryByPrecedence(word, ['conj', 'adv'])

def choosePreposition(word, index, sentence):
	# skip the prep (most likely "在") if a localizer follows
	# Note: this could happen only if the localizer is reordered to the beginning of LCP
	if index < len(sentence) and getTag(sentence[index+1]) == "LC":
		return ""

	return getDictEntryByPrecedence(word, ['prep', 'v'])

def pluralize(word):
	if word[-1] != "s":
		if word[-1] == "y": return word[:-1] + "ies"
		else: return word + "s"
	else:
		return word

def chooseNoun(word, index, sentence):
	base = getDictEntryByPrecedence(word, ['n', 'npl'])
	# add determiner unless there is a noun before (a compound)
	if index > 0 and getTag(sentence[index-1]) not in ["NN", "NR", "NT"]:
		base = base + '/' +'/'.join([addThe(w) for w in base.split('/')])

	# consider the possessive form if before another NN (might be useful)
	# if index < len(sentence) and getTag(sentence[index+1]) == "NN":
	#	base = base + '/' +'/'.join([w+" 's" for w in base.split('/')])

	# pluralize if no another NN after (might be useful)
	if index < len(sentence) and getTag(sentence[index+1]) not in ["NN", "NR", "NT"]:
		base = base # + '/' +'/'.join([pluralize(w) for w in base.split('/')]) # pluralization
	return base

def chooseNameNoun(word, index, sentence):
	base = getDictEntryByPrecedence(word, ['n', 'npl'])

	return base


def chooseTimeNoun(word, index, sentence):
	base = getDictEntryByPrecedence(word, ['n', 'npl'], result="first")
	if index > 0 and getTag(sentence[index-1]) == "P":
		return base  
	# if no preposition before, add one
	return "in "+base + "/on "+base + "/at "+base + '/during '+base
	# possibly not add one?
	#return base + "/in "+base + "/on "+base + "/at "+base + '/during '+base 


def addThe(word):
	if len(word) >= 4 and word[0:4] == "the ":
		return word
	else:
		return "the " + word


def chooseOrdinalNumber(word, index, sentence):
	base = getDictEntryByPrecedence(word, [], result="first")
	return addThe(base)

def chooseMeasureWord(word, index, sentence):
	# hopefully, more fine-grained distinctions?
	# 
	if word in ["年", "倍", "美元"]:
		return getDictEntryByPrecedence(word, ['measure word', 'n'])
	return "" 

#Only helper to return tuple of two items (return word, tense)
#tense returned in all caps as second item present, past, future, progressive, perfective ("have done something"), infinitive
def inflect(verb, case):

	return verb

def chooseVerb(word, index, sentence):
	verb = getDictEntryByPrecedence(word, ['v'])
	prep = getDictEntryByPrecedence(word, ['prep'], default=[])
	if index == 0: case = "PROGRESSIVE"
	elif verbInPrepPhrase(index, sentence): case = "INFINITIVE"
	elif verbFollowingVerb(index, sentence): case = "INFINITIVE"
	elif verbHasProgressiveModifier(index, sentence): case = "PROGRESSIVE"
	elif verbHasPerfectiveModifier(index, sentence): case = "PERFECTIVE"
	else: case = "PRESENT"
	if prep: 
		verbs = verb.split('/') + prep.split('/')
		return '/'.join(inflect(verb, case) for verb in verbs)
	else: 
		verbs = verb.split('/')
		return '/'.join(inflect(verb, case) for verb in verbs)



def chooseVE(word, index, sentence):
	verb = getDictEntryByPrecedence(word, ['v'])
	if index == 0: case = "PROGRESSIVE"
	elif verbInPrepPhrase(index, sentence): case = "INFINITIVE"
	elif verbFollowingVerb(index, sentence): case = "INFINITIVE"
	elif verbHasProgressiveModifier(index, sentence): case = "PROGRESSIVE"
	elif verbHasPerfectiveModifier(index, sentence): case = "PERFECTIVE"
	else: case = "PRESENT"

	if word == "有": return "have/there be", case
	else: return "not have/have not/there be not/there be no", case

def adj2Adv(word):
	if len(word) > 1 and word[-2:] == 'ly': return word
	if word[-1] == 'y': return word[:-1] + "ily" 
	else: return word + "ly"

def v2Adv(word):
	return word + "ingly"

def chooseAdverb(word, index, sentence):
	# if adverbs found, use them
	bestOption = getDictEntryByPrecedence(word, ['adv'], default=[])
	if bestOption: return bestOption

	# if not, find adjectives and turn them to adverbs       
	bestOption = getDictEntryByPrecedence(word, ['adj'], default=[])
	if bestOption: 
		return '/'.join([adj2Adv(w) for w in bestOption.split('/')])
			
	# if still not, find verbs and consider possible adverbs
	#bestOption = getDictEntryByPrecedence(word, ['v'], default=[])
	#if bestOption:
	#	return bestOption + '/' + '/'.join([v2Adv(w) for w in bestOption.split('/')])

	return getDictEntryByPrecedence(word, [], result="all")

def complementizerDE(word, index, sentence):

	return "that/who"  #/which/who

def genitiveDE(word, index, sentence):
	# no 's after adjectives, pronouns or quantifiers such as "most", "a few"
	if index > 0 and getTag(sentence[index-1]) in ["VA", "JJ", "PN", "CD"]:
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
