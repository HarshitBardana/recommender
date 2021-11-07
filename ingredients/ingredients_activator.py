# def recommendIngredients(final_result, data_filtered, basket):
#     import pandas as pd
#     first_append = True
#     for i in final_result.values():
#         for dish in data_filtered.index:
#             if dish == list(i.values())[0]:
#                 if first_append:
#                     new = data_filtered[data_filtered.index == dish]
                    
#                     first_append=False
#                 else:
#                     new = new.append(data_filtered[data_filtered.index == dish], ignore_index = True)

#     new = new.drop(['dish_id','sub_category','sub_category_id'],axis =1)
#     topDishes_df = pd.DataFrame(new.groupby(by = new.index).sum())
#     topDishes_df = topDishes_df.drop('Jaccard_Scores', axis=1)
#     topDishes_df = topDishes_df/topDishes_df.sum(axis = 0)
#     topDishes_df.fillna(0,inplace = True)
#     sort = topDishes_df.max(axis = 0).sort_values(ascending = True)
#     counter = 0
#     mapping = {}
#     for j in range(len(sort)):
#         if (sort[j] != 0) and (sort.index[j] not in basket) and counter<5:
#             mapping[counter] = sort.index[j]
#             counter = counter+1
#         if counter == 5:
#             break
#     return mapping

def recommendIngredients(final_result, data_filtered, basket):
    ### final_result: a dictionary from dish_activator.py
    ### data_filtered: dataframe with binary ingredients and Jaccard scores of dishes. got data_filtered from dish_activator.py
    import pandas as pd

    # creating a dataframe 'new' which contains dishes from 'final_result'
    first_append = True
    for i in final_result.values():
        for dish in data_filtered.index:
            if dish == list(i.values())[0]:
                if first_append:
                    new = data_filtered[data_filtered.index == dish]
                    
                    first_append=False
                else:
                    new = new.append(data_filtered[data_filtered.index == dish], ignore_index = False)
    new = new.drop(['dish_id','sub_category','sub_category_id'],axis =1)

    # recommending top 5 most frequent ingredients from top 5 dishes (recommended ingredients would not be presented in basket)
    topDishes_df = pd.DataFrame(new.groupby(by = new.index).sum())
    topDishes_df = topDishes_df.drop('Jaccard_Scores', axis=1)
    topDishes_df = topDishes_df/topDishes_df.sum(axis = 0)
    topDishes_df.fillna(0,inplace = True)
    sort = topDishes_df.max(axis = 0).sort_values(ascending = True)
    
    # creating dictionary for recommending dishes and ingredients
    final_recommendation = {'dish':{}, 'ingredients':{}}

    # creating dictionary for holding dish name as key and it's no. of ingredients present in basket as values
    dishes = {}
    for i in topDishes_df.index:
        basket_dish_common = 0
        for n in topDishes_df.columns:
            if topDishes_df.at[i,n] != 0:
                for g in basket:
                    if n == g:
                        basket_dish_common = basket_dish_common+1
        dishes[i] = basket_dish_common
    
    # total no. of ingredients present in dishes
    no_of_ingredients_in_dish = new.drop('Jaccard_Scores', axis = 1).sum(axis = 1)

    # recommeding the dishes
    add_up = 0
    ghumao = 0
    for k,v in dishes.items():
        # recommend the dish only if length of basket ingredients follows following condition
        if v <= (no_of_ingredients_in_dish[ghumao]*0.9):
            #print(k,v,no_of_ingredients_in_dish[ghumao])
            for d in data_filtered.index:
                if d == k:
                    final_recommendation['dish'][add_up] = {'id': int(data_filtered[data_filtered.index == d]['dish_id'][0]),'name':k}
                    add_up = add_up + 1
        ghumao = ghumao+1


    # setting up the top 5 ingredients to recommend
    counter = 0
    for j in range(len(sort)):
        if (sort[j] != 0) and (sort.index[j] not in basket) and counter<5:
            final_recommendation['ingredients'][counter] = sort.index[j]
            counter = counter+1
        if counter == 5:
            break
    
    return final_recommendation

