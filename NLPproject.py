import csv
import pandas as pd
import requests
import urllib.request
from IPython.display import Image
import spacy
from PIL import Image, ImageDraw, ImageFont
import stanza
import string
from os import listdir
import matplotlib.pyplot as plt
import os
import re
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk,ImageDraw,ImageFont
import warnings
warnings.filterwarnings("ignore")

def text_on_img(filename, text, size):
    "Draw a text on an Image, saves it, show it"
    fnt = ImageFont.truetype('arial.ttf', size)
    w,h = fnt.getsize(text)
    W=int(size/1.5)*len(text)
    H=size+50
    # create image
    image = Image.new(mode = "RGB", size = (int(size/1.5)*len(text),size+50), color = "white")
    draw = ImageDraw.Draw(image)
    # draw text
    draw.text(((W-w)/2,(H-h)/2), text, font=fnt, fill=(0,0,0))
    # save file
    image.save(path_CAA_pictograms+filename)

def getInfo(word):
    global index
    token = word[0]
    type=word[1]
    lemma=word[2]
    gender=""
    if(type=='DET'):
      lemma=token
    if(type=='NOUN' or type=='DET' or type=='PRON' or type=='ADJ'):
      if(word[3]!=None):
        


        splitted=word[3].split("|")
        for i in range(len(splitted)):
            if splitted[i].find("Gender")!=-1:
              gender=splitted[i].split("=")[1]
        if(gender=="Fem" and gender!=""):
          lemma=word[2][:-1]+"a" 
    #lemma=word[2]
    action = 'indef'
    result = []

    #identify if the word is a verb or auxiliar    
    if (type == 'AUX'):
        
        tense=word[3].split("|")[3].split("=")[1]
        
        if(tense=="Past" or tense=="Imp"):
          action="past"
        if(tense=="Fut"):
          action='future'
    
    if (type == 'VERB'):
        if not word[3].split("=")[1]=="Inf":
              
            tense=word[3].split("|")[2].split("=")[1]
            
            if(tense=="Past" or tense=="Imp"):
              action="past"
            if(tense=="Fut"):
              action='future'
    
    result.append(lemma) #add to the list the token  #TOKENCAA [0]
    result.append(action) #add to the list the action   #ACTION [1]

    number="sing"
    if(type!='ADP' and type!='ADV' and type!='INTJ' and type!='PUNCT' and type!='CCONJ' and type!='PROPN' and type!='SCONJ' and type!='X'):
      if(word[3]!=None):
          
        plural=word[3].split("|")
        
        for i in range(len(plural)):
            if plural[i].find("Number")!=-1:
              number=plural[i].split("=")[1]
              
    result.append(number)
    response = requests.get("https://api.arasaac.org/api/pictograms/it/search/" + lemma) #Obtain best pictograms based on the searchText
    status = response.status_code
    if status == 200:

      j = response.json()
      keywords=[]
      for word2 in j:
          try:
            keyword=word2["keywords"][0]["keyword"]
            if(len(keyword)>=len(token)):
              keywords.append(keyword)
          except:
            print("Something went wrong")
      keywords=[s for s in keywords if s != lemma and s != word[2] ]
      present=False
      for keyword in keywords:
          
          if lemma_sentence.find(keyword)!=-1:
              present=True
              words=len(keyword.split(" "))
              print(words,": ",keyword)
              global index
              index+=words
              global words_for_images
              words_for_images.append(keyword)
              response2 = requests.get("https://api.arasaac.org/api/pictograms/it/bestsearch/" + keyword)
              j2=response2.json()
              id = j2[0]['_id']
              result.append(id)
              index+=1
              return result
              break
    
    response = requests.get("https://api.arasaac.org/api/pictograms/it/bestsearch/" + lemma)
    j = response.json()
    status = response.status_code
    if status == 200:
      
      id = j[0]['_id'] #extract id by response
      result.append(id) #add to the list the id #ID [2]
      
      words_for_images.append(token)
      
      return result
    elif status == 404:
      print('404-no pictogram associated with this word exists =', lemma)
      text_on_img(filename=str(index)+".png",text=lemma, size=100)
      print('saving img n: ',index)
      index+=1
      words_for_images.append(lemma)
      
      return result
    elif status == 400:
      print('400-no pictogram associated with this word exists =', lemma)
      text_on_img(filename=str(index)+".png",text=lemma, size=100)
      print('saving img n: ',index)
      index+=1
      words_for_images.append(lemma)
      
      return result
    elif status == 500:
      print('500 status')
      index+=1
      words_for_images.append(lemma)
      
      return result
    
