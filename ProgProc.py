import re
import docx
import random
from autocorrect import Speller
from random import shuffle
from itertools import chain
from docx2python import docx2python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import warnings
import sys


warnings.filterwarnings("ignore")
MODEL_NAME = "dmitry-vorobiev/rubert_ria_headlines"
file_VKR = str(sys.argv[1])
file_collection = open(sys.argv[2], 'r+', encoding="UTF-8")
f = open("Сгенерированные заголовоки.txt", "w+", encoding="UTF-8")

doc = docx.Document(file_VKR)
doc_pyth = docx2python(file_VKR)


######------- I этап -------######
######Создание представлений######


text_full = []
for paragraph in doc.paragraphs:
    text_full.append(paragraph.text.lower())
text = doc_pyth.text.split('\n')

#print(text)
#print(text_full)

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
            arr = [el for el in list1 if el.find(str(list1[i-1])+'.') == 0]
            for j in range(len(arr)):
                arr[j]=arr[j][2:]
            struc[len(struc)-1].append([])   
            struc[len(struc)-1][3] = numeration(arr,[],0,subs+str(list1[i-1])+'.',struct_ex)
            i+=len(arr)
    return struc

struct = numeration(struct_numb,[],0,'',struct_ex)

def collection(file_collection):
    struct_ex = []
    for line in file_collection:
        line = line[:len(line)-1]
        line_list = []
        line_list.append(line[:line.find(":")])
        line = line[line.find(":")+2:]
        arr_list_tittles = line.split(", ")
        line_list.append(arr_list_tittles)
        struct_ex.append(line_list)
    return struct_ex

struct_ex = collection(file_collection)

######------- II этап -------######
####Внесение текста в структуру####
    
for i in range(len(text)):
    text[i] = text[i].replace('\t','').lower()
    text[i] = re.sub("[^\sA-Za-zА-Яа-яЁё.,]", "", text[i])
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
    to_t = "\n"
    
    for i in range(len(list1)-1):
        from_t = list1[i][1]
        to_t = list1[i+1][1]
        list1[i][2] = (' ').join(text[text.index(from_t)+1:text.index(to_t)])


    if list1[len(list1)-1][1] == "заключение":
        list1[len(list1)-1][2] = "ЗДЕСЬ ПИШЕТСЯ ТЕКСТ ДЛЯ ЗАКЛЮЧЕНИЯ"
    else:
        from_t = list1[len(list1)-1][1]
        list1[len(list1)-1][2] = (' ').join(text[text.index(from_t)+1:text.index(to_t)])

    return list1

struct = text_form(struct, text, "")

######------- III этап -------#######
##Автоматическая генерация названий##

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

spell = Speller('ru')

