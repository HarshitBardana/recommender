
def sub_category_activator(data,basket):
### data: the dataframe with activated categories and rank matrix
### function will return the list of sub categories which are activated


    data = data.set_index('sub_category_id')
    import math

    #calculating sub category scores for sub categories
    sub_category_score = {}
    for item in basket:
        for sub_cat in data.index:
            try :
                sub_category_score[sub_cat] = sub_category_score.get(sub_cat,0) + (1/math.sqrt(data.at[sub_cat,item]))
            except :
                continue

    activated_sub_cat = []

    #Counting average of all subcategory scores as threshold to activate subcategory
    avg_sub_cat_score = sum(sub_category_score.values()) / len(sub_category_score)

    #activating subcategories which surpasses the threshold
    for key in list(sub_category_score.keys()):
        if sub_category_score.get(key) > avg_sub_cat_score:
            activated_sub_cat.append(key)

    return (activated_sub_cat)