#importing packages
from flask import Flask, render_template, request, jsonify, json #flask app and rendering templates
import pandas as pd #reading dataframses
import sqlite3 #accessing database
from category.category_activator import *
from subcategory.subcategory_activator import *
from dish.dish_activator import *
from ingredients.ingredients_activator import *
from ingredients.ingredients_shelf import *
import warnings
warnings.filterwarnings('ignore') #suppressing errors
import json



#--------------main app starts---------------------#
app = Flask(__name__)
#--------------main app ends---------------------#


#--------------database connection starts---------------------#
def createDatabaseConnection():
  connection = sqlite3.connect('grocery_recommender.sqlite')
  return connection
#--------------database connection ends---------------------#


#----------------rendering landing page starts----------------------#
@app.route('/')
def index():
 return render_template('index_recommender.html')
#----------------rendering landing page ends----------------------#


#----------------Fetching Ingredients starts----------------------#
@app.route('/getIngredients', methods=['POST'])

#Fetching Ingredients for Autocomplete
def getIngredients():

    '''
    ***************
        #Pre-requites for calling function
          -> id :- unique identifier
          -> name :- to be displayed for autocomplete

    *****************
    '''
    #Querying Database
    connection = createDatabaseConnection()
    cursor = connection.cursor()
    records = cursor.execute("SELECT * FROM ingredients") #Fetching Ingredient Names

    temp = cursor.fetchall()
    li =[]
    for c,b,o in temp:
      dic = {}
      dic['id'] = c
      dic['name'] = b
      li.append(dic)
    return json.dumps(li)

#----------------Fetching Ingredients ends----------------------#

#----------------Generating Recommendations starts----------------------#
@app.route('/getRecommendation', methods=['POST'])

#Getting Ingredients and Dishes for Recommendation
def getRecommendation():

    #Accessing Data from Ajax Call    
 
    data = request.get_json()
    
    list_of_ingredients = data['x']
    

    if list_of_ingredients!='':
      basket = []
      
      #Storing Ingredients added in cart in basket
      for ingredients in list_of_ingredients:
        for key, value in ingredients.items():
          if key == 'name':
            if value not in basket:
              basket.append(value)

      if len(basket)>1:
        
        #Calling Category Activators
        '''
          ***************
            #Pre-requites for called function
            -> basket :- list of ingredients added in cart

            #Pre-requites for calling function
            -> activatedCategories :- list of category activators

          ***************** 
        '''
        activatedCategories = category_activator(basket)
        
    
        if len(activatedCategories)>0:
          
          #Querying Database
          connection = createDatabaseConnection()
          connection.row_factory = sqlite3.Row  
          cursor = connection.cursor()
          listToStr = ','.join(map("'{0}'".format, activatedCategories))
          
          query  = "SELECT * FROM category_master WHERE category_name IN ("+listToStr+")" #Fetching Category IDs
          cursor.execute(query)
          rows = cursor.fetchall()
          categoryIds = []
          
          for row in rows:
            category_id = row['category_id']
            if category_id not in categoryIds:
              categoryIds.append(category_id)
          

          if len(categoryIds)>0:
            
            #Querying Database
            connection = createDatabaseConnection()
            connection.row_factory = sqlite3.Row  
            cursor = connection.cursor()
            
            listToStr = ','.join(map("'{0}'".format, categoryIds))
            query  = "SELECT * FROM subcategory_ranks WHERE category_id IN ("+listToStr+")" #Fetching SubCategory Ranks

            cursor.execute(query)
            rows = cursor.fetchall()

            subCategoryRanks = {}
            subCategoryCounter = 0

            #Pushing the Query Result to Dictonary
            for row in rows:
              subCategoryRanks[subCategoryCounter] = dict(row)
              subCategoryCounter = subCategoryCounter+1

            #Converting the subcategory ranks dictonary to dataframe
            subCat_Df = pd.DataFrame.from_dict(subCategoryRanks, orient ='index')
            
            

            if(len(subCat_Df.index)>0):
              
              #Removing Space from Ingredients in Cart to Compare with Column Names
              basket = [x.replace(' ','') for x in basket]

              #Calling Sub-Category Activators
              '''
                ***************
                  #Pre-requites for called function
                  -> subCat_Df :- Dataframe with Ranks of Ingredients
                  -> basket :- list of ingredients added in cart

                  #Pre-requites for calling function
                  -> activatedCategories :- list of sub-category activated IDs

                ***************** 
              '''
              activatedSubCategories = sub_category_activator(subCat_Df,basket)

              if len(activatedSubCategories)>0:
                
                #Querying Database
                connection = createDatabaseConnection()
                connection.row_factory = sqlite3.Row  
                cursor = connection.cursor()
                subCatIds = ','.join([str(elem) for elem in activatedSubCategories])

                #Fetching Binary Dishes; 1- Ingredient Present, 0- Ingredient Not Present
                query  = "SELECT * FROM binary_dishes WHERE sub_category_id IN ("+subCatIds+")" 
                cursor.execute(query)
                rows = cursor.fetchall()
                
                
                dishRanks = {}
                dishCounter = 0

                #Pushing Query Result to Dictonary
                for row in rows:
                  dishRanks[dishCounter] = dict(row)
                  dishCounter = dishCounter+1


                #Converting the binary dish dictonary to dataframe
                dish_df = pd.DataFrame.from_dict(dishRanks, orient ='index') 
                
                if(len(dish_df.index))>0:

                  #Calling Sub-Category Activators
                  '''
                    ***************
                      #Pre-requites for called function
                      -> dish_df :- Dataframe with Binary Values of Ingredients
                      -> basket :- list of ingredients added in cart

                      #Pre-requites for calling function
                      -> activatedDishes :- list of dishes activated with Jaccard Scores

                    ***************** 
                  '''

                  activatedDishes,filteredDish_df = dishActivator(dish_df,basket)

                  
                  if(len(activatedDishes)>0 and len(filteredDish_df.index)>0):
                    top_ingredients = recommendIngredients(activatedDishes,filteredDish_df,basket) 
                    
                    

                    if(len(top_ingredients)>0):
                      
                      mapped_ing_name_list = []
                      for i in top_ingredients['ingredients']:
                        top_ing_name = top_ingredients['ingredients'][i]
                        if top_ing_name not in mapped_ing_name_list:
                          mapped_ing_name_list.append(top_ing_name)
                      
                      

                      if(len(mapped_ing_name_list)>0):
                        #Querying Database
                        connection = createDatabaseConnection()
                        connection.row_factory = sqlite3.Row  
                        cursor = connection.cursor()
                        mappedNames = ','.join("'{0}'".format(x) for x in mapped_ing_name_list)

                        #Fetching Real Ingredients Name
                        query  = "SELECT ingredients FROM ingredients WHERE mapping_ingredients IN ("+mappedNames+")" 
                        cursor.execute(query)
                        rows = cursor.fetchall()
                        
                        
                        ing_real_names = {}
                        ing_counter = 0

                        for row in rows:
                          ing_real_names[ing_counter] = dict(row)['ingredients']
                          ing_counter = ing_counter+1
                        
                        top_ingredients['ingredients'] = ing_real_names
                       
                        result = {'status':1,'result':top_ingredients}
                      else:
                        result = {'status':0}
                    else:
                      result = {'status':0}
                  else:
                    result = {'status':0}
                else:
                  result = {'status':0}  
              else:
                result = {'status':0}
            else:
              result = {'status':0}
          else:
            result = {'status':0}
        else:
          result = {'status':0}
      else:
        result = {'status':0}  
    else:
      result = {'status':0}

    

    return json.dumps(result)

