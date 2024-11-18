from bs4 import BeautifulSoup
import urllib.request
import re
import streamlit as st
import pandas as pd
import json
from urllib.parse import quote
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://www.iqair.com/world-air-quality-ranking"

with urllib.request.urlopen(url) as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')
tags = soup('table')

flags = []
cities = []
aqis = []
counter = 0

flag = re.findall('class="country-flag" src="([^"]+)', str(tags))
for f in flag:
    flags.append(f)
    counter += 1
    if counter == 12:
        counter = 0
        break
city = re.findall('class="city-label" href="/([^"]+)', str(tags))
city_names = [match.split("/")[-1] for match in city]
for c in city_names:
    cities.append(c)
    counter += 1
    if counter == 12:
        counter = 0
        break
aqi = re.findall(r'class="aqi-number.+?> (\d+) </div>', str(tags))
for a in aqi:
    aqis.append(int(a))
    counter += 1
    if counter == 12:
        break
        
top_df = pd.DataFrame({'Flags':flags,'Cities':cities,'Aqis':aqis})

def condition(x):
    if 0 <= x < 50:
        return 'background-color : green'   
    if 51 <= x < 100:
        return 'background-color : yellow'
    elif 101 <= x < 150:
        return 'background-color : orange'
    elif 151 <= x < 200:
        return 'background-color : red' 
    elif 201 <= x < 300:
        return 'background-color : purple'
    elif x > 301:
        return 'background-color : brown'                
    else:
        return ''
        
def emoji(x):
    if 0 <= x < 50:
        return 'images/Good.png'
    if 51 <= x < 100:
        return 'images/Neutral.png'
    elif 101 <= x < 150:
        return 'images/Dangerous_Sensitive.png'
    elif 151 <= x < 200:
        return 'images/Dangerous.png' 
    elif 201 <= x < 300:
        return 'images/Hazardous.png'
    elif x > 301:
        return 'images/Biohazard.png'                
    else:
        return ''

df_styled = top_df.style.map(lambda x: condition(int(x)), subset=['Aqis'])

st.set_page_config(layout="wide")
colT1,colT2 = st.columns([2,8])
with colT2:
    st.title("Calidad del Aire en el mundo 🌬")
st.image("images/Leyenda.png", caption="")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(df_styled,
        column_config={
        "Flags": st.column_config.ImageColumn(
            "Bandera"
        ),
        "Cities":"Ciudad",
        "Aqis": "Indice de Calidad del Aire",
    },hide_index=True,width=500,height=460
    )
with col2:
    location = st.text_input("Ingrese Ciudad o Pais","")
    if(location == ""):
        location = "here"
    url = "https://api.waqi.info/feed/" + quote(location) + "/?token=" + os.environ.get("API_TOKEN")
    with urllib.request.urlopen(url) as response:
        json_response = json.loads(response.read()) 
    
    if json_response['status'] != 'error':
        if(json_response['data']['aqi'] == '-'):
            json_response['data']['aqi'] = 0    
        
        st.metric("Indice de Calidad del Aire", f"{json_response['data']['aqi']}",f"{json_response['data']['city']['name']}")
 
        df = pd.DataFrame([[json_response['data']['city']['geo'][0], json_response['data']['city']['geo'][1]]], columns=["lat","lon"])
        st.map(df)
        st.image(emoji(json_response['data']['aqi']), caption="")
    else:
        st.error('Estación desconocida', icon="🚨")
