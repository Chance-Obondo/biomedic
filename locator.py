from os import listdir
import pandas as pd
import string
import random
from datetime import date
import pymongo

bio_medic_client = "mongodb+srv://developer:<password>@biomedic0.afwttjf.mongodb.net/?retryWrites=true&w=majority"

# initialize my db connection
client = pymongo.MongoClient(
    "mongodb+srv://developer:developer01@biomedic0.afwttjf.mongodb.net/?retryWrites=true&w=majority"
)
db = client["biomedic"]

# client = pymongo.MongoClient(
#     "mongodb+srv://rchatbots:rchatbots01@rchatbots0.rkfzl.mongodb.net/?retryWrites=true&w=majority"
# )
# db = client["biomedic-dev"]

vouchers_collection = db["vouchers"]

data = pd.read_csv(
    'Service delivery cost per lot - Summary 2.xlsx - Health_Facilities.csv'
)

states = [
    'Abyei Administrative Area', 'Central Equatoria State',
    'Eastern Equatoria State', 'Lakes State', 'Northern Bahr El Ghazal State',
    'Jonglei State', 'Warrap State', 'Western Equatoria State',
    'Upper Nile State', 'Western Bahr El Ghazal State',
    'Ruweng Administrative Area', 'Unity State', 'Pibor Administrative Area'
]

counties: list
payams: list
facilities: list

state_selected: int
county_selected: int
payam_selected: int
facility_selected: int
service_selected: str


def get_county(body):

  global state_selected
  global service_selected

  fullfilmentText = "Please select your county from the list below\n"
  count = 1
  state_selected = int(body['queryResult']['queryText']) - 1
  service_selected = body['queryResult']['parameters']['facility_services']

  # filter to get all the rows with the specified state
  county_filter = (data["State"] == states[state_selected])

  #get the rows with the mentioned state
  final_list = data.loc[county_filter]

  # get the counties but uniquely
  global counties
  counties = final_list["County"].unique()
  # print(counties)

  for county in counties:
    fullfilmentText += str(count) + ". " + county + "\n"
    count += 1

  print(fullfilmentText)

  result = {
      "followupEventInput": {
          "name": "counties",
          "parameters": {
              "text": fullfilmentText
          },
          "languageCode": "en-US"
      }
  }

  return result


def get_payam(body):

  global counties
  global payams
  global state_selected
  global county_selected

  fullfilmentText = "Please select your payam from the list below\n"
  count = 1
  county_selected = int(body['queryResult']['queryText']) - 1
  # state_selected = body['queryResult']['parameters']["state"]

  print(state_selected)
  print(county_selected)
  print(counties)

  # filter to get all the rows with the specified state
  payam_filter = (data["State"] == states[state_selected]) & (
      data["County"] == counties[county_selected])

  #get the rows with the mentioned state
  final_list = data.loc[payam_filter]

  # get the counties but uniquely
  payams = final_list["Payam"].unique()
  print(payams)

  for payam in payams:
    fullfilmentText += str(count) + ". " + payam + "\n"
    count += 1

  print(fullfilmentText)

  result = {
      "followupEventInput": {
          "name": "payams",
          "parameters": {
              "text": fullfilmentText
          },
          "languageCode": "en-US"
      }
  }

  return result


def get_facility(body):

  global counties
  global payams
  global state_selected
  global county_selected
  global payam_selected
  global facilities

  fullfilmentText = "Please select a health facility from the list below\n"
  count = 1
  payam_selected = int(body['queryResult']['queryText']) - 1
  # county_selected = body['queryResult']['parameters']["county"]
  # state_selected = body['queryResult']['parameters']["state"]

  print(state_selected)
  print(county_selected)
  print(payam_selected)
  print(payams)

  # filter to get all the rows with the specified state
  health_facility = (data["State"] == states[state_selected]) & (
      data["County"]
      == counties[county_selected]) & (data["Payam"] == payams[payam_selected])

  #get the column with the facilities
  final_list = data.loc[health_facility, "Health Facility"]

  # convert the facilities dataframe to a list
  facilities = final_list.values.tolist()
  print(facilities)

  for facility in facilities:
    fullfilmentText += str(count) + ". " + facility + "\n"
    count += 1

  print(fullfilmentText)

  result = {
      "followupEventInput": {
          "name": "facility",
          "parameters": {
              "text": fullfilmentText
          },
          "languageCode": "en-US"
      }
  }

  return result


def generate_voucher(body):

  global facilities
  global service_selected

  # get selected facility
  facility_selected = int(body['queryResult']['queryText']) - 1

  fb_id = body["originalDetectIntentRequest"]["payload"]["data"]["sender"][
      "id"]
  # generate a random alphanumeric string of length 10
  voucher_code = ''.join(
      random.choices(string.ascii_uppercase + string.digits, k=6))

  voucher_payload = {
      "voucher_code": voucher_code,
      "date_generated": str(date.today()),
      "senderID": fb_id,
      "facility_selected": facilities[facility_selected],
      "service_desired": service_selected,
      "facility_visited": "No"
  }

  result = vouchers_collection.insert_one(voucher_payload)

  result = {
      "fulfillmentMessages": [{
          "payload": {
              "facebook": {
                  "quick_replies": [{
                      "content_type": "text",
                      "title": "Main menu🔙",
                      "payload": "main menu"
                  }],
                  "text":
                  "You have chosen facility " + facilities[facility_selected] +
                  ". Please visit them with the following voucher code " +
                  str(voucher_code) +
                  " ... you will get your desired service free of charge😉."
              }
          },
          "platform": "FACEBOOK"
      }]
  }
  return result


