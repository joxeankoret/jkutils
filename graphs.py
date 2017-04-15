#!/usr/bin/env python

import random

#-----------------------------------------------------------------------
class CGmlGraph:
  def __init__(self, g):
    self.g = g

  def generate(self):
    buf = "graph [ \n"
    nodes = self.g.nodes()
    
    for node in nodes:
      name = node.name
      num = nodes.index(node)
      
      buf += 'node [ id %s \n label "%s"\n fill "blue" \n type "oval"\n LabelGraphics [ type "text" ] ] \n' % (num, name)
    buf += "\n"
    
    i = 0
    for parent in self.g.d:
      p = nodes.index(parent)
      for child in self.g.d[parent]:
        c = nodes.index(child)
        buf += " edge [ source %s \n target %s ]\n" % (p, c)
    
    buf += "]"
    return buf

#-----------------------------------------------------------------------
class CDotGraph:
  def __init__(self, g):
    self.g = g
    self.letter = "a"

  def generate(self):
    buf = 'digraph G {\n graph [overlap=scale]; node [fontname=Courier]; \n\n'
    nodes = self.g.nodes()
    
    for node in nodes:
      name = node.name.replace('"', r'\"')
      num = nodes.index(node)
      
      buf += ' %s%s [shape=%s, label = "%s", color="blue"]\n' % (self.letter, num, node.shape, name)
    buf += "\n"

    for parent in self.g.d:
      p = nodes.index(parent)
      for child in self.g.d[parent]:
        c = nodes.index(child)
        val = self.g.weights[parent,child]
        if val is None:
          color = "red"
        elif val == 0:
          color = "blue"
        elif val == 1:
          color = "green"
        else:
          color = "red"
        
        label = self.g.weights[parent,child]
        if label is not None:
          label = ", label=%s" % label
        else:
          label = ""
        buf += " %s%s -> %s%s [style = bold, color=%s%s]\n" % (self.letter, p, self.letter, c, color, label)
    
    buf += "}"
    return buf

#-----------------------------------------------------------------------
class CNode(object):
  def __init__(self, name, data=None, label=None, shape="box"):
    self.name = name
    self.data = data
    self.label = label
    self.shape = shape

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.__str__()

