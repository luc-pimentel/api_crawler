import time
from decouple import config
from ._base import BaseAPI
from apify_client import ApifyClient


APIFY_API_KEY = config("APIFY_API_KEY", default=None)


class ApifyAPI(BaseAPI):
    def __init__(self):

        if APIFY_API_KEY is None:
            raise ValueError("APIFY_API_KEY not found in the .env file. Please add it to proceed.")

        self.client = ApifyClient(APIFY_API_KEY)

    def get_actors(self):
        return self.client.actors().list().items
    
    def run_actor(self, actor_id, **kwargs):
        actor_client = self.client.actor(actor_id)
        
        run_input = kwargs if kwargs else None
        my_actor_run = actor_client.start(run_input=run_input)
        
        return my_actor_run
    
    def get_run(self, run_id):
        return self.client.run(run_id).get()
    
    def get_run_results(self, run_id):
        return self.client.run(run_id).dataset().list_items().items
    

    def run_and_get_results(self, actor_id, **kwargs):
        run = self.run_actor(actor_id, **kwargs)
        

        run_id = run['id']


        while True:
            status = self.get_run(run_id)['status']
            if status == 'SUCCEEDED':
                break
            time.sleep(10)  # Wait for 10 seconds before checking again

        results = self.get_run_results(run_id)
        return results
