from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import urllib
import csv

def artist_pic(artist):
    link_url=""
    artist = artist.replace(" ", "_")
    # strona do bsa
    wikihp = "https://en.wikipedia.org/wiki/"
    URL = wikihp + artist
    wiki = requests.get(URL)
    scwiki = BeautifulSoup(wiki.content, "html.parser")
    # szukanie zdjec
    images = scwiki.find_all("td", class_="infobox-image")
    for link in images:
        string_link = str(link)
        if re.findall('src=',string_link) == []:
            continue
        link_url = link.find('img').get('src')
    return link_url

#pobieranie zdjęć ze zescrapowanych linków
def download_artist_pic(artist_list):
    artist_pic_url = []
    for i in artist_list:
        with_i = i.replace(" ", "_")
        path="images/"+with_i+".png"
        https_url = "https:"+artist_pic(i)
        if https_url == "https:":
            continue
        urllib.request.urlretrieve(https_url,path)
    return print("Zdjęcia pobrane")

#url zdjęć w listę w plik
def artist_pic_to_file(artist_list):
    artist_pic_url = []
    for i in artist_list:
        artist_pic_url.append(artist_pic(i))
    with open('urls.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(artist_pic_url)
    return print("URL zapisane")

#csv do data frame i zmiana piewrszej kolumny
df = pd.read_csv('dane_spotify.csv', sep=',')
df.rename(columns={ df.columns[0]: "id" }, inplace = True)

#Listy url,artystów, liczba utworów
artist_list = sorted(df.artist.unique().tolist())
artist_song_counted = df.groupby('artist')['title'].nunique()

#artist_pic_to_file(artist_list) - sluży do pobrania url do pliku przy pierwszym uruchomieniu
artist_urls_df = pd.read_csv('urls.csv', sep=',')
artist_url = artist_urls_df.columns.values.tolist()



app = Flask(__name__)
@app.route('/')
def home_page():
    return render_template('index.html', artist_url_list_counted=zip(artist_url,artist_list,artist_song_counted))

@app.route('/<artist>')
def artist_page(artist):
    artist_img = " "
    artist_df = df[df['artist'] == artist]
    artist_df = artist_df[['title','language','year','top genre']].values.tolist()
    for i in range(len(artist_list)):
        if artist == artist_list[i]:
            artist_img = artist_url[i]
        else:
            continue
    return render_template('artist.html', artist=artist , artist_img=artist_img, artist_df=artist_df, tableLen= 15 - len(artist_df) )

@app.route('/<artist>/<song>')
def artist_song(artist,song):
    artist_df = df[df['artist'] == artist]
    artist_df_song = artist_df[artist_df['title'] == song]
    lyrics = artist_df_song['lyrics'].values.tolist()
    lyricsStr = lyrics[0]
    return render_template('song.html', artist=artist , song=song , lyrics=lyricsStr )

if __name__ == '__main__':
    app.run()


