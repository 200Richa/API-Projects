import requests
from datetime import datetime
from secrets import MY_URL, TOKEN, USERNAME, GRAPH_ID, pixela_endpoint

TODAY_DATE = datetime.now().strftime("%Y%m%d")
yesterday = datetime(2021, 5, 14).strftime("%Y%m%d")

graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"
pixel_addition_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH_ID}"
pixel_update_endpoint = f"{pixel_addition_endpoint}/{yesterday}"


users_params = {
    "token": TOKEN,
    "username": USERNAME,
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}

graph_config = {
    "id": GRAPH_ID,
    "name": "coding",
    "unit": "min",
    "type": "int",
    "color": "ajisai",
}

headers = {
    "X-USER-TOKEN": TOKEN,
}

pixel_params = {
    "date": yesterday,
    "quantity": input("How many minutes did you code today?: "),
}

update_params = {
    "quantity": input(f"Enter how much time u code on {yesterday}"),
}

# TO CREATE A NEW USERNAME
# response = requests.post(url=pixela_endpoint, json=users_params)


# TO CREATE A NEW GRAPH
# response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)


# TO ADD A NEW PIXEL EACH DAY
response = requests.post(url=pixel_addition_endpoint, json=pixel_params, headers=headers)


# TO UPDATE A PIXEL
# response = requests.put(url=pixel_update_endpoint, json=update_params, headers=headers)


# TO DELETE A PIXEL
# response = requests.delete(url=pixel_update_endpoint, headers=headers)