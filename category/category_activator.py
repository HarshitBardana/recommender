def category_activator(basket):
    ### basket: a list with the user input ingredients. (ingredients containing spaces are NOT sqeezed yet.)
    ### This function returnes a list with activated categories
    #Predefined List of Ingredients with Highest Frequency in Category
    breads_activator = ['oil', 'coriander leaf', 'wheat flour', 'all purpose flour', 'onion', 'cumin seed', 'green chilli', 'clarified butter', 'red chilli powder', 'butter', 'garam masala', 'ginger', 'garlic', 'sugar', 'yogurt', 'milk', 'potato', 'turmeric powder', 'green chilly', 'turmeric']
    cake_activator = ['sugar', 'butter', 'vanilla essence', 'egg', 'all purpose flour', 'cream', 'baking powder', 'cocoa powder', 'milk', 'baking soda', 'oil', 'chocolate', 'brown sugar', 'lemon', 'caster sugar', 'cinnamon', 'buttermilk', 'sour cream', 'cheese', 'hazelnut']
    pizza_activator = ['onion', 'mozzarella', 'tomato', 'garlic', 'red pepper', 'chicken', 'olive oil', 'kidney bean', 'cilantro', 'oil', 'black pepper', 'capsicum', 'tomato paste', 'oregano', 'cheddar cheese', 'sugar', 'pizza sauce', 'jack cheese', 'black bean', 'all purpose flour']
    rice_activator = ['rice', 'onion', 'clove', 'cinnamon', 'oil', 'cumin seed', 'bay leaf', 'coriander leaf', 'clarified butter', 'mint leaf', 'garam masala', 'green cardamom', 'cardamom', 'ginger garlic paste', 'yogurt', 'tomato', 'red chilli powder', 'curd', 'chicken', 'lemon']

    #----Mapping activators to actual categories---#
    cat_activator = {'breads':breads_activator, 'cake': cake_activator, 'pizza': pizza_activator, 'rice':rice_activator }
    activated_cat = []

    #Activating Categories if Ingredient is present in basket and Activator List
    for item in basket:
        for key in cat_activator.keys():
            if item in cat_activator.get(key):
                if key not in activated_cat:
                    activated_cat.append(key)

    return activated_cat
        

    