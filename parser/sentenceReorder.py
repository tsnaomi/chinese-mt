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
  # if condition: result = some_reordered_tree

  return Tree(parsed_tree.label(), [reorder(c) for c in result])



def GetChildIndex(parsed_tree, label, search_range=None):
  """ return a list of indices of the children with the designated label
      can optionally restrict the search range
      e.g., search_range = [-1] means only look at the last child
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


def lastChild(parsed_tree):
  if isinstance(parsed_tree, Tree):
    return parsed_tree[len(parsed_tree) - 1]

def moveChildToFront(parsed_tree, child_label):
  """ return a tree where the child_label node is moved to the front
  """
  if isinstance(parsed_tree, Tree):
    front = [c for c in parsed_tree if c.label() == child_label]
    rest = [c for c in parsed_tree if c.label() != child_label]
    return Tree(parsed_tree.label(), front + rest)

def moveChildToBack(parsed_tree, child_label):
  """ return a tree where the child_label node is moved to the back
  """
  if isinstance(parsed_tree, Tree):
    back = [c for c in parsed_tree if c.label() == child_label]
    rest = [c for c in parsed_tree if c.label() != child_label]
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