def search_voucher(body):

  fb_id = body["originalDetectIntentRequest"]["payload"]["data"]["sender"][
      "id"]

  result = vouchers_collection.find_one({"senderID": fb_id})
  print(result["voucher_code"])
  voucher_code = "yaay"

  return {
      "fulfillmentMessages": [{
          "payload": {
              "facebook": {
                  "quick_replies": [{
                      "content_type": "text",
                      "title": "Main menu🔙",
                      "payload": "main menu"
                  }],
                  "text":
                  "Your voucher code is: " + result["voucher_code"] +
                  ".\nPresent it to the health facility for assistance."
              }
          },
          "platform": "FACEBOOK"
      }]
  }


body = {
    "responseId":
    "b9d4ebb8-da98-48ab-844a-6ef0e0a3d674-d5f6109d",
    "queryResult": {
        "queryText":
        "3",
        "action":
        "locator",
        "parameters": {},
        "allRequiredParamsPresent":
        True,
        "fulfillmentMessages": [{
            "text": {
                "text": [
                    "Good choice./nPlease reply with the number of the state you are currently located in /n1. Abyei Administrative Area/n2. Central Equatoria State/n3. Eastern Equatoria State/n4. Lakes State/n5 /n6. /n7. /n8. /n9. /n10. /n11. /n12. /n13. ."
                ]
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
                "timestamp": "1705270045548",
                "message": {
                    "mid":
                    "m_q9NRzTD51nPa4M72lSQLlB5NQaxcUefXNorRs6YpoFUFNEga3xahduNkgOhBZp83YJoLTwbnyLl0NxKWF-JoJQ",
                    "text": "1"
                },
                "sender": {
                    "id": "25312035848395889"
                },
                "recipient": {
                    "id": "210972265431842"
                }
            }
        }
    },
    "session":
    "projects/bio-medc-bot-dev-ixvr/agent/sessions/87694359-ed0a-3d8f-94ca-1f3ef24153d3"
}

body2 = {
    "responseId":
    "b9d4ebb8-da98-48ab-844a-6ef0e0a3d674-d5f6109d",
    "queryResult": {
        "queryText":
        "3",
        "action":
        "locator",
        "parameters": {
            "state": 3,
        },
        "allRequiredParamsPresent":
        True,
        "fulfillmentMessages": [{
            "text": {
                "text": [
                    "Good choice./nPlease reply with the number of the state you are currently located in /n1. Abyei Administrative Area/n2. Central Equatoria State/n3. Eastern Equatoria State/n4. Lakes State/n5 /n6. /n7. /n8. /n9. /n10. /n11. /n12. /n13. ."
                ]
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
                "timestamp": "1705270045548",
                "message": {
                    "mid":
                    "m_q9NRzTD51nPa4M72lSQLlB5NQaxcUefXNorRs6YpoFUFNEga3xahduNkgOhBZp83YJoLTwbnyLl0NxKWF-JoJQ",
                    "text": "1"
                },
                "sender": {
                    "id": "25312035848395889"
                },
                "recipient": {
                    "id": "210972265431842"
                }
            }
        }
    },
    "session":
    "projects/bio-medc-bot-dev-ixvr/agent/sessions/87694359-ed0a-3d8f-94ca-1f3ef24153d3"
}

body3 = {
    "responseId":
    "b9d4ebb8-da98-48ab-844a-6ef0e0a3d674-d5f6109d",
    "queryResult": {
        "queryText":
        "3",
        "action":
        "locator",
        "parameters": {},
        "allRequiredParamsPresent":
        True,
        "fulfillmentMessages": [{
            "text": {
                "text": [
                    "Good choice./nPlease reply with the number of the state you are currently located in /n1. Abyei Administrative Area/n2. Central Equatoria State/n3. Eastern Equatoria State/n4. Lakes State/n5 /n6. /n7. /n8. /n9. /n10. /n11. /n12. /n13. ."
                ]
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
                "timestamp": "1705270045548",
                "message": {
                    "mid":
                    "m_q9NRzTD51nPa4M72lSQLlB5NQaxcUefXNorRs6YpoFUFNEga3xahduNkgOhBZp83YJoLTwbnyLl0NxKWF-JoJQ",
                    "text": "1"
                },
                "sender": {
                    "id": "25312035848395889"
                },
                "recipient": {
                    "id": "210972265431842"
                }
            }
        }
    },
    "session":
    "projects/bio-medc-bot-dev-ixvr/agent/sessions/87694359-ed0a-3d8f-94ca-1f3ef24153d3"
}

# print(get_county(body))
# print(get_payam(body2))
# print(get_facility(body3))