#-----------------------------------------------------------------------
class CGraph(object):
  def __init__(self):
    self.d = {}
    self.weights = {}
    self.labels = {}
    self.letter = "a"

  def __str__(self):
    return str(self.d)

  def __repr__(self):
    return self.__str__()

  def clear(self):
    self.d.clear()

  def set_dict(self, d):
    self.d = d

  def has_key(self, x):
    return self.d.has_key(x)

  def add_node(self, node):
    self.d[node] = []
  
  def del_node(self, n):
    if self.d.has_key(n):
      del self.d[n]
    
    for n2 in list(self.d):
      if n in self.d[n2]:
        self.d[n2].remove(n)

  def add_vertex(self, edge):
    self.add_node(edge)

  def add_edge(self, n1, n2, check_dups=False, value=None, label=None):
    if not self.d.has_key(n1):
      self.d[n1] = []
    
    if check_dups:
      if n2 in self.d[n1]:
        return
    
    self.d[n1].append(n2)
    self.weights[(n1, n2)] = value
    self.labels[(n1,n2)] = label
  
  def edge_exists(self, n1, n2):
    if not self.d.has_key(n1):
      return False
    return n2 in self.d[n1]

  def get_weight(self, n1, n2):
    if self.weights.has_key((n1, n2)):
      return self.weights[(n1, n2)]
    else:
      return None

  def has_children(self, n):
    return len(self.d[n]) > 0

  def has_parents(self, n):
    for n2 in self.d:
      if n in self.d[n2]:
        return True
    return False

  def node(self, name):
    for n in self.d:
      if n.name == name:
        return n
    
    return None

  def search_path(self, start, end, path=[]):
    path = path + [start]
    if start == end:
      return path
    
    if not self.d.has_key(start):
      return None
    
    for node in self.d[start]:
      if node not in path:
        newpath = self.search_path(node, end, path)
        if newpath:
          return newpath
    
    return None

  def search_all_paths(self, start, end, path=[]):
    path = path + [start]
    
    if start == end:
      yield path
    elif not self.d.has_key(start):
      yield None
    else:
      for node in self.d[start]:
        if node not in path:
          newpaths = self.search_all_paths(node, end, path)
          for newpath in newpaths:
            yield newpath

  def search_longest_path(self, astart, aend):
    longest = None
    l = self.search_all_paths(astart, aend)
    
    for path in l:
      if path is None:
        continue
      
      if longest is None or len(path) > len(longest):
        longest = path
    
    return longest

  def search_shortest_path(self, start, end, path=[]):
    path = path + [start]
    if start == end:
      return path
    if not self.d.has_key(start):
      return None
    
    shortest = None
    for node in self.d[start]:
      if node not in path:
        newpath = self.search_path(node, end, path)
        if newpath:
          if not shortest or len(shortest) > len(newpath):
            shortest = newpath
    
    return shortest

  def add_graph(self, g2):
    for key in list(g2.d):
      if not self.d.has_key(key):
        self.d[key] = []
      
      for value in list(g2.d[key]):
        self.d[key].append(value)

  def nodes(self):
    l = []
    for father in self.d:
      if father not in l:
        l.append(father)
      
      for child in self.d[father]:
        if child not in l:
          l.append(child)
    return l

  def to_adjacency_list(self):
    l = ()
    for father in self.d:
      for child in self.d[father]:
        l += ((father, child), )
    
    return l

  def from_adjacency_list(self, l):
    for element in l:
      k, v = element
      if not self.d.has_key(k):
        self.d[k] = []
      
      if v not in self.d[k]:
        self.d[k].append(v)

  def to_adjacency_matrix(self):
    nodes = self.nodes()
    nodes.sort()
    
    x = []
    for n1 in nodes:
      y = []
      for n2 in nodes:
        if not self.d.has_key(n2) or n1 not in self.d[n2]:
          v = 0
        else:
          v = 1
        y.append(v)
      
      x.append(y)
    
    return nodes, x

  def to_gml(self):
    gml = CGmlGraph(self)
    return gml.generate()
  
  def to_dot(self):
    dot = CDotGraph(self)
    dot.letter = self.letter
    return dot.generate()

  def is_subgraph(self, g2):
    for node in g2.d:
      if node not in self.d:
        return False
      
      for subnode in g2.d[node]:
        if subnode not in self.d[node]:
          return False
    
    return True

  def intersect(self, g):
    l1 = set(self.to_adjacency_list())
    l2 = set(g.to_adjacency_list())    
    r = l1.intersection(l2)
    
    return r

  def union(self, g):
    l1 = set(self.to_adjacency_list())
    l2 = set(g.to_adjacency_list())    
    r = l1.union(l2)
    
    return r

  def difference(self, g):
    l1 = set(self.to_adjacency_list())
    l2 = set(g.to_adjacency_list())    
    r = l1.difference(l2)
    
    return r
  
  def symmetric_difference(self, g):
    l1 = set(self.to_adjacency_list())
    l2 = set(g.to_adjacency_list())    
    r = l1.symmetric_difference(l2)
    
    return r

