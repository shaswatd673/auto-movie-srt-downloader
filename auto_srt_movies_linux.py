#!/usr/bin/env python3
import sys
import os
import requests
from zipfile import ZipFile
import re

dic = frozenset(['.mp4','.mkv','.avi'])
cur_path = os.path.abspath("./")

#def change_srt_name(file_name):

def distance(a,b):

    mat = [[0 for j in range(len(a)+1)] for i in range(len(b)+1)]
    
    for i in range(len(b)+1):
        mat[i][0]=i
    
    for j in range(len(a)+1):
        mat[0][j]=j

    for i in range(1,len(b)+1):
        for j in range(1,len(a)+1):
            if(a[j-1]==b[i-1]):
                mat[i][j]=mat[i-1][j-1]
            else:
                mat[i][j] = 1+min(mat[i][j-1],mat[i-1][j],mat[i-1][j-1])

    return mat[len(b)][len(a)]


def add_srt(imdb_code,movie):
    search_url='https://rest.opensubtitles.org/search/imdbid-'+imdb_code
    header = {
        'X-User-Agent': 'TemporaryUserAgent',
        'Content-Type':'application/json'
    }
    raw_token = requests.post(search_url, headers=header).json()
    #print(raw_token)
    min_dist = sys.maxsize
    max_rating = 0.0
    for res in raw_token:
        if res['SubLanguageID']=='eng':
            srt_name = res['SubFileName']
            print(movie,"    <->   ",srt_name)
            cur_dist = distance(movie,srt_name[:srt_name.rindex('.')])
            if(cur_dist<min_dist):
                download_link = res['ZipDownloadLink']
                min_dist = cur_dist
                max_rating = res['SubRating']
            elif cur_dist==min_dist and max_rating<res['SubRating']:
                download_link = res['ZipDownloadLink']
                max_rating = res['SubRating']
            
    file = requests.get(download_link,allow_redirects=True).content
    file_path = cur_path+'/'+imdb_code+'.zip'
    open(file_path,'wb').write(file)
    srt_file_name = ""
    with ZipFile(file_path,'r') as zip:
        for name in zip.namelist():
            if(name[name.rindex('.'):]=='.srt'):
                srt_file_name = name
                zip.extract(srt_file_name,cur_path)
    
    print(srt_file_name)
    if srt_file_name != "":
        src = cur_path+'/'+srt_file_name
        des = cur_path+'/'+movie+'.srt'
        os.rename(src,des)

def get_imdbCode(movie):
    x = re.findall(r"19|20[0-9]{2}",movie)
    movie = " ".join(movie.split('.'))
    if len(x)!=0:
        split_index = movie.rfind(x[-1])+4
        movie = movie[:split_index]
    print(movie)
    url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyAE2AJoOo-UwdFBViEVhmIvmWdETl4KwdQ&cx=010039529011339298797:xtmhrxq7iiy&q='
    url+=movie
    res = requests.get(url)
    data = res.json()
    search_info = []
    for i in data['items']:
        search_info.append([i['link'],i['pagemap']['cse_thumbnail']])
    
    ind = search_info[0][0].rindex("tt")
    return search_info[0][0][ind+2:-1]



if __name__=="__main__":
    movie_list = []
    for file in os.listdir(cur_path):
        if os.path.isfile(os.path.join(cur_path,file)):
            name = file[:file.rindex('.')]
            ext = file[file.rindex('.'):]
            if(ext=='.srt'):
                print("Already Present will change the name only")
                break
            if ext in dic:
                movie_list.append(name)
    
    for movie in movie_list:
        imdb_code = get_imdbCode(movie)
        add_srt(imdb_code,movie)
