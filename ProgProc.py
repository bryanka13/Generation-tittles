import nltk
import pymorphy2
import re
import docx
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from random import shuffle
from itertools import chain
from docx2python import docx2python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import warnings
import random
warnings.filterwarnings("ignore")

MODEL_NAME = "dmitry-vorobiev/rubert_ria_headlines"
######------- I этап -------######
######Создание представлений######

doc = docx.Document('ex1234.docx')
doc_pyth = docx2python('ex1234.docx')

text_full = []
for paragraph in doc.paragraphs:
    text_full.append(paragraph.text.lower())
text = doc_pyth.text.split('\n')




sub1 = "содержание"
sub1_1 = "оглавление"

sub2 = "литература"
sub2_1 = "библиография"
sub2_2 = "список литературы"

arr = [len(text_full)]

st = [text_full.index(el) for el in text_full if sub1 in el] + arr
st1 = [text_full.index(el) for el in text_full if sub1_1 in el] + arr
start = min(st[0],st1[0])+1

fin = [text_full.index(el) for el in text_full if sub2 in el] + arr
fin1 = [text_full.index(el) for el in text_full if sub2_1 in el] + arr 
fin2 = [text_full.index(el) for el in text_full if sub2_2 in el] + arr

final = min(fin[0],fin1[0],fin2[0])

struct_ex = []
struct_numb = []
struct = []


for i in range(start, final):
    struct_ex.append(text_full[i].split(sep = "\t"))
    
for i in range(len(struct_ex)):
    struct_numb.append(struct_ex[i][0])


a = 0

def numeration(list1,struc,i,subs,struct_ex):

    global a
    
    while i != len(list1):
        if '.' not in list1[i]:
            struc.append([str(subs)+str(list1[i]), struct_ex[a][1],""])
            i+=1
            a+=1
        else:
            arr = [el for el in list1 if str(list1[i-1])+'.' in el]
            for j in range(len(arr)):
                arr[j]=arr[j][2:]
            struc[len(struc)-1].append([])   
            struc[len(struc)-1][3] = numeration(arr,[],0,subs+str(list1[i-1])+'.',struct_ex)
            i+=len(arr)
    return struc

struct = numeration(struct_numb,[],0,'',struct_ex)

struct_ex = [['1', ['введение'], ''],
             ['2', ['постановка задачи','постановка проблемы',
                    'постановка вопроса', 'описание задачи',
                    'цели и задачи'], ''],
             ['2', ['обзор существующих решений', 'обзорная часть',
                    'исследования', 'существующие работы',
                    'готовые реализации', 'обзор литературы',
                    'вариации исходной задачи'], ''],
             ['2', ['решение','подход к решению','идея реализации',
                    'алгоритм решения','декомпозиция исходной задачи',
                    'реалзация программы','программный продукт',
                    'описание решения', ], ''],
             ['2', ['результаты','результаты работы алгоритма',
                    'готовые результаты', 'статистика',
                    'эксперименты и результаты','практическая часть',
                    'аналитика результатов работы',
                    'описание полученных результатов', ], ''],
             ['3', ['заключение'], '']]

######------- II этап -------######
####Внесение текста в структуру####
    
for i in range(len(text)):
    text[i] = text[i].replace('\t','').lower()
    text[i] = re.sub("[^A-Z\sa-zА-Яа-яЁё,-]", "", text[i])
    text[i] = text[i].replace('----mediaimagepng----','')
    text[i] = text[i].replace('----image alt text----','')
    text[i] = text[i].replace('см рис','')
    text[i] = text[i].replace('рис','')

    
text = [el for el in text if el != '']


sub2 = "введение"


fin = []

for i in range(len(text)):
    if sub2 == text[i]:
        fin.append(i)
        
final = fin[1]


for i in range(final):
    text.pop(0)

def text_form(list1, text, spec_to):

    from_t = ""
    to_t = "/n"
    
    for i in range(len(list1)-1):
        from_t = list1[i][1]
        if len(list1[i]) == 4:
            to_t = list1[i][3][0][1]
        else:
            to_t = list1[i+1][1]
        list1[i][2] = (' ').join(text[text.index(from_t)+1:text.index(to_t)])

        if len(list1[i]) == 4:
            spec_to = list1[i+1][1]
            list1[i][3] = text_form(list1[i][3],text,spec_to)

    if list1[len(list1)-1][1] == "заключение":
        list1[len(list1)-1][2] = "ЗДЕСЬ ПИШЕТСЯ ТЕКСТ ДЛЯ ЗАКЛЮЧЕНИЯ"
    else:
        from_t = list1[len(list1)-1][1]
        list1[len(list1)-1][2] = (' ').join(text[text.index(from_t)+1:text.index(spec_to)])

    return list1

struct = text_form(struct, text, "")