#-----------------------------------------------------------------------
def test1():
  assert str(CNode("x")) == "x"

  g = CGraph()
  n1 = CNode("a")
  n2 = CNode("b")
  n3 = CNode("c")
  n4 = CNode("d")
  
  g.add_edge(n1, n2)
  g.add_edge(n1, n3)
  g.add_edge(n2, n4)
  g.add_edge(n3, n4)
  
  print "Printing a graph with 4 nodes"
  print g
  
  
  print "Searching path between n1 and n1"
  print g.search_path(n1, n1)
  print "Searching path between n1 and n2"
  print g.search_path(n1, n2)
  print "Searching path between n1 and n4"
  print g.search_path(n1, n4)

  print "Creating a graph with 6 nodes"
  g = CGraph()
  a = CNode("a")
  b = CNode("b")
  c = CNode("c")
  d = CNode("d")
  e = CNode("e")
  f = CNode("f")
  
  g.add_edge(a, b)
  g.add_edge(b, c)
  g.add_edge(c, a)
  g.add_edge(d, e)
  g.add_edge(e, f)
  print "1# Searching a path between a and f"
  print g.search_path(a, f)

  g.add_edge(c, d)
  print "2# Searching a path between a and f"
  print g.search_path(a, f)
  
  g.add_edge(b, f)
  g.add_edge(c, f)
  g.add_edge(a, e)
  print "Searching all paths between a and f"
  print list(g.search_all_paths(a, f))
  
  print "Searching the shortest path between a and f"
  print g.search_shortest_path(a, f)
  
  print "Clearing the graph"
  g.clear()
  print g

#-----------------------------------------------------------------------
def test2():
  #print "Creating 2 graphs with 3 and 5 nodes"
  a = CNode("a")
  b = CNode("b")
  c = CNode("c")
  n = CNode("n")
  x = CNode("x")
  y = CNode("y")

  g1 = CGraph()
  g2 = CGraph()

  g1.add_edge(a, b)
  g1.add_edge(a, c)

  g2.add_edge(a, n)
  g2.add_edge(n, y)
  g2.add_edge(b, x)
  g2.add_edge(x, y)

  #print "Graph 1"
  #print g1
  #print "Graph 2"
  #print g2
  #print "Adding graph 2 to graph 1"
  g1.add_graph(g2)

  #print "Resulting graph"
  #print g1
  
  #print "Adjacency list"
  print g1.to_adjacency_list()
  
  #print "Adjacency matrix"
  #print g1.nodes()
  print g1.to_adjacency_matrix()

#-----------------------------------------------------------------------
def test3():
  a = CNode("a")
  b = CNode("b")
  c = CNode("c")
  n = CNode("n")
  x = CNode("x")
  y = CNode("y")

  g1 = CGraph()
  g2 = CGraph()

  g1.add_edge(a, b)
  g1.add_edge(a, c)

  g2.add_edge(a, n)
  g2.add_edge(n, y)
  g2.add_edge(b, x)
  g2.add_edge(x, y)

  g1.add_graph(g2)
  dot = g1.to_dot()
  gml = g1.to_gml()

#-----------------------------------------------------------------------
def randomGraph(totally=False):
  if totally:
    node_count = random.randint(0, 50)
  else:
    node_count = 50
  nodes = {}
  
  for x in range(node_count):
    name = "n%d" % x
    nodes[name] = CNode(name)
  
  g = CGraph()
  
  for x in nodes:
    for y in nodes:
      if random.randint(0, 10) == 0:
        g.add_edge(nodes[x], nodes[y])

  print g.to_dot()

#-----------------------------------------------------------------------
def randomGraph2():
  node_count = random.randint(0, 50)
  nodes = {}
  
  for x in range(node_count):
    name = "n%d" % x
    nodes[name] = CNode(name)
  
  g = CGraph()
  
  for x in nodes:
    for y in nodes:
      if random.randint(0, 1) == 1:
        g.add_edge(nodes[x], nodes[y])

  for i in range(100):
    n1 = random.choice(nodes.keys())
    n2 = random.choice(nodes.keys())
    
    #print "Searching a path between %s and %s in a %d nodes graph" % (n1, n2, node_count)
    path = g.search_path(n1, n2)
    if path:
      print "Path found between %s and %s in a %d nodes graph" % (n1, n2, node_count)
      print path

