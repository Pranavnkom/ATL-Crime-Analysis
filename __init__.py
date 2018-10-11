import os
from flask import Flask, request, render_template
import pandas as pd
from json import loads
import googlemaps
import matplotlib as mpl
import io
import base64
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from math import cos, asin, sqrt

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))

gmaps_key = googlemaps.Client(key = 'AIzaSyDpTVDSs4skfp01KMgW-t6R-8v-8xVviX8')


filename = 'COBRA-2009-2017.csv'
df = pd.read_csv(filename, dtype='str', error_bad_lines=False,)
df = df.drop_duplicates()
df[['Latitude','Longitude']] = df[['Latitude','Longitude']].apply(pd.to_numeric, errors='ignore')
dic = {}
for i in df['UCR_Literal'].unique():
    dic[i] = 0



app = Flask(__name__)



@app.route('/', methods=['GET','POST'])
def main():
    return render_template("home.html")

@app.route('/searched',methods=['POST'])
def searched():
    address = request.form['address']
    parts = address.split(',')
    if (not " Atlanta" in  parts) or (not " GA" in parts):
        return "Must input an Atlanta address."
    if not request.form['km']:
        return "Please enter a radius."
    geocode_result = gmaps_key.geocode(address)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lng = geocode_result[0]["geometry"]["location"]["lng"]
    lats = df['Latitude'].tolist()
    lngs = df['Longitude'].tolist()
    crimes = df['UCR_Literal'].tolist()
    times = df['Possible_Time'].tolist()
    dates = df['Possible_Date'].tolist()
    day_crimes = 0
    night_crimes = 0

    for i in df['UCR_Literal'].unique():
        dic[i] = 0

    for i,j,k,l,m in zip(lats,lngs,crimes,dates,times):
        if (distance(lat,lng,i,j) < int(request.form['km'])) and (request.form['year'] in str(l).split('-')):
            dic[k]+= 1
            if int(m) >= 700 and int(m) <= 1900:
                day_crimes += 1
            else:
                night_crimes += 1

    content = {}
    content['0'] = "In {}, there were...".format(request.form['year'])
    ind = 1
    for i in dic:
        if dic[i] == 1:
            content[str(ind)] = str(dic[i]) + " incident of " + str(i).lower() + ','
        else:
            content[str(ind)] = str(dic[i]) + " incidents of " + str(i).lower() + ',\n'
        ind += 1
    content['12'] = " within {} kilometers of the inputted address. ".format(request.form['km'])
    content['13'] = "There were {} crimes during the day and {} crimes during the night.".format(day_crimes, night_crimes)

    return render_template("search.html",content=content)

@app.route('/graphs', methods=['POST'])
def graphs():
    address = request.form['input1']
    parts = address.split(',')
    crime = request.form['crime']
    if (not " Atlanta" in  parts) or (not " GA" in parts):
        return "Must input an Atlanta address."
    if not request.form['km1']:
        return "Please enter a radius."
    geocode_result = gmaps_key.geocode(address)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lng = geocode_result[0]["geometry"]["location"]["lng"]
    lats = df['Latitude'].tolist()
    lngs = df['Longitude'].tolist()
    crimes = df['UCR_Literal'].tolist()
    dates = df['Possible_Date'].tolist()


    dic = {'2009':0, '2010':0, '2011':0, '2012':0, '2013':0, '2014':0, '2015':0, '2016':0, '2017':0}

    for i,j,k,l in zip(lats,lngs,crimes,dates):
        if (distance(lat,lng,i,j) < int(request.form['km1'])) and str(k) == str(crime):
            if str(i).split('-')[0] != '2008':
                try:
                    dic[str(l).split('-')[0]] += 1
                except:
                    pass

    img = io.BytesIO()

    plt.clf()
    plt.plot(['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017'],[dic['2009'],dic['2010'],dic['2011'],dic['2012'],dic['2013'],dic['2014'],
    dic['2015'],dic['2016'],dic['2017'],])
    plt.title("Incidents of {} in a {} km Radius".format(request.form['crime'], request.form['km1']))
    plt.xlabel("Years")
    plt.ylabel("# of Crimes")
    plt.savefig(img, format='png')

    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()
    content = {'plot_url': plot_url}


    #return '<img src="data:image/png;base64,{}">'.format(plot_url)
    return render_template("graphs.html",content=content)
