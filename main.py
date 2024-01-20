from fastapi import FastAPI, Request
import uvicorn
import data_models
import user_functions
import locator

app = FastAPI()


@app.get("/")
def root():

  return {"message": "hi from Bio Medic"}


# this endpoint will manage user registration data
@app.post("/biomedic_bot")
async def user_verification(request: Request):

  body = await request.json()
  action = body["queryResult"]["action"]
  # print(body)
  result = {}
  if action == "verify":
    # check if user exists and set event name
    result = user_functions.verify_user(body)

  elif action == "register":
    # register user
    result = user_functions.register_user(body)

  elif action == "county":
    # get user county
    result = locator.get_county(body)

  elif action == "payam":
    # get user payam
    result = locator.get_payam(body)

  elif action == "facilities":
    # get facilities
    result = locator.get_facility(body)

  elif action == "generate_voucher":
    # get facilities
    result = locator.generate_voucher(body)

  elif action == "search_voucher":
    # get facilities
    result = locator.search_voucher(body)

  # elif action == "user_interaction":
  #   # record user interation
  #   result = user_functions.user_interaction(body)

  return result


# this endpoint will manage user registration data
@app.post("/reg")
def register_user(user: data_models.User):
  results = {"user": user}
  return results


fb_result = {
    "fulfillmentMessages": [{
        "payload": {
            "facebook": {
                "quick_replies": [{
                    "title": "Find a facility📍",
                    "payload": "locator",
                    "content_type": "text"
                }, {
                    "content_type": "text",
                    "title": "HIV information📖",
                    "payload": "hiv"
                }],
                "text":
                "Select an option from below👇 so that I can assist you"
            }
        },
        "platform": "FACEBOOK"
    }]
}

# if __name__ == "__main__":
#   uvicorn.run(app, host="0.0.0.0", port=8080)
