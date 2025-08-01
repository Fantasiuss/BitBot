import requests,math
from ratelimit import limits, sleep_and_retry
from loguru import logger

profession_ids = {
    "Carpentry": 3,
    "Construction": 15,
    "Cooking": 13,
    "Farming": 11,
    "Fishing": 12,
    "Foraging": 14,
    "Forestry": 2,
    "Hunting": 9,
    "Leatherworking": 8,
    "Masonry": 4,
    "Merchanting": 15,
    "Mining": 5,
    "Sailing": 21,
    "Scholar": 7,
    "Slayer": 18,
    "Smithing": 6,
    "Tailoring": 10,
    "Taming": 17
}

@sleep_and_retry
@limits(calls=5, period=1)
def call_api(url):
    return requests.get(url)

def level_from_total_xp(total_xp):
    """
    Calculate the level based on total XP.
    """
    if type(total_xp) is not int:
        logger.debug(f"Invalid total XP type: {type(total_xp)}. Expected int.")
        return 1
    if total_xp < 0:
        logger.debug(f"Negative total XP: {total_xp}. Returning level 0.")
        return 1
    return math.floor(1+(62/(9*math.log(2)))*math.log(total_xp/6020+1))

class PlayerInformation:
    def __init__(self, username):
        self.rawdata = get_player_info(username)
        if not self.rawdata:
            raise ValueError("Invalid username or player not found.")
        self.data = self.rawdata["nodes"][1]["data"]
        
        self.reference = self.data[1]
        
        self.username = self.data[self.reference["username"]]
        self.skillmap = self.data[self.reference["skillMap"]]
        self.claims = ", ".join([self.data[self.data[x]["name"]] for x in self.data[self.reference["claims"]]])
        self.empires = ", ".join([self.data[self.data[x]["empireName"]] for x in self.data[self.reference["empireMemberships"]]])
        
        self.skillexp = {
            # Here's how the skillmap works. self.skillmap is a dictionary of 'skill #1 is item #'
            # Go to item # and you'll find a dictionary with the ID, name, title and category.
            # Go to ID - 1 and you'll find the total XP.
        }
        
        for skill_id, skill_info in self.skillmap.items():
            logger.debug(f"Skill {self.data[self.data[skill_info]["name"]]}: {self.data[self.data[int(skill_info)]["id"] - 1]}, ({skill_id,skill_info})")
            if(self.data[self.data[skill_info]["name"]] == "ANY"): continue
            self.skillexp[self.data[self.data[skill_info]["name"]]] = self.data[self.data[int(skill_info)]["id"] - 1]
            
        self.skills = {skill: level_from_total_xp(xp) for skill, xp in self.skillexp.items()}

def get_player_info(username):
    logger.debug("Fetching player info for:", username)
    # Step 1: Get the player ID from search results
    search_url = f"https://bitjita.com/api/players?q={username}"
    search_response = call_api(search_url)
    search_data = search_response.json()

    player_id = search_data["players"][0]["entityId"] if search_data["players"] else None
    if not player_id:
        logger.debug(f"Player {username} not found.")
        return None

    # Step 2: Get the full player info using the ID
    info_url = f"https://bitjita.com/api/players/{player_id}"
    info_response = call_api(info_url)
    info_data = info_response.json()

    return info_data

def get_leaderboard(profession:str,filter=None):
    profession_id = profession_ids[profession.capitalize()]
    url = f"https://bitjita.com/api/skills/leaderboard?sortBy={profession_id}&sortOrder=desc&page=1"
    
    response = call_api(url)
    data = response.json()
    
    return data["players"][:10]

def get_empire_data(empire_name):
    search_url = f"https://bitjita.com/api/empires/?q={empire_name.replace(' ', '+')}"
    search_response = call_api(search_url)
    search_data = search_response.json()
    
    try:
        if not search_data["empires"] or len(search_data["empires"]) < 1:
            logger.debug(f"Empire {empire_name} not found in search results.")
            return None
    except KeyError:
        logger.debug(f"Unexpected response format for empire search: {search_data}")
        return None
    
    empire_id = search_data["empires"][0]["entityId"]
    
    url = f"https://bitjita.com/empires/{empire_id}/__data.json"
    response = call_api(url)
    data = response.json()
    empire_data = data["nodes"][1]["data"]
    empire_ref = data["nodes"][1]["data"][1]
    
    return {
        "name": empire_data[empire_ref["name"]],
        "members": len(empire_data[empire_data[0]["members"]]),
        "owner": empire_data[empire_data[empire_data[empire_data[0]["members"]][0]]["playerName"]],
    }