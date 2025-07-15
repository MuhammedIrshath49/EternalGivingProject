# This is Web Scraping to get the Quranic Verses
#import pandas as pd
import datetime
import bs4
import requests


surah_dict = {
 1:"Surah Al-Fatihah",
 2:"Surah Al-Baqarah",
 3:"Surah Aali Imran",
 4:"Surah An-Nisa",
 5:"Surah Al-Ma’idah" ,
 6:"Surah Al-An’am",
 7:"Surah Al-A’raf" ,
 8:"Surah Al-Anfal",
 9:"Surah At-Taubah",
10:"Surah Yunus",
11:"Surah Hud",
12:"Surah Yusuf",
13:"Surah Ar-Ra’d",
14:"Surah Ibrahim",
15:"Surah Al-Hijr",
16:"Surah An-Nahl",
17:"Surah Al-Isra",
18:"Surah Al-Kahf",
19:"Surah Maryam",
20:"Surah Ta-Ha",
21:"Surah Al-Anbiya",
22:"Surah Al-Haj",
23:"Surah Al-Mu’minun",
24:"Surah An-Nur",
25:"Surah Al-Furqan",
26:"Surah Ash-Shu’ara",
27:"Surah An-Naml",
28:"Surah Al-Qasas",
29:"Surah Al-Ankabut",
30:"Surah Ar-Rum",
31:"Surah Luqman",
32:"Surah As-Sajdah",
33:"Surah Al-Ahzab",
34:"Surah Saba",
35:"Surah Al-Fatir",
36:"Surah Ya-Sin",
37:"Surah As-Saffah",
38:"Surah Sad",
39:"Surah Az-Zumar",
40:"Surah Ghafar",
41:"Surah Fusilat",
42:"Surah Ash-Shura",
43:"Surah Az-Zukhruf",
44:"Surah Ad-Dukhan",
45:"Surah Al-Jathiyah",
46:"Surah Al-Ahqaf",
47:"Surah Muhammad",
48:"Surah Al-Fat’h",
49:"Surah Al-Hujurat",
50:"Surah Qaf",
51:"Surah Adz-Dzariyah",
52:"Surah At-Tur",
53:"Surah An-Najm",
54:"Surah Al-Qamar",
55:"Surah Ar-Rahman",
56:"Surah Al-Waqi’ah",
57:"Surah Al-Hadid",
58:"Surah Al-Mujadilah",
59:"Surah Al-Hashr",
60:"Surah Al-Mumtahanah",
61:"Surah As-Saf",
62:"Surah Al-Jum’ah",
63:"Surah Al-Munafiqun",
64:"Surah At-Taghabun",
65:"Surah At-Talaq",
66:"Surah At-Tahrim",
67:"Surah Al-Mulk",
68:"Surah Al-Qalam",
69:"Surah Al-Haqqah",
70:"Surah Al-Ma’arij",
71:"Surah Nuh",
72:"Surah Al-Jinn",
73:"Surah Al-Muzammil",
74:"Surah Al-Mudaththir",
75:"Surah Al-Qiyamah",
76:"Surah Al-Insan",
77:"Surah Al-Mursalat",
78:"Surah An-Naba’",
79:"Surah An-Nazi’at" ,
80:"Surah ‘Abasa",
81:"Surah At-Takwir",
82:"Surah Al-Infitar",
83:"Surah Al-Mutaffifin",
84:"Surah Al-Inshiqaq",
85:"Surah Al-Buruj",
86:"Surah At-Tariq",
87:"Surah Al-A’la",
88:"Surah Al-Ghashiyah",
89:"Surah Al-Fajr",
90:"Surah Al-Balad",
91:"Surah Ash-Shams",
92:"Surah Al-Layl",
93:"Surah Adh-Dhuha",
94:"Surah Al-Inshirah",
95:"Surah At-Tin",
96:"Surah Al-‘Alaq",
97:"Surah Al-Qadar",
98:"Surah Al-Bayinah",
99:"Surah Az-Zalzalah",
100 : "Surah Al-‘Adiyah",
101 : "Surah Al-Qari’ah",
102 : "Surah At-Takathur",
103 : "Surah Al-‘Asr",
104 : "Surah Al-Humazah",
105 : "Surah Al-Fil",
106 : "Surah Quraish",
107 : "Surah Al-Ma’un",
108 : "Surah Al-Kauthar",
109 : "Surah Al-Kafirun",
110 : "Surah An-Nasr",
111 : "Surah Al-Masad",
112 : "Surah Al-Ikhlas",
113 : "Surah Al-Falaq",
}

url = f"http://ayatalquran.com/random"
r  = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
soup = bs4.BeautifulSoup(r.text,"html.parser")
verse = soup.find('h2',id="ayah_text")
SurahNo = soup.find(id="ayah_ref underline underline-offset-4 hover:text-black dark:hover:text-white")
SurahName = soup.find(id= "surah_name underline underline-offset-4 hover:text-black dark:hover:text-white")
verse = verse if verse is not None else "Unknown verse"
SurahNo = SurahNo if SurahNo is not None else "Unknown number"
SurahName = SurahName if SurahName is not None else "Unknown name"
QuranicVerse = verse + " (" +  SurahNo +  ")" + " (Surah" + " " + SurahName

def printQuranicverse():
   url = f"http://ayatalquran.com/random"
   r  = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
   soup = bs4.BeautifulSoup(r.text,"html.parser")
   verse = soup.find(id="ayah_text").text
   SurahNo = int(soup.find(id="sura_id").text)
   VerseNo = int(soup.find(id="verse_id").text)
   QuranChapter = surah_dict.get(SurahNo)
  
   QuranicVerse = verse + " " + "(" + QuranChapter + " , " + "Verse " + str(VerseNo) + ")"

   return (str(QuranicVerse))


#print(QuranicVerse)
 
    