def tittle_gen(list1,struct_ex):

    
    for i in range(len(list1)-1):
        
        if list1[i][1] == "введение":
            f.write(list1[i][0]+' '+list1[i][1]+ "\n")
            f.write("\n---ГЕНЕРАЦИЯ ЗАГОЛОВКОВ НАЧАТА!---\n\n")


        flag_tit = False
        text = list1[i][2]
        text_start = text[:2000]
        text_end = text[:-2000]
        text =  spell(text_start+text_end)
        for k in range(0,len(struct_ex)):
            if list1[i][1] in struct_ex[k][1] or list1[i][1] == struct_ex[k][0]:
                
                flag_tit = True
                l1 = random.randint(0,len(struct_ex[k][1])-1)
                l2 = random.randint(0,len(struct_ex[k][1])-1)
                l3 = random.randint(0,len(struct_ex[k][1])-1)
                head1 = (struct_ex[k][1][l1]+' ')
                head2 = (struct_ex[k][1][l2]+' ')
                head3 = (struct_ex[k][1][l3]+' ')
                text1 = text
                text2 = text
                text3 = text
                head1 = ""
                head2 = ""
                head3 = ""


        if flag_tit:
            encoded_batch = tokenizer.prepare_seq2seq_batch(
             [text1],
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
             [text2],
             return_tensors="pt",
             padding="max_length",
             truncation=True,
             max_length=512)

            output_ids = model.generate(
             input_ids=encoded_batch["input_ids"],
             max_length=512,
             no_repeat_ngram_size=3,
             num_beams=3,
             top_k=0
            )

            headline2 = tokenizer.decode(output_ids[0], 
             skip_special_tokens=True, 
             clean_up_tokenization_spaces=False)

            encoded_batch = tokenizer.prepare_seq2seq_batch(
             [text3],
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

            headline3 = tokenizer.decode(output_ids[0], 
             skip_special_tokens=True, 
             clean_up_tokenization_spaces=False)

            headline1 = spell(head1+(" ").join(headline1.split()[:4]))
            headline2 = spell(head2+(" ").join(headline2.split()[:4]))
            headline3 = spell(head3+(" ").join(headline3.split()[:4]))
            
            headline1 = headline1.replace(". справка","")
            headline1 = headline1.replace("( инжект )","")
            headline1 = headline1.replace("в интернете","")
            headline1 = headline1.replace("эксперты : ","")
            headline2 = headline2.replace(". справка","")
            headline2 = headline2.replace("( инжект )","")
            headline2 = headline2.replace("в интернете","")
            headline2 = headline2.replace("эксперты : ","")
            headline3 = headline3.replace(". справка","")
            headline3 = headline3.replace("( инжект )","")
            headline3 = headline3.replace("в интернете","")
            headline3 = headline3.replace("эксперты : ","")
            headline3 = headline3.replace("эксперт : ","")
            headline2 = headline2.replace("эксперт : ","")
            headline1 = headline1.replace("эксперт : ","")
            headline3 = headline3.replace(". интерактивныи репортаж","")
            headline2 = headline2.replace(". интерактивныи репортаж","")
            headline1 = headline1.replace(". интерактивныи репортаж","")
            headline3 = headline3.replace("инет","")
            headline2 = headline2.replace("инет","")
            headline1 = headline1.replace("инет","")
            headline3 = headline3.replace("инфографика","")
            headline2 = headline2.replace("инфографика","")
            headline1 = headline1.replace("инфографика","")
            headline3 = headline3.replace(":","")
            headline2 = headline2.replace(":","")
            headline1 = headline1.replace(":","")
            headline3 = headline3.replace("(","")
            headline2 = headline2.replace("(","")
            headline1 = headline1.replace("(","")
                
            
            f.write(list1[i][0]+' '+list1[i][1]+ "\n")
            if flag_tit:
                f.write(headline1.capitalize()+ "\n")
                f.write(headline2.capitalize()+ "\n")
                f.write(headline3.capitalize()+ "\n")
            f.write("\n")


    if list1[len(list1)-1][1] == "заключение":
        f.write(list1[len(list1)-1][0] + ' ' + list1[len(list1)-1][1]+ "\n")
        f.write("\n---ГЕНЕРАЦИЯ ЗАГОЛОВКОВ ЗАВЕРШЕНА!---")
    else:
        flag_tit = False
        text = list1[len(list1)-1][2]
        text_start = text[:2000]
        text_end = text[:-2000]
        text =  spell(text_start+text_end)
        

        for k in range(1,len(struct_ex)):
            if list1[len(list1)-1][1] in struct_ex[k][1] or list1[len(list1)-1][1] == struct_ex[k][0]:
                flag_tit = True
                l1 = random.randint(0,len(struct_ex[k][1])-1)
                l2 = random.randint(0,len(struct_ex[k][1])-1)
                l3 = random.randint(0,len(struct_ex[k][1])-1)
                head1 = (struct_ex[k][1][l1]+' ')
                head2 = (struct_ex[k][1][l2]+' ')
                head3 = (struct_ex[k][1][l3]+' ')
                text1 = text
                text2 = text
                text3 = text
                head1 = ""
                head2 = ""
                head3 = ""
                    
        if flag_tit:
            encoded_batch = tokenizer.prepare_seq2seq_batch(
            [text1],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512)

            output_ids = model.generate(
            input_ids=encoded_batch["input_ids"],
            max_length=512,
            no_repeat_ngram_size=2,
            num_beams=3,
            top_k=0
            )

            headline1 = tokenizer.decode(output_ids[0], 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=False)

            encoded_batch = tokenizer.prepare_seq2seq_batch(
            [text2],
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
            [text3],
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
                headline1 = spell(head1+(" ").join(headline1.split()[:4]))
                headline2 = spell(head2+(" ").join(headline2.split()[:4]))
                headline3 = spell(head3+(" ").join(headline3.split()[:4]))
            
            headline1 = headline1.replace(". справка","")
            headline1 = headline1.replace("( инжект )","")
            headline1 = headline1.replace("в интернете","")
            headline1 = headline1.replace("эксперты : ","")
            headline2 = headline2.replace(". справка","")
            headline2 = headline2.replace("( инжект )","")
            headline2 = headline2.replace("в интернете","")
            headline2 = headline2.replace("эксперты : ","")
            headline3 = headline3.replace(". справка","")
            headline3 = headline3.replace("( инжект )","")
            headline3 = headline3.replace("в интернете","")
            headline3 = headline3.replace("эксперты : ","")
            headline3 = headline3.replace("эксперт : ","")
            headline2 = headline2.replace("эксперт : ","")
            headline1 = headline1.replace("эксперт : ","")
            headline3 = headline3.replace(". интерактивныи репортаж","")
            headline2 = headline2.replace(". интерактивныи репортаж","")
            headline1 = headline1.replace(". интерактивныи репортаж","")
            headline3 = headline3.replace(":","")
            headline2 = headline2.replace(":","")
            headline1 = headline1.replace(":","")
            headline3 = headline3.replace("(","")
            headline2 = headline2.replace("(","")
            headline1 = headline1.replace("(","")
            
        if flag_tit:
            f.write(list1[len(list1)-1][0]+ ' ' + list1[len(list1)-1][1] + "\n")
            f.write(headline1.capitalize()+ "\n")
            f.write(headline2.capitalize()+ "\n")
            f.write(headline3.capitalize()+ "\n")
            f.write("\n")
        
    return list1

tittle_gen(struct, struct_ex)

doc_pyth.close()