#-----------------------------------------------------------------------
def testRandomGraph():
  node_count = random.randint(2, 20)
  nodes = {}
  
  g = CGraph()
  
  for x in range(node_count):
    name = "n%d" % x
    nodes[name] = CNode(name)

  for x in nodes:
    for y in nodes:
      if random.randint(0, 4) == 1:
        g.add_edge(nodes[x], nodes[y])

  print "Graph"
  print g
  print
  print "Searching paths"
  for n1 in g.nodes():
    if g.has_key(n1):
      for n2 in g.d[n1]:
        print n1, n2
        print "Shortest", g.search_shortest_path(n1, n2)
        print "Longest", g.search_longest_path(n1, n2)
        print "All paths: Total %d" % len(list(g.search_all_paths(n1, n2)))

#-----------------------------------------------------------------------
def testis_subgraph():
  """
  Graph 1
         A
        / \
         B   C
        / \ / \
       D  E F  G
  
  Graph 2
         A
        / 
         B
        / \
       D  E
  """

  a = CNode("a")
  b = CNode("b")
  c = CNode("c")
  d = CNode("d")
  e = CNode("e")
  f = CNode("f")
  g = CNode("g")

  g1 = CGraph()
  g1.add_edge(a, b)
  g1.add_edge(a, c)
  g1.add_edge(b, d)
  g1.add_edge(b, e)
  g1.add_edge(c, f)
  g1.add_edge(c, g)

  g2 = CGraph()
  print g2
  g2.add_edge(a, b)
  g2.add_edge(b, d)
  g2.add_edge(b, e)

  print g1
  print "g", g2
  # Check if it's a subgraph
  assert g1.is_subgraph(g2) 
  
  # Change the graph and check again
  g2.add_edge(a, d)
  assert g1.is_subgraph(g2) == False

#-----------------------------------------------------------------------
def testRandomSubgraph():
  #import random

  node_count = random.randint(0, 100)
  nodes = dict()
  
  for x in range(node_count):
    name = "n%d" % int(x)
    nodes[name] = CNode(name)
  
  g = CGraph()
  i = 0
  for x in nodes:
    for y in nodes:
      if random.randint(0, 1) == 1:
        g.add_edge(nodes[x], nodes[y])
      i += 1
      if i <= node_count/2:
        g1 = g
  
  assert g.is_subgraph(g1) == True

#-----------------------------------------------------------------------
def testOperations():
  a = CNode("a")
  b = CNode("b")
  c = CNode("c")
  d = CNode("d")
  e = CNode("e")
  f = CNode("f")
  g = CNode("g")

  g1 = CGraph()
  g1.add_edge(a, b)
  g1.add_edge(a, c)
  g1.add_edge(b, d)
  g1.add_edge(b, e)
  g1.add_edge(c, f)
  g1.add_edge(c, g)

  g2 = CGraph()
  g2.add_edge(a, b)
  g2.add_edge(b, d)
  g2.add_edge(b, e)
  
  g3 = CGraph()
  al = g1.intersect(g2)

  g3.from_adjacency_list(al)
  print g3
  
  al = g1.union(g2)
  g3.clear()
  g3.add_edge(f, a)
  
  g3.from_adjacency_list(al)
  print g3
  
  print g3.to_adjacency_matrix()
  
  print g3.difference(g1)
  print g2.difference(g1)
  print g3.difference(g2)
  
  al1 = g1.union(g2)
  al2 = g2.union(g3)
  new_graph = CGraph()
  new_graph.from_adjacency_list(al1)
  new_graph.from_adjacency_list(al2)
  
  print new_graph

#-----------------------------------------------------------------------
def testNode():
  g = CGraph()
  n = g.node("kk")
  if not n:
    n = CNode("kk")

  g.add_node(n)

#-----------------------------------------------------------------------
def testAll():
  test1()
  test2()

  randomGraph()
  randomGraph2()
  testRandomGraph()
  testis_subgraph()
  testNode()
  testRandomSubgraph()
  testOperations()
  print "Done!"

if __name__ == "__main__":
  testAll()
  pass
