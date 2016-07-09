import graphlab as gl

class group_recommender(object):
    def __init__(self, cuisine_sf, dict_cuisine_items):
        self.cuisine = cuisine_sf
        self.cuisine_items = dict_cuisine_items
    
    def recommend(self, group_list):
        group_name = "_".join(group_list)
        
        sf_avg_user = self.cuisine.filter_by(group_list, "user_id") \
                                  .groupby(key_columns='item_id',
                                           operations={'rating': gl.aggregate.MEAN('rating')})  
        
        sf_avg_user.add_column(gl.SArray([group_name] * len(sf_avg_user)), "user_id")
        
        sf_new = sf.append(sf_avg_user)
        
        model = gl.recommender.create(sf_new, target='rating')
    
        results = model.recommend([group_name], exclude_known=False)
        result_cuisine = results["item_id"][0]
        
        sf_items = self.cuisine_items[result_cuisine]
        model_items = gl.recommender.create(sf_items, target='rating')
        
        results_items = model_items.recommend(group_list)
        return results_items[["user_id", "item_id"]].to_numpy().tolist()