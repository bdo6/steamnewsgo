#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

SteamAPIkey = 'FFF27E8F084794A0696BEE665C659A7A'
NewsApi = '793aa71cc8e24a6b8b35d95774e3c5d7'

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")
             
        template_values={}
        template_values['page_title']="Steam Username Search"
        template = JINJA_ENVIRONMENT.get_template('greetform.html')
        self.response.write(template.render(template_values))
 
def safeGet(url):   # Takes in a url
    try:
        return urllib2.urlopen(url)                 # Tries to return content of the url
    except urllib2.HTTPError, e:                    # Spits out 1 error for HTTPError
        print 'The server couln\'t fulfill the request.'
        print 'Error code: ', e.code
    except urllib2.URLError, e:                        # Gets another error for URLError
        print 'We failed to reach a server'
        print 'Reason: ', e.reason
    return None



class GreetResponseHandlr(webapp2.RequestHandler):
    def post(self):

        vals={} #dictionary
        tag = self.request.get('tag')
        vals['page_title']="Showing The Top 5 Games and News For: " + tag
                  
        if tag:
            tag = self.request.get('tag')
            vals['tag']=tag

            if tag.isdigit():     #User input if its a number or not #Passing only tag
                                 #By default it is true and it is a user id since there are numbers
                steamid = tag     # Assigning tag this variable since this is the steamid
            else:
                url= "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" +SteamAPIkey + "&vanityurl=" + tag
                data= safeGet(url)           #Random variable is used to save it. We can't use safeget as a variable bc its a function    #In this case, tag is the customURL
                logging.info(url)
                if data is not None: # Checking if we get anything back from safeget
                    idresolution=json.load(data)     #we are are assigning the result of json.load into a variable so that we can access it later.  #json.load... will give dicitonary                   # Checking if there is no error
                    if "steamid" in idresolution["response"]: # So we needed to have this set of if/else statements if no steam id is found for the input
                        steamid= idresolution["response"]["steamid"] #We can use steamid variable again and want to use because we need the steam id.
                                                                #We can use it again beacause it was previously used in the if statement but not in the else statement. It will get one or the other - it will never get "2" steamids
                    else:
                        logging.info("No steam id exist")
                        steamid = None
                        template = JINJA_ENVIRONMENT.get_template('greetform.html')
                        self.response.write(template.render(vals))
                        return # Stop if you get nothing back due to an error
                else:
                    logging.info("Got no data") # Print got no data to the terminal as it redirect it to the home apge rather than crash
                    steamid = None
                    template = JINJA_ENVIRONMENT.get_template('greetform.html')
                    self.response.write(template.render(vals))  #We are adding this else statement to account for cases the input by the user
                    return                                            # (tag) is incorrect, internet is down or any other errors. This isn't a case where there is no match like previously.
                                                                # This allows the application to still run without crashing
            logging.info("steamid: " + steamid) # Gives meaning to the numbers (the steam id)/ that is gives it a title

            vals["displayid"] = steamid # When load greet response, it will have steam id

            def getSteamGames(steamid):  #Function # There is no data we are just trying to get the list of games
                APIKEY = SteamAPIkey
                # What we are trying to do: http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=FFF27E8F084794A0696BEE665C659A7A&steamid=76561197960434622&format=json
                params = {'format': 'json', 'key': APIKEY, 'steamid': steamid, 'include_appinfo': 1, 'include_played_free_games': 1 } # 1 is as simple number represetation of true. 0 is false in steam
                paramstr = urllib.urlencode(params) # Takes dictionary of params and formats it to make it look like the URL
                baseurl = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
                steamrequest = baseurl + paramstr
                logging.info(steamrequest) # print out url

                response = safeGet(steamrequest) # Getting the data from the url $ urllib and urllib2 are used in python 2 for 2 different libraries
                                                # We need safeget to notify the user for errors, including if its a dictionary

                if response is not None:  # This is saying if the response has data
                    steamrequestjsonstr = response.read() # Taking the data form the url and reading it
                    gamelistdata = json.loads(steamrequestjsonstr) #takes the json and turns into a readable dictionary
                    return (gamelistdata)
                # if response is None: This is saying if response has no data

                #else: is not needed because if the program has data it will already have return something and not finish the function
                    #return None
                return None  # If we don't get any data, we get nothing # Having the return statement at end of the function is good practice because you are
                            # Guaranteed to return something rather than crashing if it nothing is return

            # Testing
            #logging.info(getSteamGames(steamid))


            def getGamingNews(gamename):
                APIKEY2 = NewsApi
                params = {'q': '"' + gamename + '" game', 'apiKey': NewsApi, 'sources':"ign,polygon,engadget,techradar", 'pageSize': 100, 'language': "en"}
                # Providing parameters into the url. These dictionaries do not have to be in order
                # NewsAPi wants double quotes. We are using single quotes so that python interpretes doesn't mix up the quotation characters
                paramstr = urllib.urlencode(params)
                baseurl = 'https://newsapi.org/v2/everything?'
                newsrequest = baseurl + paramstr
                logging.info(newsrequest)

                response = safeGet(newsrequest)

                if response is not None:
                    newsrequestjsontr = response.read()
                    newslistdata = json.loads(newsrequestjsontr) #Changing json file into a dictionary
                    return (newslistdata)

                return None


            ownedgames = getSteamGames(steamid) #Calling to get a list of the user's owned games. This is not part of the funciton above. It is using the function
            #to execute the code


            if ownedgames is not None:
                games = ownedgames["response"]["games"] #List of games owned by user not sorted
                topgames = sorted(games, key=lambda x: int(x["playtime_forever"]), reverse=True)[:5]
                            #results or w.e. (in this games) is here is the list you are sorting
                            #key is how do you sort it while lambda is the function that provides the result for the key
                            # x is each object we are sorting to
                #logging.info(pretty(topgames)) #Testing to see if it worked

                #newsgames= getGamingNews("age of empires: definitive edition") # check how picky api was vs one word like pokemon
                #logging.info(newsgames)

                gamingdictionary = {}           #Store the games (key is the name of the game) and its news (the news will be a list as a value)
                gameicons = {}
                topnames = []

                for game in topgames:
                    gamename = game["name"] # Accessing a dictionary or list. Curly braces are only for new dictionaries
                    topnames.append(gamename)  # Append is a function where it adds something to the end of the list. This creates a list
                    # of the games in order of # hrs played
                    gameicons[gamename] = 'http://media.steampowered.com/steamcommunity/public/images/apps/%s/%s.jpg' % (game["appid"], game["img_logo_url"]) # Now that we have the list of games we can
                    #plug in additional features like the logo's of the games
                    # Creates a url for the icon of each game and puts it into the gameicon's dictionary with key of the name. The name is the game name (not the info of each game). The info is what we used to
                    #get the data
                    gamenews = getGamingNews(gamename) #Accessing function
                    game["news"] = gamenews["articles"] #added so that we get news and attached to dictionary in top games
                    gamingdictionary[gamename] = gamenews["articles"] # We are storing the game and its news as a key value pair rather than having to start over each time with the for loop
                    # We are now adding to the new dictionary above gamingdictionary
                    #logging.info("/////////////////////////////////") #Seperator
                    #logging.info(pretty(gamenews))    # To print it out here. Note: Discovered that it searches titles inside the article even briefly mentioning it
                    # Ex: Getting metal gear survive news that mention 7 days to die due to them being both zombie survival
                    #We needed to attach all news to each game rather than overwriting it
               # logging.info(pretty(gamingdictionary)) # This was to test gaming dictionary. quotes not for variables
                # logging.info(pretty(topnames))
                vals['top_names'] = topnames
                vals['gaming_news'] = gamingdictionary # vals passes it to html
                vals['gameicons'] = gameicons
            else:
                return


            template = JINJA_ENVIRONMENT.get_template('greetresponse.html')
            self.response.write(template.render(vals))
        else:
            template = JINJA_ENVIRONMENT.get_template('greetform.html')
            self.response.write(template.render(vals))
 
application = webapp2.WSGIApplication([ \
                                      ('/steamresponse', GreetResponseHandlr),
                                      ('/.*', MainHandler)
                                      ], 
                                      debug=True)