from bs4 import BeautifulSoup
import scrape_schema_recipe
import mysql.connector
import datetime
import requests
import math
import json
import os

class Database():
    def __init__(self):
        self.connector = mysql.connector.connect(
            host = "localhost",
            user = "test",
            passwd = "test",
            database = os.environ['DATABASE_NAME']
        )
        self.cursor = self.connector.cursor()
        
    def ensureConnected(self):
        if not self.connector.is_connected():
            self.connector = mysql.connector.connect(
                host = "localhost",
                user = "test",
                passwd = "test",
                database = os.environ['DATABASE_NAME']
            )
            self.cursor = self.connector.cursor()

    def login(self, content):
        self.ensureConnected()
        sql = "SELECT id, username, password, metric, notifications, storageLocations FROM Users WHERE username = %s"
        usr = (str(content['username']), )
        self.cursor.execute(sql, usr)
        result = self.cursor.fetchall()

        if len(result) == 0:
            payload = {
                'data' : 'Invalid username.'
            }
            return (json.dumps(payload), 401)
        else:
            if content['password'] == result[0][2]:
                payload = {
                    'data' : 'Successful login.',
                    'userID' : result[0][0],
                    'measureType' : result[0][3],
                    'notifPref' : result[0][4],
                    'locations' : result[0][5]
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    'data' : 'Incorrect password.'
                }
                return (json.dumps(payload), 401)

    def signUp(self,content):
        self.ensureConnected()
        # check if any user name or email address exist in the data base
            #if yes  
                #return 1 for name already in database
                #return 2 for email already in database
                #return 3 for name and email both in the database
            #if no
                #perform necessary operation to dump data in the database then
                #return 0 to confirm data successfully in database
        sql = "SELECT id FROM `Users` WHERE `Users`.`username` = %s"
        usrn = (str(content['username']),)
        self.cursor.execute(sql,usrn)
        result1 = self.cursor.fetchall()

        sqlTwo = "SELECT id FROM `Users` WHERE `Users`.`email` = %s"
        usre = (str(content['useremail']),)
        self.cursor.execute(sqlTwo,usre)
        result2 = self.cursor.fetchall()

        if len(result1) == 0 and len(result2) == 0:
            sql = "SELECT inventoryID FROM Users ORDER BY inventoryID DESC"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()

            if len(result) > 0:
                inventoryID = result[0][0] + 1
            else:
                inventoryID = 1

            storageLocations = {
                'locations' : ['Fridge', 'Freezer', 'Dry']
            }

            sqlInsert = "INSERT INTO Users (name, email, phone, username, password, inventoryID, storageLocations) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (content['name'], content['useremail'], content['phone'], content['username'], content['password'], inventoryID, json.dumps(storageLocations), )
            #inventoryID = result[0][0] + 1
            self.cursor.execute(sqlInsert, val)
            result = self.connector.commit()
            return (json.dumps(dict(data='0')), 200)
        elif(len(result1) != 0 and len(result2) != 0):
            return (json.dumps(dict(data='3')), 401)
        else:
            if(len(result1) != 0 ):
                return (json.dumps(dict(data='1')), 401)
            if(len(result2) != 0):
                return (json.dumps(dict(data='2')), 401)
                
    def addItem(self, content):
        self.ensureConnected()
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        inventoryID = result[0][0]

        sql = "SELECT id, itemname, quantity, measurement, location FROM Items WHERE inventoryID = %s AND itemname = %s AND measurement = %s AND location = %s"
        val = (inventoryID, content['itemname'], content['measurement'], content['location'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        if content['expDate'] == "":
            sql = "SELECT expiration FROM ShelfLife WHERE name = %s"
            val = (content['itemname'], )
            self.cursor.execute(sql, val)
            itemExpData = self.cursor.fetchall()

            if len(itemExpData) != 0:
                if content['location'] == 'Pantry':
                    if 'DOP_Pantry_Metric' != None:
                        min = itemExpData[0][0]['DOP_Pantry_Min']
                        metric = itemExpData[0][0]['DOP_Pantry_Metric']
                        if metric.lower() == 'days':
                            content['expDate'] = datetime.date.today() + timedelta(days=min)
                        elif metric.lower() == 'weeks':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 7))
                        elif metric.lower() == 'months':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 30))
                        elif metric.lower() == 'years':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 365))
                    elif 'Pantry_Metric' != None:
                        min = itemExpData[0][0]['Pantry_Min']
                        metric = itemExpData[0][0]['Pantry_Metric']
                        if metric.lower() == 'days':
                            content['expDate'] = datetime.date.today() + timedelta(days=min)
                        elif metric.lower() == 'weeks':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 7))
                        elif metric.lower() == 'months':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 30))
                        elif metric.lower() == 'years':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 365))
                elif content['location'] == 'Refrigerator':
                    if 'DOP_Refrigerate_Metric' != None:
                        min = itemExpData[0][0]['DOP_Refrigerate_Min']
                        metric = itemExpData[0][0]['DOP_Refrigerate_Metric']
                        if metric.lower() == 'days':
                            content['expDate'] = datetime.date.today() + timedelta(days=min)
                        elif metric.lower() == 'weeks':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 7))
                        elif metric.lower() == 'months':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 30))
                        elif metric.lower() == 'years':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 365))
                    elif 'Refrigerate_Metric' != None:
                        min = itemExpData[0][0]['Refrigerate_Min']
                        metric = itemExpData[0][0]['Refrigerate_Metric']
                        if metric.lower() == 'days':
                            content['expDate'] = datetime.date.today() + timedelta(days=min)
                        elif metric.lower() == 'weeks':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 7))
                        elif metric.lower() == 'months':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 30))
                        elif metric.lower() == 'years':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 365))
                elif content['location'] == 'Freezer':
                    if 'DOP_Freeze_Metric' != None:
                        min = itemExpData[0][0]['DOP_Freeze_Min']
                        metric = itemExpData[0][0]['DOP_Freeze_Metric']
                        if metric.lower() == 'days':
                            content['expDate'] = datetime.date.today() + timedelta(days=min)
                        elif metric.lower() == 'weeks':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 7))
                        elif metric.lower() == 'months':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 30))
                        elif metric.lower() == 'years':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 365))
                    elif 'Freeze_Metric' != None:
                        min = itemExpData[0][0]['Freeze_Min']
                        metric = itemExpData[0][0]['Freeze_Metric']
                        if metric.lower() == 'days':
                            content['expDate'] = datetime.date.today() + timedelta(days=min)
                        elif metric.lower() == 'weeks':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 7))
                        elif metric.lower() == 'months':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 30))
                        elif metric.lower() == 'years':
                            content['expDate'] = datetime.date.today() + timedelta(days=(min * 365))
            else:
                content['expDate'] = datetime.date.today() + datetime.timedelta(days=3)

        if len(result) == 0:
            useData = {
                "purchased" : [
                    {
                        "date" : datetime.datetime.now().strftime("%Y-%m-%d"),
                        "quantity" : content["quantity"]
                    }
                ],
                "purchasedTotal" : content["quantity"],
                "used" : [],
                "usedTotal" : 0,
                "wasted" : [],
                "wastedTotal" : 0
            }

            sql = "INSERT INTO FoodUse (itemname, measurement, `usage`) VALUES (%s, %s, %s)"
            val = (content['itemname'], content['measurement'], json.dumps(useData), )
            self.cursor.execute(sql, val)
            result = self.connector.commit()

            sql = "SELECT id FROM FoodUse ORDER BY id DESC;"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            useID = result[0][0]

            sql = "INSERT INTO Items (inventoryID, itemname, expiration, quantity, measurement, location, useID) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (inventoryID, content['itemname'], content['expDate'], content['quantity'], content['measurement'], content['location'], useID, )
            self.cursor.execute(sql, val)
            result = self.connector.commit()
        else:
            itemID = result[0][0]

            sql = "UPDATE Items SET quantity = %s WHERE id = %s"
            val = ((float(content['quantity']) + float(result[0][2])), itemID, )
            self.cursor.execute(sql, val)
            result = self.connector.commit()

            sql = "SELECT useID FROM Items WHERE id = %s"
            val = (itemID, )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            useID = result[0][0]

            sql = "SELECT `usage` FROM FoodUse WHERE id = %s"
            val = (useID, )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()

            purchased = {
                'date' : datetime.datetime.now().strftime("%Y-%m-%d"),
                'quantity' : content['quantity']
            }

            useData = json.loads(result[0][0])
            useData['purchased'].append(purchased)
            useData['purchasedTotal'] = float(useData['purchasedTotal']) + float(content['quantity'])

            sql = "UPDATE FoodUse SET `usage` = %s WHERE id = %s"
            val = (json.dumps(useData), useID, )
            self.cursor.execute(sql, val)
            result = self.connector.commit()

        return (json.dumps(dict(data='Item added.')), 200)

    def getItem(self, content):
        self.ensureConnected()
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        inventoryID = result[0][0]

        sql = "SELECT id, itemname, expiration, quantity, measurement, location FROM Items WHERE inventoryID = %s"
        val = (inventoryID, )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        for i in result:
            if i[1] == content['itemname']:
                payload = {
                    'data' : 'Successfully pulled item from inventory.',
                    'item' : dict(itemID=i[0], itemname=i[1], expDate=i[2], quantity=i[3], measurement=i[4], location=i[5])
                }
                return (json.dumps(payload, default=str), 200)
        return (json.dumps(dict(data="Could not pull item.")), 401)

    def delItem(self, content):
        self.ensureConnected()
        sql = "SELECT id, itemname, quantity, measurement, location, useID FROM Items WHERE id = %s"
        val = (content['itemID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        if len(result) is not 0:
            newQuantity = result[0][2] - float(content['quantity'])
        
            if newQuantity <= 0:
                #sql = "DELETE FROM Items WHERE id = %s"
                sql = "UPDATE Items SET quantity = %s WHERE id = %s"
                val = (0, content['itemID'], )
            else:
                sql = "UPDATE Items SET quantity = %s WHERE id = %s"
                val = (newQuantity, content['itemID'], )
                
            useID = result[0][5]
            
            sql = "SELECT `usage` FROM FoodUse WHERE id = %s"
            val= (useID, )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            
            useData = json.loads(result[0][0])
            
            if content['Used'] == 'used':
                used = {
                    "date" : datetime.datetime.now().strftime("%Y-%m-%d"),
                    "quantity" : content["quantity"]
                }
                useData['used'].append(used)
                useData['usedTotal'] = float(useData['usedTotal']) + float(content['quantity'])
                
                sql = "UPDATE FoodUse SET `usage` = %s WHERE id = %s"
                val = (json.dumps(useData), useID, )
                self.cursor.execute(sql, val)
                result = self.connector.commit()
            else:
                exp = {
                    "date" : datetime.datetime.now().strftime("%Y-%m-%d"),
                    "quantity" : content["quantity"]
                }
                useData['wasted'].append(exp)
                useData['wastedTotal'] = float(useData['wastedTotal']) + float(content['quantity'])
                
                sql = "UPDATE FoodUse SET `usage` = %s WHERE id = %s"
                val = (json.dumps(useData), useID, )
                self.cursor.execute(sql, val)
                result = self.connector.commit()
        
            self.cursor.execute(sql, val)
            self.connector.commit()
        
            return (json.dumps(dict(data='Item deleted.')), 200)
        else:
            return (json.dumps(dict(data='Item does not exist')), 401)

    def getInventory(self, content):
        self.ensureConnected()
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        inventoryID = result[0][0]

        sql = "SELECT id, useID, itemname, expiration, quantity, measurement, location FROM Items WHERE inventoryID = %s ORDER BY itemname"
        val = (inventoryID, )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        temp = []
        for i in result:
            temp.append(dict(itemID=i[0], useID=i[1], itemname=i[2], expDate=i[3], quantity=i[4], measurement=i[5], location=i[6]))

        payload = {
            'data' : temp
        }
        
        if len(temp) == 0:
            return (json.dumps(dict(data='Inventory is currently empty.'), default=str), 401)
        else:
            return (json.dumps(payload, default=str), 200)

    def searchItem(self, content):
        self.ensureConnected()
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        inventoryID = result[0][0]
        
        sql = "SELECT id, useID, itemname, expiration, quantity, measurement, location FROM Items WHERE itemname LIKE %s AND inventoryID = %s"
        val = ('%' + content['itemname'] + '%', inventoryID, )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        temp = []
        for i in result:
            temp.append(dict(itemID=i[0], useID=i[1], itemname=i[2], expDate=i[3], quantity=i[4], measurement=i[5], location=i[6]))
        
        payload = {
            'data' : temp
        }
        
        if len(temp) == 0:
            return (json.dumps(dict(data='Item not found in inventory.'), default=str), 401)
        else:
            return (json.dumps(payload, default=str), 200)

    def getReccRecipes(self, content):
        self.ensureConnected()
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        inventoryID = result[0][0]

        sql = "SELECT (itemname) FROM Items WHERE inventoryID = %s ORDER BY expiration"
        val = (inventoryID, )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        searchUrl = 'https://www.foodnetwork.com/search/'

        for i in range(0, 5):
            if " " in result[i][0]:
                result[i][0].replace(' ', '-')
            searchUrl = searchUrl + "-" + result[i][0]
        searchUrl = searchUrl + '-'

        searchRequest = requests.get(searchUrl)
        soup = BeautifulSoup(searchRequest.text)

        temp = []
        for link in soup.find_all('h3', 'm-MediaBlock__a-Headline'):
            recipeUrl = link.a.get('href')
            if 'recipes' in recipeUrl:
                url = "https:" + recipeUrl
                recipe_list = scrape_schema_recipe.scrape_url(url, python_objects=True)

                if len(recipe_list) != 0:
                    recipe = {
                        'name' : recipe_list[0]['name'],
                        'cookTime' : recipe_list[0]['cookTime'],
                        'recipeIngredient' : recipe_list[0]['recipeIngredient'],
                        'recipeInstructions' : recipe_list[0]['recipeInstructions']
                    }

                    temp.append(recipe)

        payload = {
            'data' : temp
        }

        return (json.dumps(payload, default=str), 200)
        
    def getPersonalRecipes(self, content):
        self.ensureConnected()
        sql = "SELECT recipeID FROM PersonalRecipes WHERE userID = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        temp = []

        if len(result) > 0:
            for i in result:
                sql = "SELECT id, name, description, servings, ingredients FROM Recipes WHERE id = %s"
                val = (i[0], )
                self.cursor.execute(sql, val)
                recipe = self.cursor.fetchall()
                
                with open('/home/mperry/debug.log', 'w') as debug:
                    debug.write(str(i))

                tempJson = {
                    'recipeID' : recipe[0][0],
                    'name' : recipe[0][1],
                    'description' : recipe[0][2],
                    'servings' : recipe[0][3],
                    'ingredients' : '{\"ingredients\" : ' + recipe[0][4].replace("\'", "\"") + '}'
                }
                
                temp.append(tempJson)
                
            payload = {
                'data' : temp
            }
            
            return (json.dumps(payload, default=str), 200)
        else:
            return (json.dumps(dict(data='Personal Recipes Empty.')), 401)

    def addRecipe(self, content):
        self.ensureConnected()
        sql = "INSERT INTO Recipes (name, description, servings, ingredients) VALUES (%s, %s, %s, %s)"
        val = (content['name'], content['description'], content['servings'], str(content['ingredients']), )
        self.cursor.execute(sql, val)
        result = self.connector.commit()

        sql = "SELECT id FROM Recipes ORDER BY id DESC LIMIT 1"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        sql = "INSERT INTO PersonalRecipes (userID, recipeID) VALUES (%s, %s)"
        val = (content['userID'], result[0][0], )
        self.cursor.execute(sql, val)
        result = self.connector.commit()

        return (json.dumps(dict(data='Recipe Added.')), 200)

    def delRecipe(self, content):
        self.ensureConnected()
        sql = "DELETE FROM PersonalRecipes WHERE recipeID = %s"
        val = (content['recipeID'], )
        self.cursor.execute(sql, val)
        result = self.connector.commit()

        sql = "DELETE FROM Recipes WHERE id = %s"
        val = (content['recipeID'], )
        self.cursor.execute(sql, val)
        result = self.connector.commit()

        return (json.dumps(dict(data='Recipe Deleted.')), 200)
        
    def getTrends(self, content):
        self.ensureConnected()
        
        # Get inventoryID
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        # Get items in user's inventory, along with its useID
        sql = "SELECT id, itemname, measurement, useID FROM Items WHERE inventoryID = %s"
        val = (result[0][0], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        userItems = result
        useData = []
        
        # Get usage information from FoodUse
        for x in userItems:
            sql = "SELECT `usage` FROM FoodUse WHERE id = %s"
            val = (x[3], )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchone()
            useData.append(json.loads(result[0]))
        
        # Trim items from usage history that are older than 6 months(technically 24 weeks)
        cutOffDate = datetime.date.today() - datetime.timedelta(days=168)
        
        for x in useData:
            index = 0
            for i in x['used']:
                if datetime.date.fromisoformat(i['date']) < cutOffDate:
                    x['used'].pop(index)
                index += 1
            indexToo = 0
            for j in x['wasted']:
                if datetime.date.fromisoformat(j['date']) < cutOffDate:
                    x['wasted'].pop(indexToo)
                indexToo += 1
                
        # Calculate (x,y) values to send to mobile application
        usedPoints = []
        usedPoints.append((0, 0))
        wastedPoints = []
        wastedPoints.append((0, 0))
        
        segmentBeginDate = cutOffDate
        segmentStopDate = cutOffDate + datetime.timedelta(days=14)
        xValue = 1

        largestYval = 0

        while(segmentStopDate <= datetime.date.today()):
            
            usedSegmentTotal = 0
            wastedSegmentTotal = 0

            for x in useData:
                for i in x['used']:
                    if datetime.date.fromisoformat(i['date']) > segmentBeginDate and datetime.date.fromisoformat(i['date']) <= segmentStopDate:
                        usedSegmentTotal += i['quantity']
                for j in x['wasted']:
                    if datetime.date.fromisoformat(j['date']) > segmentBeginDate and datetime.date.fromisoformat(j['date']) <= segmentStopDate:
                        wastedSegmentTotal += j['quantity']
                        
            usedPoints.append((xValue, usedSegmentTotal))
            wastedPoints.append((xValue, wastedSegmentTotal))
            
            if usedSegmentTotal > largestYval:
                largestYval = usedSegmentTotal
            if wastedSegmentTotal > largestYval:
                largestYval = wastedSegmentTotal

            xValue += 1
            segmentBeginDate = segmentBeginDate + datetime.timedelta(days=14)
            segmentStopDate = segmentStopDate + datetime.timedelta(days=14)
        
        # Return values to application
        payload = {
            'used' : usedPoints,
            'wasted' : wastedPoints,
            'largest' : largestYval
        }
        
        return (json.dumps(payload), 200)
        
    def generatePerfectLarder(self, content):
        self.ensureConnected()
        
        # Get inventoryID
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        # Get items in user's inventory, along with its useID
        sql = "SELECT id, itemname, measurement, useID FROM Items WHERE inventoryID = %s"
        val = (result[0][0], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        userItems = result
        useData = []
        
        # Get use data for each item and store in parallel list
        for x in userItems:
            sql = "SELECT id, itemname, measurement, `usage` FROM FoodUse WHERE id = %s"
            val = (x[3], )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchone()
            data = {
                "id" : result[0],
                "itemname" : result[1],
                "measurement" : result[2],
                "usage" : json.loads(result[3]),
                "useValues" : [],
                "useTotal" : 0
            }
            useData.append(data)
        
        # Only look at last 6 months of use data    
        cutOffDate = datetime.date.today() - datetime.timedelta(days=168)
        
        for x in useData:
            for index, i in enumerate(x['usage']['used']):
                if datetime.date.fromisoformat(i['date']) < cutOffDate:
                    x['used'].pop(index)
        
        #useValues = []
        segmentBeginDate = cutOffDate
        segmentStopDate = cutOffDate + datetime.timedelta(days=14)
                    
        while(segmentStopDate <= datetime.date.today()):

            for x in useData:
                usedSegmentTotal = 0
                
                for i in x['usage']['used']:
                    if datetime.date.fromisoformat(i['date']) > segmentBeginDate and datetime.date.fromisoformat(i['date']) <= segmentStopDate:
                        usedSegmentTotal += i['quantity']
                
                x['useValues'].append(usedSegmentTotal)
                x['useTotal'] += usedSegmentTotal

            segmentBeginDate = segmentBeginDate + datetime.timedelta(days=14)
            segmentStopDate = segmentStopDate + datetime.timedelta(days=14)
            
        for x in useData:
            x['need'] = x['useTotal'] / 12
            
        return useData
        
    def getPerfectLarder(self, content):
        self.ensureConnected()
        
        return (json.dumps(dict(data=self.generatePerfectLarder(content))), 200)

    def getShoppingList(self, content):
        self.ensureConnected()
        
        useData = self.generatePerfectLarder(content)
        
        # Calculate how much of which items are missing from inventory based upon perfect larder
        
        # Get inventoryID
        sql = "SELECT (inventoryID) FROM Users WHERE id = %s"
        val = (content['userID'], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        # Get items in user's inventory, along with its useID
        sql = "SELECT id, itemname, quantity, measurement FROM Items WHERE inventoryID = %s"
        val = (result[0][0], )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        
        userItems = result
        
        needsToDel = []

        #for index, x in enumerate(useData):
        index = 0
        for x in useData:
            for i in userItems:
                if x['itemname'] == i[1] and x['measurement'] == i[3]:
                    x['need'] -= i[2]
                    if x['need'] < 0.5:
                        needsToDel.append(index)
                    else:
                        x['need'] = math.ceil(x['need'])
            index += 1
        
        needsToDel.reverse()

        for x in needsToDel:
            useData.pop(x)
                
        # Return shopping list in json format
        return (json.dumps(dict(data=useData)), 200)

    def updateMeasurementSetting(self, content):
        self.ensureConnected()
        sql = "UPDATE Users SET metric = %s WHERE id = %s"
        val = (content['measureType'], content['userID'], )
        self.cursor.execute(sql, val)
        result = self.connector.commit()
        
        return (json.dumps(dict(data='Successfully Updated.')), 200)
        
    def updateStorageLocations(self, content):
        self.ensureConnected()
        sql = "UPDATE Users SET storageLocations = %s WHERE id = %s"
        val = (content['locations'], content['userID'], )
        self.cursor.execute(sql, val)
        result = self.connector.commit()
        
        return (json.dumps(dict(data='Successfully Updated.')), 200)
        
    def getItemsAboutToExpire(self,content):
        self.ensureConnected()
        currentDate = content["currentDate"]
        currentUserId = content['userID']
        oneWeekAheadDate = content["currentWeekAhead"]
        sql = "SELECT * FROM `Items` WHERE `Items`.`inventoryID` = %s AND `Items`.`expiration` >= %s AND `Items`.`expiration` < %s ORDER BY `userID` ASC"
        val = (currentUserId,currentDate,oneWeekAheadDate)
        self.cursor.execute(sql,val)
        result = self.cursor.fetchall()
        if(len(result) == 0):
             return (json.dumps(dict(data='empty')), 401)
        else:
            return (json.dumps(dict(data=result)), 200)
