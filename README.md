# JK Utils

These are my own Python utilities that I have been using over the last years. Because they might be useful for others too, I decided to make them freely available for anyone.

# License

The libraries are released under LGPL 2.1, which means that you can use in commercial/closed-source software if you want.

# What is in the package?

So far, there are utilities for the following things:

  * graphs: Utility library to construct graphs, find sub-graphs, search paths, etc...
  * fuzzy_hashing: My own fuzzy hashing algorithms.
  * simple_log: Extremely simple logging utilities.
  * process: Simple process management utilities.
  * query_utils: Utilities for constructing SQL language's "where" clauses.
  * web_db: Wrappers around web.py database utilities, for MySQL and SQLite.

# Examples

## Graphs

This is an easy example usage of the graphs library showing how to find if a graph is a sub-graph of another graph (isomorphism):

```
def test_is_subgraph():
  """
  G1)
           A
          / \
         B   C
        / \ / \
       D  E F  G

  G2)
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
  g2.add_edge(a, b)
  g2.add_edge(b, d)
  g2.add_edge(b, e)

  # Check if it's a subgraph
  assert g1.is_subgraph(g2) 
  
  # Change the graph and check again
  g2.add_edge(a, d)
  assert g1.is_subgraph(g2) == False
```

