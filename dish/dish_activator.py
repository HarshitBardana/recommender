def dishActivator(data_filtered,basket):
    ### data_filtered: dataframe with binary values for ingredients
    ### basket: user input ingredients (all the spaces are removed. i.e. 'all purpose flour' mapped to 'allpurposeflour')
    from sklearn.metrics import jaccard_score
    import warnings
    warnings.filterwarnings('ignore')
    import pandas as pd

    data_filtered = data_filtered.set_index('dish')

    #creating a dataframe of basket in the sequenced version of data_filtered
    basket_df = pd.DataFrame(columns=list(data_filtered.drop(['dish_id','sub_category','sub_category_id'],axis =1).columns),index = ["Ingredients"])
    for item in basket :
        try :
            if item in data_filtered.drop(['dish_id','sub_category','sub_category_id'],axis =1).columns :
                basket_df.at["Ingredients",item] = 1.0
        except :
            continue
    basket_df.fillna(0.0, inplace = True)
    basket_df = basket_df.astype(float)


    jaccard_scores = []
    
    #creating an extra column of Jaccard score in in data_filtered
    jaccard_df = data_filtered.drop(['dish_id','sub_category','sub_category_id'],axis =1)

    #a dictionary holding dish name as key and jaccard score as value
    final_dict = {}
    counter = 0
    for row in jaccard_df.index:
        score = jaccard_score(jaccard_df.loc[row].values.tolist(), basket_df.loc["Ingredients"].values.tolist())
        final_dict[counter] = {'name':row,'score':score}
        jaccard_scores.append(score)
        counter=counter + 1
    jaccard_df["Jaccard_Scores"] = jaccard_scores 
    data_filtered["Jaccard_Scores"] = jaccard_scores 

    # filtering top 5 dishes with highest Jaccard score
    value = dict(sorted(final_dict.items(), key=lambda x: x[1]['score'], reverse=True)[:5])

    # framing into a usable dictionary format 
    final_result = {i: v for i, v in enumerate(value.values())}
    
    return final_result, data_filtered
