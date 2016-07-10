""

from collections import Counter
import pickle

import graphlab as gl
import numpy as np
import pandas as pd

class GroupRecommender(object):
    ""
    
    def __init__(self, cuisine_sf, dict_cuisine_items):
        self.cuisine = gl.SFrame(cuisine_sf)
        self.cuisine_items = dict_cuisine_items
    
    def recommend(self, group_list):
        group_name = "_".join(group_list)
        
        sf_avg_user = self.cuisine.filter_by(group_list, "user_id") \
                                  .groupby(key_columns='item_id',
                                           operations={'rating': gl.aggregate.MEAN('rating')})  
        
        sf_avg_user.add_column(gl.SArray([group_name] * len(sf_avg_user)), "user_id")
#         print sf_avg_user
        
        sf_new = self.cuisine.append(sf_avg_user)
        
        model = gl.recommender.create(sf_new, target='rating')
    
        results = model.recommend([group_name], exclude_known=False)
#         print results
        result_cuisine = results["item_id"][:3]
    
        option_list = []
        for cuisine in result_cuisine:
            
            sf_items = gl.SFrame(self.cuisine_items[cuisine])
            model_items = gl.recommender.create(sf_items, target='rating')

            results_items = model_items.recommend(group_list, exclude_known=False, k = 2)
    #         print results_items
                
            if cuisine == "Pizza":
                group_size = len(group_list)
                num_pizza = int(group_size / 1.5)
                item_results = [item for item, count in Counter(results_items["item_id"]).most_common()][:num_pizza]
                option_list.append(("Pizza Party!", item_results))
        
            else:
                group_size = len(group_list)
                item_results = [item for item, count in Counter(results_items["item_id"]).most_common()][:group_size]
                option_list.append((cuisine, item_results))

        return option_list

if __name__ == "__main__":

    data_cuisine = pickle.load(open("data/user_by_cuisine_ratings.pkl", 'rb'))
    df_cuisine = pd.DataFrame(data_cuisine)
    data_items = pickle.load(open("data/user_by_cuisine_by_dish_ratings.pkl", 'rb'))
    model = GroupRecommender(df_cuisine, data_items)
    
    group_list = np.random.choice(df_cuisine["user_id"].unique(), size = 2, replace=False)
    result = model.recommend(group_list)

    print("Group Order for " + ", ".join(group_list))
    print("Computing recommendation...")
    print("Recommendation: ")
    print(result)
