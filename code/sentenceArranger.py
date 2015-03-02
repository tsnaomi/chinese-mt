import re
import subprocess

from dictionary import dictionary
from defSelector import getTag, getWord, isType

########################################################			
#Central interface for rearranging characters in sentence,
#so that it makes sense in english, given the 
#selected option ("baseline" or "optimized")
########################################################

def sentenceArranger(sentence, option="optimized"):

	if option=="baseline": return sentence

	if option=="optimized":
		clauses = retrieveClauseList(sentence)
		for i in xrange(len(clauses)):
			clauses[i] = checkDEG(clauses[i])
		return recombineClauses(clauses)


#############################################
# Helper functions to check/alter clauses
#############################################


def checkDEG(clause):

	index = findFirstPattern(clause, ["DEG"])
	if index == None: return clause
	demarcators = set(["VC", "VE", "VV", "P", "CC", "CS", "PU"])

	i = index - 1
	first_phrase = []
	while i >= 0:
		if getTag(clause[i]) not in demarcators:
			first_phrase = [clause[i]] + first_phrase
			i -= 1
		else: break

	beginning = clause[:i+1]

	i = index + 1
	second_phrase = []
	while i < len(clause):
		if getTag(clause[i]) not in demarcators:
			second_phrase = second_phrase + [clause[i]]
			i += 1
		else: break

	end = clause[i:]
	clause = beginning + second_phrase + [clause[index]] + first_phrase + end
	return clause

#Don't know what to do with this yet
def checkLocalizers(clause):
	index = findFirstPattern(clause, ["LC"])
	if index == None: return clause
	return clause
	

#############################################
# Useful utility functions
#############################################


# Find first incidence of pattern of format ["POS-tag1", "POS-tag2", ..., "POS-tag2"]
# Return None if cannot find it, otherwise return index of the incidence
def findFirstPattern(clause, pattern):
	
	clauseLen = len(clause)
	patternLen = len(pattern)
	
	for i in xrange(clauseLen):
		if i + patternLen > clauseLen: return None
		if clause[i + patternLen - 1] == "\n": return None
		if all(getTag(clause[i+j]) == pattern[j] for j in xrange(patternLen)): 
			return i
		else: continue


def retrieveClauseList(sentence):
	clauses = []
	clause = []
	for word in sentence:
		clause.append(word)
		if word == "，#PU" or word == "\n":
			clauses.append(clause)
			clause = []
		else: continue
	return clauses

def recombineClauses(clauses):
	return sum(clauses, [])
