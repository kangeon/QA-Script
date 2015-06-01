#!/usr/bin/python
import cgi
import cgitb
import os
import subprocess as sub
import re
import urllib


cgitb.enable()

# Referenced code from http://www.tutorialspoint.com/python/python_cgi_programming.htm for GET Method and FieldStorage
# Create instance of FieldStorage
form = cgi.FieldStorage()

# Check command from field
command = form.getvalue('command')

# command not set (Initial Screen)
if (not command):
  if("submitq" in form) and ("question" in form):
    question = form.getvalue('question')
    questionInvalidSearch = re.search(r'.*====.*', question)
    if (not questionInvalidSearch):
      qnum = 0;
      qid = "q" + `qnum`
      while sub.call(['/home/gk698/bin/question', 'create', qid, question]) != 0:
        qnum += 1
        qid = "q" + `qnum`
	
  questionList = []
  # referenced code from http://pymotw.com/2/subprocess/ 
  proc = sub.Popen(['/home/gk698/bin/question', 'list'],
                   stdout=sub.PIPE,
	   			  )
  output = proc.stdout
  for line in iter(proc.stdout.readline,''):
    questionList.append(line.rstrip('\n'))
  
  # Print header
  print 'Content-Type: text/html'
  print

  #Your HTML body
  print "<ul>"
  for item in questionList:
    quoteditem=urllib.quote(item)
    print "<li><a href='http://cs.nyu.edu/~gk698/cgi-bin/question.cgi?command=view&qid=%s'>%s</a></li>" % (quoteditem, item)
  print "</ul>"
  print "<a href='http://cs.nyu.edu/~gk698/cgi-bin/question.cgi?command=create'>Add Question</a>"

if (command == "view") or (command == "vote"):
  questionID = urllib.unquote(form.getvalue('qid'))
  quotedQuestionID=urllib.quote(questionID)	
  if("submita" in form) and ("answer" in form):
    answer = form.getvalue('answer')
    answerInvalidSearch = re.search(r'.*====.*', answer)
    if (not answerInvalidSearch):
      anum = 0;
      aid = "a" + `anum`
      while sub.call(['/home/gk698/bin/question', 'answer', questionID, aid, answer]) != 0:
        anum += 1
        aid = "a" + `anum`
  
  if command == "vote":
    if "aid" in form:
      answerID = urllib.unquote(form.getvalue('aid'))
      if "upvote" in form:
        sub.call(['/home/gk698/bin/question', 'vote', 'up', questionID, answerID])
      else:
        sub.call(['/home/gk698/bin/question', 'vote', 'down', questionID, answerID])
    else:
      if "upvote" in form:
        sub.call(['/home/gk698/bin/question', 'vote', 'up', questionID])
      else:
        sub.call(['/home/gk698/bin/question', 'vote', 'down', questionID])

  print 'Content-Type: text/html'
  print
  
  answerList = []
  proc = sub.Popen(['/home/gk698/bin/question', 'view', questionID],
                   stdout=sub.PIPE,
	   			  )
  #Save output of subprocess to a string.				  
  output = proc.communicate()[0]
  answerList = output.split("====")
  
  # print question details
  questionLines = answerList[0].splitlines()
  voteCountSearch = re.search(r'-?\d+$', questionLines[0])
  if voteCountSearch:
    voteCount = voteCountSearch.group()
  else:
    print "Error: Invalid format."
    print "<br>"	
  print "<p>"
  print "<b>"
  for line in questionLines[1:]:
    print line
    print "<br>"
  print "</b>"
  print "<p>"
  print "<form action=question.cgi method=post>"
  if (re.match(r'^-', voteCount)) or (re.match(r'^0', voteCount)):
    print "%s" % voteCount
  else:
    print "+%s" % voteCount
  print "<input type=submit value='Up' name='upvote'>"
  print "<input type=submit value='Down' name='downvote'>"
  print "<input type=hidden value='%s' name='qid'>" % quotedQuestionID
  print "<input type=hidden value='vote' name='command'>"
  print "</form>"
  print "</p>"
  print "<hr style='border: 2px solid #000;' />"
  
  answerList.pop(0)
  answerList.sort(reverse=True)
  for answer in answerList:
    answerLines = answer.splitlines()
    for line in answerLines[2:]:
      print line
      print "<br>"
    
    voteCountSearch = re.search(r'-?\d+\s', answerLines[1])
    voteCount = voteCountSearch.group()
    answerIDSearch = re.search(r'\s.+/.+$', answerLines[1])
    answerID = answerIDSearch.group().strip()
    print "<form action=question.cgi method=post>"
    if (re.match(r'^-', voteCount)) or (re.match(r'^0', voteCount)):
      print "%s" % voteCount
    else:
      print "+%s" % voteCount
    # print "%s" % answerID
    quotedAnswerID = urllib.quote(answerID)
    print "<input type=submit value='Up' name='upvote'>"
    print "<input type=submit value='Down' name='downvote'>"
    print "<input type=hidden value='%s' name='aid'>" % quotedAnswerID
    print "<input type=hidden value='%s' name='qid'>" % quotedQuestionID
    print "<input type=hidden value=vote name='command'>"
    print "</form>"
    print "<hr style='border: 1px dashed black;' />"

  print "<a href='http://cs.nyu.edu/~gk698/cgi-bin/question.cgi?command=answer&qid=%s'>Add Answer</a>" % quotedQuestionID

if command == "create":
  print 'Content-Type: text/html'
  print
  print "<p>What is your question?</p>"
  print "<form action=question.cgi method=post>"
  print "<textarea name=question rows=10 cols=20>"
  print "</textarea><br>"
  print "<input type=submit value='Cancel' name='cancelq'>"
  print "<input type=submit value='Submit' name='submitq'>"
  print "</form>"
  
if command == "answer":
  print 'Content-Type: text/html'
  print
  questionID = urllib.unquote(form.getvalue('qid'))
  quotedQuestionID = urllib.quote(questionID)
  print "<p>What is your answer?</p>"
  print "<form action=question.cgi method=post>"
  print "<textarea name=answer rows=10 cols=20>"
  print "</textarea><br>"
  print "<input type=submit value='Cancel' name='cancela'>"
  print "<input type=submit value='Submit' name='submita'>"
  print "<input type=hidden value='%s' name='qid'>" % quotedQuestionID
  print "<input type=hidden value='view' name='command'>"  
  print "</form>"  
  
