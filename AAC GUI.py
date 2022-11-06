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
#stanza.download('it')
nlp=stanza.Pipeline('it',processors='tokenize,pos,lemma',tokenize_pretokenized=True)

def try_synset(lemmax):
  global synsetFound
  from nltk.corpus import wordnet as wn
  synsetsList=[]
  for synset in wn.synsets(lemmax,lang=('ita')):
      for lemma in synset.lemma_names(u'ita'):
          if(lemmax!=lemma):
            synsetsList.append(lemma)
  #print(synsetsList)
  for i in range(len(synsetsList)):
    response = requests.get("https://api.arasaac.org/api/pictograms/it/search/" + synsetsList[i])
    status = response.status_code
    if status == 200:
      synsetFound=True
      j = response.json()
      id = j[0]['_id']
      return id
  
def text_on_img(filename, text, size):

    if(len(text)<5):
      fnt = ImageFont.truetype('arial.ttf', size)
    else:
      size=size-40
      fnt = ImageFont.truetype('arial.ttf', size)
    #fnt = ImageFont.truetype('arial.ttf', size)
    W, H = (280,280)
    # create image
    image = Image.new(mode = "RGB", size = (W,H), color = "white")
    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(text,font=fnt)
    # draw text
    draw.text((((W-w)/2,(H-h)/2)), text,font=fnt, fill=(0,0,0))
    # save file
    image.save(path_CAA_pictograms+filename)

def getInfo(word):
    global synsetFound
    synsetFound=False
    global index
    type=word[1]
    if(type!='PROPN'):
      token=word[0].lower()
      lemma=word[2].lower()
    else:
      token = word[0]
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
          lemma=token
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
              if(len(keyword)>3):
                keywords.append(keyword)
            if(len(keywords)==10):
              break
          except:
            print("Something went wrong")
      if(len(keywords)>0):
        """if(keywords[0]!=token):
          keywords=[]"""
        keywords=[s for s in keywords if s != lemma and s != word[2] ]
        #print(keywords)
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
      print('404-no pictogram associated with this word exists =', lemma,"lets try with synsets")
      id=try_synset(lemma)
      if(synsetFound==True):
        result.append(id)
        words_for_images.append(token)
        return result
      else:
          
        print("No synset found")
        #print('saving img n: ',index)
        if(type=='VERB' or type=='AUX'):
          text_on_img(filename=str(index)+".png",text=token, size=100)
          words_for_images.append(token)
        else:
          text_on_img(filename=str(index)+".png",text=lemma, size=100)
          words_for_images.append(lemma)
        index+=1
        return result

    elif status == 400:
      print('400-no pictogram associated with this word exists =', lemma,"lets try with synsets")
      try_synset(lemma)
      #print('saving img n: ',index)
      if(type=='VERB' or type=='AUX'):
        text_on_img(filename=str(index)+".png",text=token, size=100)
        words_for_images.append(token)
      else:
        text_on_img(filename=str(index)+".png",text=lemma, size=100)
        words_for_images.append(lemma)
      index+=1
      
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
  global pics
  pics=[]
  global index
  while index<len(words):
    info = getInfo(words[index]) #TOKENCAA [0] | ACTION [1] | PLURAL_STATUS[2] | ID[3]
    #print("info:",info)
    if(len(info)==4):
      pics.append(info[3])
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
    #print('saving img n: ',index)
    index+=1
    
  elif not action == 'indef':
    #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_action-'+action+'_300.png',
   path_CAA_pictograms +str(index)+'.png')
    #print('saving img n: ',index)
    index+=1
    
  else:
     #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_300.png',
   path_CAA_pictograms+str(index)+'.png')
    #print('saving img n: ',index)
    index+=1

def translate(input_text):
  imagesList = listdir(path_CAA_pictograms)
  for i in imagesList:
    os.remove(path_CAA_pictograms+i)
  global index
  index=0
  global lemma_sentence
  lemma_sentence=""
  global words_for_images
  words_for_images=[]
  frase=str(input_text)
  #print(frase)
  frase=re.sub(r"[-()\"#/@;:<>{}`+=~|$%&]", "", frase)
  #frase= input()
  doc=nlp(frase)
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
      print('pics: ',pics)
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
        plt.figure().clear()
        plt.cla()
        plt.clf()
        img = plt.imread(path_CAA_pictograms+imagesList[0])
        imgplot = plt.imshow(img)
        ax = plt.gca()
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.title.set_text(words_for_images[0])
        plt.savefig(path_CAA_pictograms+'figure.png') 
      #plt.show()
      return(pics)

index=0
lemma_sentence=""
words_for_images=[]
pics=[]

def startGUI():
  executed=False
  v=""
  sg.theme('TealMono')   # Add a touch of color
  # All the stuff inside your window.
  layout = [  
              [sg.Text('Enter the sentence'), sg.Input(key='-INPUT-')],
              [sg.Submit('Translate'), sg.Button('Clear'), sg.Button('Cancel')],
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
              #window['OUTPUT'].update(value=v)
              im = Image.open(path_CAA_pictograms+'figure.png')
              image = ImageTk.PhotoImage(image=im)
              window['-IMAGE-'].update(data=image)

      elif event=='Clear':
          window.FindElement('-INPUT-').Update('')
          window.FindElement('-IMAGE-').Update('')
          executed=False

  window.close()

def evaluation():
  n_correct=0
  df = pd.read_csv("C:/Users/nican/Desktop/NLP progetto/sentences.csv")
  for i in range(len(df)):
    lst=df["array_id"][i].split("[")[2].split("]")
    lst = lst[:len(lst)-2]
    lst=lst[0].split(",")
    for k in range(len(lst)):
      lst[k]=int(lst[k])
    df["array_id"][i]=lst

  for i in range(len(df)):
    if(translate(df["sentence"][i])==df["array_id"][i]):
      n_correct+=1
      print("originale: ",df["array_id"][i])
    if(i==5):
      break
    
  print(n_correct)

startGUI()