# # importing required modules
# import PyPDF2
#
# # creating a pdf file object
# pdfFileObj = open('resume33.pdf', 'rb')
#
# # creating a pdf reader object
# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
#
# # printing number of pages in pdf file
# print(pdfReader.numPages)
#
# content = " "
#
# for i in range (pdfReader.numPages):
#     pageObj = pdfReader.getPage(i)
#     # pageObj = pdfReader.getNumPages(i)
#     print(pageObj.extractText())
# # extracting text from page


# closing the pdf file object 
# pdfFileObj.close()








from flask import Flask,render_template,request,session,redirect,url_for
from DBConnection import Db

from werkzeug.utils import secure_filename
import os
import time

import PyPDF2
db = Db()


pdfFileObj = open('R4.pdf', 'rb')

## creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

## printing number of pages in pdf file
print(pdfReader.numPages)

## creating a page object

content = ""
for i in range(0, pdfReader.getNumPages()):
    content += pdfReader.getPage(i).extractText() + "\n"  # Extract text from page and add to content

    content = " ".join(content.replace(u"\xa0", " ").strip().split())

    print(content)

a = (content.find("Skills"))
b = (content.find("project"))

newstring = content[a:b]

print(newstring)

newstring = newstring.replace(",", " ")

thislist = []

thislist = newstring.split()

print(thislist)

newlist = []

res = db.select("select * from skills")
data = res

for i in thislist:
    res = db.selectOne("select * from skills where skillName='" + i + "'")
    if res is not None:
        newlist.append(res['skillID'])

print(newlist)

# closing the pdf file object
pdfFileObj.close()


