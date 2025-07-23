import requests

# You can find the ID of an empire from the URL of its page on Bitjita.
# For example, here is Legion's URL: https://bitjita.com/empires/217
def get_empire_member_count(empire_id):
    url = f"https://bitjita.com/empires/{empire_id}/__data.json"
    response = requests.get(url)
    data = response.json()

    print(f"Fetching member count for empire ID: {empire_id} name: {data["nodes"][1]["data"][data["nodes"][1]["data"][1]["name"]]}")
    members:list = data["nodes"][1]["data"][data["nodes"][1]["data"][0]["members"]]

    return len(members)

print(get_empire_member_count(2669))
print(get_empire_member_count(217))