#----------------Generating Recommendations ends----------------------#

#----------------Shelf of Ingredients starts----------------------#
@app.route('/sendDishes', methods=['POST'])

def sendDishes():
   #Accessing Data from Ajax Call
    dish_id_list = request.form.getlist("dish[]", type=int)
    basket = request.form['basket']
    basket = list(basket.split(","))
    
    #Removing Space from Ingredients in Cart to Compare with Column Names
    basket = [x.replace(' ','') for x in basket]


    #Querying Database
    connection = createDatabaseConnection()
    connection.row_factory = sqlite3.Row  
    cursor = connection.cursor()
    dish_ids = ','.join("'{0}'".format(x) for x in dish_id_list)

    #Fetching Real Ingredients Name
    query  = "SELECT * from binary_dishes WHERE dish_id IN ("+dish_ids+")" 
    cursor.execute(query)
    rows = cursor.fetchall()
    
    userDishes = {}
    userDishCounter = 0

    #Pushing Query Result to Dictonary
    for row in rows:
      userDishes[userDishCounter] = dict(row)
      userDishCounter = userDishCounter+1

    userDish_df = pd.DataFrame.from_dict(userDishes, orient ='index')
    shelf_ing = get_shelf(userDish_df,basket)

    if(len(shelf_ing)>0):
       #Querying Database
        # connection = createDatabaseConnection()
        # connection.row_factory = sqlite3.Row  
        # cursor = connection.cursor()

        for i in shelf_ing:
          shelf_mappedNames_list = (shelf_ing[i]['shelf'])
          mappedNames = ','.join("'{0}'".format(x) for x in shelf_mappedNames_list)

          #Fetching Real Ingredients Name
          query  = "SELECT ingredients FROM ingredients WHERE mapping_ingredients IN ("+mappedNames+")" 
          cursor.execute(query)
          rows = cursor.fetchall()
          #Pushing the Query Result to Dictonary
          temp_counter = 0
          temp_dict = {}
          for row in rows:
            temp_dict[temp_counter] = (dict(row)['ingredients'])
            temp_counter = temp_counter + 1
          
          list_real_names = []
          for j in temp_dict:
            name = temp_dict[j]
            if name not in list_real_names:
              list_real_names.append(name)
          
          shelf_ing[i]['shelf'] = list_real_names

        result = {'status':1,'response':shelf_ing}
    else:
      result = {'status':0}

    return json.dumps(result)

#----------------Shelf of Ingredients ends----------------------#

  

#--------------main app ends---------------------#


#--------------calling main app---------------------#
if __name__ == '__main__':

      app.run(debug=True)
#--------------calling main app ends---------------------#