path_CAA_pictograms = 'C:/Users/nican/Desktop/NLP progetto/immagini/'

def getArray_id(words):
  array_id = []
  infos=[]
  global index
  while index<len(words):
    info = getInfo(words[index]) #TOKENCAA [0] | ACTION [1] | PLURAL_STATUS[2] | ID[3]
    print("info:",info)
    infos.append(info)
    if(len(info)==4):

      action = info[1]
      id = info[3]
      plural_status = info[2]
      array_id.append(id) #add id to array_id
      getImg(id, plural_status,action) #save img
  
  return infos

def getImg(id, plural_status,action): #parameter:id, plural_status, action
  #print('id','id')
  global index
  if plural_status=="Plur":
    #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_plural_300.png',
   path_CAA_pictograms+str(index)+'.png')
    print('saving img n: ',index)
    index+=1
    
  elif not action == 'indef':
    #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_action-'+action+'_300.png',
   path_CAA_pictograms +str(index)+'.png')
    print('saving img n: ',index)
    index+=1
    
  else:
     #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_300.png',
   path_CAA_pictograms+str(index)+'.png')
    print('saving img n: ',index)
    index+=1

def translate(input_text):
  global index
  index=0
  global lemma_sentence
  lemma_sentence=""
  global words_for_images
  words_for_images=[]
  #stanza.download('it')
  nlp=stanza.Pipeline('it',processors='tokenize,mwt,pos,lemma')
  frase=str(input_text)
  #print(frase)
  frase=re.sub(r"[-()\"#/@;:<>{}`+=~|$%&]", "", frase)
  imagesList = listdir(path_CAA_pictograms)
  for i in imagesList:
    os.remove(path_CAA_pictograms+i)
  #frase= input()
  #words_for_images=[]
  doc=nlp(frase)
  #index=0
  lemmas=[]
  for sentence in doc.sentences:
      posT=[(w.text, w.pos,w.lemma,w.feats) for w in sentence.words]
      print(posT)
      for i in posT:
        lemmas.append(i[2])
      lemma_sentence=""
      for i in lemmas:
        lemma_sentence+=i
        lemma_sentence+=" "
      getArray_id(posT)

      print('words for images: ',words_for_images)
      imagesList = listdir(path_CAA_pictograms)
      n_images = len(imagesList)
      
      if(n_images>1):

        fig, axes = plt.subplots(1,n_images)
        for ax, imgname in zip(axes, imagesList):
          img = plt.imread(path_CAA_pictograms+imgname)
          ax.imshow(img)
          ax.xaxis.set_visible(False)
          ax.yaxis.set_visible(False)
        for ax,j in zip(fig.axes,range(len(words_for_images))):
          ax.title.set_text(words_for_images[j])
        plt.savefig(path_CAA_pictograms+'figure.png')
      elif(n_images==1):
        img = plt.imread(path_CAA_pictograms+imagesList[0])
        imgplot = plt.imshow(img)
        ax = plt.gca()
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.title.set_text(words_for_images[0])
        plt.savefig(path_CAA_pictograms+'figure.png')
                      
      #plt.show()

index=0
lemma_sentence=""
words_for_images=[]

def startGUI():
  executed=False
  v=""
  sg.theme('DarkAmber')   # Add a touch of color
  # All the stuff inside your window.
  layout = [  
              [sg.Text('Enter the sentence'), sg.Input(key='-INPUT-')],
              [sg.Button('Translate'), sg.Button('Clear'), sg.Button('Cancel')],
              [sg.Text(""), sg.Multiline(key='OUTPUT') ],
              [sg.Image(size=(300, 300), key='-IMAGE-')]
              ]

  # Create the Window
  window = sg.Window('AAC', layout)
  # Event Loop to process "events" and get the "values" of the inputs

  while True:

      event, values = window.read()
      if event in (sg.WINDOW_CLOSED, 'Cancel'):
          break
      elif event == 'Translate':
          if executed==False or v!=values['-INPUT-']:
            if values['-INPUT-']!="":
                
              v = values['-INPUT-']
              translate(v)
              executed=True
              window['OUTPUT'].update(value=v)
              im = Image.open(path_CAA_pictograms+'figure.png')
              image = ImageTk.PhotoImage(image=im)
              window['-IMAGE-'].update(data=image)

      elif event=='Clear':
          window.FindElement('-INPUT-').Update('')
          window.FindElement('OUTPUT').Update('')
          window.FindElement('-IMAGE-').Update('')
          executed=False

  window.close()

startGUI()
