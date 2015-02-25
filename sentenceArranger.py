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
		for clause in clauses:
			if(includesNN_DEC_NN(clause)): continue

		return recombineClauses(clauses)


#############################################
# Helper functions to identify/alter clauses
#############################################

def includesNN_DEC_NN(clause):
	return True

#############################################
# Useful utility functions
#############################################

def deriveTags(clause):
	tags = ""
	for word in clause:
		if word != "\n": tags += word.split("#")[1] + " "
	return tags

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