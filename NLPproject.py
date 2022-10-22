import csv
import pandas as pd
import requests
from IPython.display import Image
import urllib.request
from PIL import Image
from IPython.display import Image
import spacy

def getInfo(word):
    token = word[0]
    type=word[1]
    lemma=word[2]
    action = 'indef'
    result = []

    #identify if the word is a verb    
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
    
    result.append(lemma) #add a list the token for CAA  #TOKENCAA [0]
    result.append(action) #add a list the action   #ACTION [1]

    #qui inserisco plural status nuovo
    number="sing"
    if(type!='ADP' and type!='ADV' and type!='INTJ' and type!='PUNCT'):
      plural=word[3].split("|")
      
      for i in range(len(plural)):
          if plural[i].find("Number")!=-1:
            number=plural[i].split("=")[1]
            
    #print(number)
    result.append(number)

    response = requests.get("https://api.arasaac.org/api/pictograms/it/search/" + lemma) #Obtain best pictograms based on the searchText
  
    status = response.status_code
    #print(status)
    #status code = 200 -> SUCCESS
    if status == 200:

      j = response.json()

      #AGGIUNTA QUI X PAROLE COMPOSTE
      keywords=[]
      for word in j:
          keywords.append(word["keywords"][0]["keyword"])
      keywords=[s for s in keywords if s != lemma ]
      
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
              response2 = requests.get("https://api.arasaac.org/api/pictograms/it/search/" + keyword)
              j2=response2.json()
              id = j2[0]['_id']
              result.append(id)
              return result
              break

      #print(present)
      index+=1
      words_for_images.append(token)
      response = requests.get("https://api.arasaac.org/api/pictograms/it/bestsearch/" + lemma)
      j = response.json()
      #ID [3]
      id = j[0]['_id'] #extract id by response
      result.append(id) #add a list the id #ID [2]

      return result
    #status code = 500 -> NOT FOUND
    elif status == 404:
      print('no pictogram associated with this word exists =', lemma)
      index+=1
      return result
    #status code = 500 -> ERROR
    elif status == 500:
      #print(response.json())
      index+=1
      return result
    
path_CAA_pictograms = 'C:/Users/nican/Desktop/NLP progetto/immagini/'

def getArray_id(words):
  array_id = []
  infos=[]
  global index
  while index<len(words):
  #for index in range(len(words)):
    #print(index)
    #print(word)
    info = getInfo(words[index]) #TOKENCAA [0] | ACTION [1] | ID[2] | PLURAL_STATUS[3]
    print(info)
    infos.append(info)
    #print(info)
    if(len(info)==4):

      action = info[1]
      id = info[3]
      plural_status = info[2]
      array_id.append(id) #add id to array_id
      getImg(id, plural_status,action) #save img in Drive
  
  #return array_id
  return infos

def getImg(id, plural_status,action): #parameter:id, plural_status[true/false], action[past, future,none]
  #print('id','id')
  if plural_status=="Plur":
    #Copy a network object denoted by a URL to a local file
     #urllib.request.urlretrieve(url, filename=None, reporthook=None, data=None)
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_plural_300.png',
   path_CAA_pictograms+str(index)+'.png')
    
  elif not action == 'indef':
    #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_action-'+action+'_300.png',
   path_CAA_pictograms +str(index)+'.png') 
    
  else:
     #Copy a network object denoted by a URL to a local file
    urllib.request.urlretrieve('https://static.arasaac.org/pictograms/'+str(id)+'/'+str(id)+'_300.png',
   path_CAA_pictograms+str(index)+'.png')
    
import stanza
#stanza.download('it')
nlp=stanza.Pipeline('it',processors='tokenize,mwt,pos,lemma')
frase="corro in un campo da tennis"
#frase= input()
words_for_images=[]
doc=nlp(frase)
index=0
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
    #print(lemma_sentence)
    getArray_id(posT)

    from os import listdir
    import matplotlib.pyplot as plt
    #path = 'C:/Users/nican/Desktop/NLP progetto/immagini/'
    imagesList = listdir(path_CAA_pictograms) 
    n_images = len(imagesList)  
    figure, axes = plt.subplots(1,n_images)
    for ax, imgname in zip(axes, imagesList):
      img = plt.imread(path_CAA_pictograms+imgname)
      ax.imshow(img)
    for ax,j in zip(figure.axes,range(len(words_for_images))):
      ax.title.set_text(words_for_images[j])
      ax.axis("off")                    
    plt.show()