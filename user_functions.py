import pymongo


# initialize my db connection
client = pymongo.MongoClient(
    "mongodb+srv://developer:developer01@biomedic0.afwttjf.mongodb.net/?retryWrites=true&w=majority"
)
db = client["biomedic"]

# # initialize my db connection
# client = pymongo.MongoClient(
#     "mongodb+srv://rchatbots:rchatbots01@rchatbots0.rkfzl.mongodb.net/?retryWrites=true&w=majority"
# )
# db = client["biomedic-dev"]
userReg_collection = db["user_data"]


def register_user(body):

  response = {}
  fb_id = body["originalDetectIntentRequest"]["payload"]["data"]["sender"][
      "id"]
  source = body["originalDetectIntentRequest"]["source"]
  parameters = body["queryResult"]["parameters"]
  user_payload = {"fb_id": fb_id, "data": parameters}

  # result = userReg_collection.insert_one(user_payload)
  result = userReg_collection.find_one({"fb_id": fb_id})

  print(result)
  if result is None:
    result = userReg_collection.insert_one(user_payload)
    response = {
        "followupEventInput": {
            "name": "user_registered",
            "languageCode": "en-US"
        }
    }
  else:
    response = {
        "followupEventInput": {
            "name": "user_exists",
            "languageCode": "en-US"
        }
    }

  return response


def verify_user(body):

  response = {}

  # get the user facebook Id
  fb_id = body["originalDetectIntentRequest"]["payload"]["data"]["sender"][
      "id"]

  # find the user using their facebook Id
  result = userReg_collection.find_one({"fb_id": fb_id})

  if result is None:
    response = {
        "followupEventInput": {
            "name": "register_user",
            "languageCode": "en-US"
        }
    }
  else:
    response = {
        "followupEventInput": {
            "name": "user_exists",
            "languageCode": "en-US"
        }
    }

  return response


body = {
    "responseId":
    "e3f734fe-482c-4095-82ed-a32429fbddee-d5f6109d",
    "queryResult": {
        "queryText":
        "hi",
        "action":
        "register",
        "parameters": {
            "hepatitis_status": "negative",
            "hiv_status": "positive",
            "tb_status": "negative",
            "id": 35651010.0,
            "age": 25.0,
            "gender": "male"
        },
        "allRequiredParamsPresent":
        True,
        "fulfillmentMessages": [{
            "text": {
                "text": ["hi from biomedic chatbot"]
            },
            "platform": "FACEBOOK"
        }],
        "outputContexts": [{
            "name":
            "projects/bio-medc-bot-dev-ixvr/agent/sessions/87694359-ed0a-3d8f-94ca-1f3ef24153d3/contexts/__system_counters__",
            "parameters": {
                "no-input": 0.0,
                "no-match": 0.0
            }
        }],
        "intent": {
            "name":
            "projects/bio-medc-bot-dev-ixvr/agent/intents/c7e77f2f-cca7-48a6-aeb3-37393e10771d",
            "displayName": "Default Welcome Intent"
        },
        "intentDetectionConfidence":
        1.0,
        "languageCode":
        "en"
    },
    "originalDetectIntentRequest": {
        "source": "facebook",
        "payload": {
            "data": {
                "recipient": {
                    "id": "210972265431842"
                },
                "message": {
                    "mid":
                    "m_b-pE_U9qWPSWazZn4CzPrh5NQaxcUefXNorRs6YpoFVZRVrjrTgPl_S78bXOi6cccNNK6rMHL9XGrDkM8vN-gg",
                    "text": "hi"
                },
                "sender": {
                    "id": "25312035848396000"
                },
                "timestamp": "1705239823888"
            }
        }
    },
    "session":
    "projects/bio-medc-bot-dev-ixvr/agent/sessions/87694359-ed0a-3d8f-94ca-1f3ef24153d3"
}

register_user(body)
