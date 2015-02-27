# coding=utf-8

from nltk.tree import *
from nltk.draw import tree

def reorder(parsed_tree):
  """ takes a parse tree, return a re-ordered tree 
   1. move DEC de to the end, then move what was before de to the end
   2. move LOC to the front
   3. move PP, LOCP in the middle of the sentence to the end.
  """
  result = parsed_tree

  if not isinstance(parsed_tree, Tree):
    # return leaves as they are
    return result

  # all the reordering happens below
  # general schema 
  # if condition: result = some_reorder_strategy(result, ...)

  # move CP headed by DEC to the back of the current phrase
  cp_inds = indicesOfCP(result)
  decp_inds = [i for i in cp_inds if isHeadedByDEC(result[i])]

  result = moveChildrenToBack(result, decp_inds)

  # move DEC to the front of the current phrase
  dec_inds = indicesOfDEC(result)
  if dec_inds:
    result = moveChildrenToFront(result, dec_inds)

  # move LC to the front of the current phrase
  lc_inds = indicesOfLC(result)
  if lc_inds:
    result = moveChildrenToFront(result, lc_inds)

  return Tree(parsed_tree.label(), [reorder(c) for c in result])



def childrenIndicesByLabel(parsed_tree, label, search_range=None):
  """ return a list of indices of the children with the designated label
      can optionally restrict the search range
      NOTE: indices must be positive! So use [len(ls)-1] instead of [-1]
  """
  # words
  if not isinstance(parsed_tree, Tree):
    return []

  # terminal nodes
  if not isinstance(parsed_tree[0], Tree):
    return []

  if search_range is not None:
    return [i for i in search_range
              if parsed_tree[i].label() == label]
  else:
    return [i for i in range(len(parsed_tree)) 
              if parsed_tree[i].label() == label]


def indicesOfCP(parsed_tree):
  # return a list containing all the CP indices
  
  return childrenIndicesByLabel(parsed_tree, "CP")

def indicesOfDEC(parsed_tree):
  # return a list containing the index of DEC
  # only look for the final position, so either [] or singleton
  
  return childrenIndicesByLabel(parsed_tree, "DEC", 
                                search_range=[len(parsed_tree)-1])

def isHeadedByDEC(parsed_tree):
  # return whether the tree is headed by DEC

  if indicesOfDEC(parsed_tree):
    return True
  else:
    return False

def indicesOfLC(parsed_tree):
  # return a list containing the index of LC
  # only look for the final position, so either [] or singleton
  
  return childrenIndicesByLabel(parsed_tree, "LC", 
                                search_range=[len(parsed_tree)-1])

def isHeadedByLC(parsed_tree):
  # return whether the tree is headed by LC

  if indicesOfLC(parsed_tree):
    return True
  else:
    return False



def moveChildrenToFront(parsed_tree, indices):
  """ return a tree where the nodes with the indices are moved to the front
  """
  if isinstance(parsed_tree, Tree):
    front = [parsed_tree[i] for i in range(len(parsed_tree))
                            if i in indices]
    rest = [parsed_tree[i] for i in range(len(parsed_tree))
                            if i not in indices]
    return Tree(parsed_tree.label(), front + rest)

def moveChildrenToBack(parsed_tree, indices):
  """ return a tree where the nodes with the indices are moved to the front
  """
  if isinstance(parsed_tree, Tree):
    back = [parsed_tree[i] for i in range(len(parsed_tree))
                            if i in indices]
    rest = [parsed_tree[i] for i in range(len(parsed_tree))
                            if i not in indices]
    return Tree(parsed_tree.label(), rest + back)





# produce tagged sentences
def tree2TaggedSentence(ptr):
  return ' '.join([word + "#" + pos for (word, pos) in ptr.pos()])

def substituteNormalNumbers(s):
  """ turn utf Chinese Arabic numbers back to normal Arabic numbers
  """
  s = s.replace("\xef\xbc\x90", "0")
  s = s.replace("\xef\xbc\x91", "1")
  s = s.replace("\xef\xbc\x92", "2")
  s = s.replace("\xef\xbc\x93", "3")
  s = s.replace("\xef\xbc\x94", "4")
  s = s.replace("\xef\xbc\x95", "5")
  s = s.replace("\xef\xbc\x96", "6")
  s = s.replace("\xef\xbc\x97", "7")
  s = s.replace("\xef\xbc\x98", "8")
  s = s.replace("\xef\xbc\x99", "9")

  return(s)  

if __name__ == '__main__':
    
  parsed_path = "./dev-parsed-30-stp.txt"
  output_path = parsed_path.replace("parsed", "reordered")

  with open(parsed_path, 'r') as parsed_file:
    raw_parsed = parsed_file.read()

  parsed_strings = [s for s in raw_parsed.split("\n\n") if s != "" ]
  parsed_trees = [Tree.fromstring(s) for s in parsed_strings]

  reordered_trees = [reorder(ptr) for ptr in parsed_trees]
  sentences = [tree2TaggedSentence(ptr) for ptr in reordered_trees]

  with open(output_path, 'w') as output_file:
    for s in sentences:
      output_file.write(substituteNormalNumbers(s) + '\n')
