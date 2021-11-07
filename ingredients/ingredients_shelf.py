def get_shelf(rec_dish_df,basket):
    final_dict = {}
    counter = 0 
    for dish_id in rec_dish_df.index:
        recommended_ingredients = []
        for col in rec_dish_df.columns:
            if (rec_dish_df.at[dish_id,col] == 1) and (col not in basket):
                recommended_ingredients.append(col)
        final_dict[counter] = {"dish":rec_dish_df.iloc[dish_id].dish, "shelf":recommended_ingredients}
        counter = counter+1
    return final_dict