#!/usr/bin/python

"""
JK Utils SQL Query Utils
Copyright (C) 2016-2017 Joxean Koret

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
02110-1301  USA
"""

import sys
import shlex

#-----------------------------------------------------------------------
QUERY_OPERATORS   = ["or", "and", "not"]
COMPARE_OPERATORS = ["!=", "<=", ">=", "=", "<", ">", "like", "is"]

#-----------------------------------------------------------------------
def q2w(fields, query):
  q2w = CQuery2Where()
  q2w.valid_fields = fields
  return q2w.process(query)

#-----------------------------------------------------------------------
def seems_query(q):
  try:
    tokens = tokenize(q)
    if len(tokens) == 1:
      return False
    
    return True
  except:
    return False

#-----------------------------------------------------------------------
def tokenize(query):
  tokens = shlex.split(query)
  l = []
  for token in tokens:
    added = False
    if token not in COMPARE_OPERATORS:
      for op in COMPARE_OPERATORS:
        total = token.count(op)
        if total == 1 and op != token:
          tmp = token.split(op)
          l.append(tmp[0])
          l.append(op)
          if len(tmp) > 1:
            l.append(tmp[1])
          added = True
          break

    if not added:
      l.append(token)

  return l

#-----------------------------------------------------------------------
class CQuery2Where:
  def __init__(self):
    self.valid_fields = []

  def is_valid_field(self, field):
    if len(self.valid_fields) == 0:
      return True
    return field in self.valid_fields

  def quote_string(self, s):
    if s.isdigit():
      return str(s)
    elif s == "null":
      return "null"

    s = s.replace('"','\\"')
    s = s.replace("'","\\'")
    s = s.replace("\n", "")
    return "'%s'" % s

  def process(self, query):
    where = ""
    tokens = tokenize(query)
    compare = False
    query_op = False
    field = False
    for token in tokens:
      if token.strip(" ") == "":
        continue

      if token in QUERY_OPERATORS:
        if query_op:
          raise Exception("Invalid nested operator.")

        query_op = True
        where += "%s " % token
        continue
      elif token in COMPARE_OPERATORS:
        if compare:
          raise Exception("Invalid nested operator %s." % repr(token))
        compare = True
        where += "%s " % token
      elif self.is_valid_field(token):
        where += "%s " % token
      elif compare:
        where += "%s " % self.quote_string(token)
        compare = False
      else:
        raise Exception("Invalid operator field or keyword %s." % repr(token))

      if query_op:
        query_op = False
      
      if field:
        field = False

    return where

#-----------------------------------------------------------------------
def usage():
  print "Usage:", sys.argv[0], "<query>"

#-----------------------------------------------------------------------
def main(query):
  print q2w(["clustered", "total_functions", "hash"], query)

if __name__ == "__main__":
  if len(sys.argv) == 1:
    usage()
  else:
    main(" ".join(sys.argv[1:]))