######------- III этап -------#######
##Автоматическая генерация названий##

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def tittle_gen(list1,struct_ex):

    
    for i in range(len(list1)-1):
        flag_tit = False
        text = list1[i][2]
        text = (list1[i][1]+' ')*3 + text
        if list1[i][0] == "1":
            spec_headline = struct_ex[0][1][0]
            flag = True
        else:
            flag = False
            for k in range(1,len(struct_ex)-1):
                if list1[i][1] in struct_ex[k][1]:
                    flag_tit = True
                    l1 = random.randint(0,len(struct_ex[k][1])-1)
                    l2 = random.randint(0,len(struct_ex[k][1])-1)
                    l3 = random.randint(0,len(struct_ex[k][1])-1)
                    #text = (struct_ex[k][1][l1]+' ')*5 + text
                    head1 = (struct_ex[k][1][l1]+' ')
                    head2 = (struct_ex[k][1][l2]+' ')
                    head3 = (struct_ex[k][1][l3]+' ')


        if flag_tit:
            encoded_batch = tokenizer.prepare_seq2seq_batch(
             [text],
             return_tensors="pt",
             padding="max_length",
             truncation=True,
             max_length=512)

            output_ids = model.generate(
             input_ids=encoded_batch["input_ids"],
             max_length=512,
             no_repeat_ngram_size=4,
             num_beams=2,
             top_k=0
            )

            headline1 = tokenizer.decode(output_ids[0], 
             skip_special_tokens=True, 
             clean_up_tokenization_spaces=False)

            encoded_batch = tokenizer.prepare_seq2seq_batch(
             [text],
             return_tensors="pt",
             padding="max_length",
             truncation=True,
             max_length=512)

            output_ids = model.generate(
             input_ids=encoded_batch["input_ids"],
             max_length=512,
             no_repeat_ngram_size=4,
             num_beams=5,
             top_k=0
            )

            headline2 = tokenizer.decode(output_ids[0], 
             skip_special_tokens=True, 
             clean_up_tokenization_spaces=False)

            encoded_batch = tokenizer.prepare_seq2seq_batch(
             [text],
             return_tensors="pt",
             padding="max_length",
             truncation=True,
             max_length=512)

            output_ids = model.generate(
             input_ids=encoded_batch["input_ids"],
             max_length=512,
             no_repeat_ngram_size=4,
             num_beams=20,
         top_k=0
        )

            headline3 = tokenizer.decode(output_ids[0], 
             skip_special_tokens=True, 
             clean_up_tokenization_spaces=False)

            headline1 = head1 + headline1
            headline1 = head2 + headline2
            headline1 = head3 + headline3
            
            headline1 = headline1.replace(". справка","")
            headline1 = headline1.replace("( инжект )","")
            headline2 = headline2.replace(". справка","")
            headline2 = headline2.replace("( инжект )","")
            headline3 = headline3.replace(". справка","")
            headline3 = headline3.replace("( инжект )","")
                
            
            print(list1[i][0], ' ', list1[i][1])
            if flag:
                print(spec_headline.capitalize())
            elif flag_tit:
                print(headline1.capitalize())
                print(headline2.capitalize())
                print(headline3.capitalize())
            print()

        

            if len(list1[i]) == 4:
                list1[i][3] = tittle_gen(list1[i][3],struct_ex)

    if list1[len(list1)-1][1] == "заключение":
        print(list1[len(list1)-1][0], ' ', list1[len(list1)-1][1])
        print("Заключение")
    else:
        flag_tit = False
        for k in range(1,len(struct_ex)-1):
                if list1[len(list1)-1][1] in struct_ex[k][1]:
                    flag_tit = True
                    l1 = random.randint(0,len(struct_ex[k][1])-1)
                    l2 = random.randint(0,len(struct_ex[k][1])-1)
                    l3 = random.randint(0,len(struct_ex[k][1])-1)
                    #text = (struct_ex[k][1][l1]+' ')*5 + text
                    head1 = (struct_ex[k][1][l1]+' ')
                    head2 = (struct_ex[k][1][l2]+' ')
                    head3 = (struct_ex[k][1][l3]+' ')
                    
        text = list1[len(list1)-1][2]
        text = (list1[len(list1)-1][1]+' ')*5 + text

        encoded_batch = tokenizer.prepare_seq2seq_batch(
         [text],
         return_tensors="pt",
         padding="max_length",
         truncation=True,
         max_length=512)

        output_ids = model.generate(
         input_ids=encoded_batch["input_ids"],
         max_length=512,
         no_repeat_ngram_size=4,
         num_beams=2,
         top_k=0
        )

        headline1 = tokenizer.decode(output_ids[0], 
         skip_special_tokens=True, 
         clean_up_tokenization_spaces=False)

        encoded_batch = tokenizer.prepare_seq2seq_batch(
         [text],
         return_tensors="pt",
         padding="max_length",
         truncation=True,
         max_length=512)

        output_ids = model.generate(
         input_ids=encoded_batch["input_ids"],
         max_length=512,
         no_repeat_ngram_size=4,
         num_beams=5,
         top_k=0
        )

        headline2 = tokenizer.decode(output_ids[0], 
         skip_special_tokens=True, 
         clean_up_tokenization_spaces=False)

        encoded_batch = tokenizer.prepare_seq2seq_batch(
         [text],
         return_tensors="pt",
         padding="max_length",
         truncation=True,
         max_length=512)

        output_ids = model.generate(
         input_ids=encoded_batch["input_ids"],
         max_length=512,
         no_repeat_ngram_size=4,
         num_beams=20,
         top_k=0
        )

        headline3 = tokenizer.decode(output_ids[0], 
         skip_special_tokens=True, 
         clean_up_tokenization_spaces=False)
        if flag_tit:
            headline1 = head1 + headline1
            headline1 = head2 + headline2
            headline1 = head3 + headline3
        
        headline1 = headline1.replace(". справка","")
        headline1 = headline1.replace("( инжект )","")
        headline2 = headline2.replace(". справка","")
        headline2 = headline2.replace("( инжект )","")
        headline3 = headline3.replace(". справка","")
        headline3 = headline3.replace("( инжект )","")
            
        if flag_tit:
            print(list1[len(list1)-1][0], ' ', list1[len(list1)-1][1])
            print(headline1.capitalize())
            print(headline2.capitalize())
            print(headline3.capitalize())
            print()
        
    return list1

tittle_gen(struct, struct_ex)

doc_pyth.close()
