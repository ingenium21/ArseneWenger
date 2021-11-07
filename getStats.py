import re,logging,logging.handlers,datetime,requests,requests.auth,sys,json,unicodedata
from bs4 import BeautifulSoup
import tabulate
import time

#Gets current squad memebers and their URLs    
squadDict={}
def fetchSquad():
  tableurl="https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"
  page= requests.get(tableurl, headers={'id':'stats_standard_11160'}, timeout=15).text
  pagesoup = BeautifulSoup(page, 'html.parser')
  tablemain=pagesoup.find('table',{'id':'stats_standard_11160'})
  body=tablemain.find('tbody')

  #Get rows
  rows = body.find_all('tr')
  for row in rows:
    plyrtag=row.find('a')
    plyrname=plyrtag.text
    plyrurl=plyrtag['href']
    plyrpos=row.find('td',{'data-stat':'position'}).text
    squadDict[plyrname]=[]
    squadDict[plyrname].append(plyrurl)
    squadDict[plyrname].append(plyrpos)
  # print(squadDict)  

###################

#Stat slash command function
def statParser(tableurl, pos):
  
  # file1=open("Myfile.txt","a")
  # file1.write(pagesoup.prettify())
  point2=time.time()
  page= requests.get(tableurl, stream=True)
  tablehtml=""
  addvar=False
  for lines_b in page.iter_lines():
    lines_d=lines_b.decode('utf-8')
    if '<tbody>' in lines_d:
      addvar=True
    if addvar:  
      tablehtml+=lines_d
      if "</tbody>" in lines_d:
        break
  point3=time.time()
  pagesoup = BeautifulSoup(tablehtml, 'html.parser')
  tablemain=pagesoup.find('table')
  body=tablemain.find('tbody')

  data=[]
  #Gets table headers
  ssn = body.find_all('th',attrs={'data-stat':'season'},string='2021-2022')
  for rows in ssn:
    row=rows.find_parent('tr',id='stats')
    #Find competition name
    compname_t=row.find('td',{'data-stat':'comp_level'})
    compname=compname_t.find('a').text
    if pos!='GK':
      #No of games played
      gms=row.find('td',{'data-stat':'games'}).text
      #No of starts
      strts=row.find('td',{'data-stat':'games_starts'}).text
      #Goals
      goals=row.find('td',{'data-stat':'goals'}).text
      #Assists
      assts=row.find('td',{'data-stat':'assists'}).text
      #Penalties
      pens=row.find('td',{'data-stat':'pens_made'}).text
      #YC
      yc=row.find('td',{'data-stat':'cards_yellow'}).text
      #RC
      rc=row.find('td',{'data-stat':'cards_red'}).text
      data.append([compname,gms,strts,goals,assts,pens,yc,rc])
    else:
      #No of games played
      gms=row.find('td',{'data-stat':'games_gk'}).text
      #No of starts
      strts=row.find('td',{'data-stat':'games_starts_gk'}).text
      #Goals
      goals_against=row.find('td',{'data-stat':'goals_against_gk'}).text
      #Assists
      svs=row.find('td',{'data-stat':'saves'}).text
      #Penalties
      svs_pct=row.find('td',{'data-stat':'save_pct'}).text
      #YC
      csheet=row.find('td',{'data-stat':'clean_sheets'}).text
      #RC
      w=row.find('td',{'data-stat':'wins_gk'}).text
      d=row.find('td',{'data-stat':'draws_gk'}).text
      l=row.find('td',{'data-stat':'losses_gk'}).text
      data.append([compname,gms,strts,goals_against,svs,svs_pct,csheet,w+"-"+d+"-"+l])

  
  if pos!='GK':
    header=['Comp','Pl','St','G','A','Pen','YC','RC']
    table=tabulate.tabulate(data,headers=header,tablefmt='pretty')
  else:
    header=['Comp','Pl','St','GConc','Sv','Sv%','CS','W-D-L'] 
    table=tabulate.tabulate(data,headers=header,tablefmt='pretty') 
  print(table)
  return table #Returns table