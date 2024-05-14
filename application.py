from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
#import pymongo
import csv
import os
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By # This needs to be used 

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            DRIVER_PATH = r"chromedriver.exe"

            # Initialize the Chrome WebDriver
            driver = webdriver.Chrome(DRIVER_PATH)
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            driver.get(flipkart_url)
            flipkartPage = driver.page_source
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class":"cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            driver.get(productLink)
            prodRes= driver.page_source
            driver.quit()
            prod_html = bs(prodRes, "html.parser")
            commentboxes = prod_html.find_all("div", {"class":"RcXBOT"})

            filename = searchString + ".csv"
            with open(filename, "w", newline='', encoding='utf-8') as fw:
                headers = ["Product","Customer Name", "Rating","Heading","Comment"]
                writer = csv.DictWriter(fw, fieldnames=headers)
                writer.writeheader()

                reviews = []

                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all("p",{"class":"_2NsDsF AwS1CA"})[0].text
                    except Exception as e:
                        name = 'Name not found: ' + str(e)

                    try:
                        rating = commentbox.div.div.div.div.text
                    except Exception as e:
                        rating = 'Rating not found: ' + str(e)

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except Exception as e:
                        commentHead = 'Comment Head not found: ' + str(e)

                    try:
                        comtag = commentbox.div.div.find_all('div',{"class":""})
                        custComment = comtag[0].div.text
                    except Exception as e:
                        custComment = 'Comment not found: ' + str(e)

                    mydict = {"Product": searchString, "Customer Name": name, "Rating": rating, "Heading": commentHead, "Comment": custComment}
                    reviews.append(mydict)
                   
                writer.writerows(reviews)

            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)    