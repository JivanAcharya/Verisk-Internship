import requests
import json
url = "https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_2025_0__ba2fbd3409733a83fb62c3ee4219487c.json"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "application/json",
    "Referer": "https://www.timeshighereducation.com/world-university-rankings/2025/world-ranking",

}

response = requests.get(url,headers=headers)
if response.status_code == 200:
    data  = response.json()
    # print(data)
    with open("./testing/times_uni_ranking.json","w") as f:
        json.dump(data,f, indent=4)
    print("Data saved successfully")
else:
    print("\n ERROR:", response.status_code)
    response.raise_for_status()