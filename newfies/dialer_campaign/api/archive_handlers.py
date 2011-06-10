#The code bellow is not used at the moment

class campaignsubscriberHandler(BaseHandler):
    """
    Campaign Subscriber Handler
    """
    model = CampaignSubscriber
    allowed_methods = ('GET',)
    fields = ('id', 'contact', 'name', 'description', 'status',
              'additional_vars',  ('campaign', ('name', 'status',)))

    @classmethod
    def content_length(cls, campaignsubscriber):
        return len(campaignsubscriber.content)

    @staticmethod
    def resource_uri(self):
        return ('campaignsubscriber', [' campaignsubscriber_id',])

    @throttle(1000, 1*60) # Throttle if more that 1000 times within 1 minute
    def read(self, request, campaign_id=None, contact=None):
        """
        Reads the status of subscriber added to a campaign
        
        **Attributes**
        
        campaign_id, contact
        
        **Attributes Details**
        
        - campaign_id : Campaign ID
        - contact : contact number of the subscriber
        
        **CURL Usage**
        
        curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/campaignsubscriber/%campaign_id%/
        
        curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/campaignsubscriber/%campaign_id%/%contact%/
        """
        try:
            obj_campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            resp = rc.BAD_REQUEST
            resp.write("The Campaign ID doesn't exist!")
            return resp
        
        base = CampaignSubscriber.objects
        if not contact :
            try :
                list_campaignsubscriber = base.get(id=campaign_id)
                return list_campaignsubscriber
            except :
                return rc.NOT_FOUND
        else:
            try :
                list_campaignsubscriber = base.get(id=campaign_id, contact=contact)
                return list_campaignsubscriber
            except :
                return rc.NOT_FOUND
