import os
import pickle

import requests
from bs4 import BeautifulSoup

from surf_bot.constants import SURFLINE_SEARCH_URL


def search_surfline(spot_name: str) -> str:
    results_url = os.path.join(SURFLINE_SEARCH_URL, "%20".join(spot_name.split()))
    return results_url


def parse_search_results(spot_name: str) -> dict:
    result_url = search_surfline(spot_name)
    result_html = requests.get(result_url)
    result_soup = BeautifulSoup(result_html.content, "html.parser")
    surf_spots = result_soup.find_all("section", {"id": "surf-spots"})
    surf_spots = surf_spots[0].find_all("div", {"class": "result"})

    result_dict = {}
    for spot_idx, surf_spot in enumerate(surf_spots):
        result_name = surf_spot.find_all("span", {"class": "result__name"})
        spot_location = surf_spot.find_all("span", {"class": "result__breadcrumb"})

        spot_name = f"{result_name[0].text}, {spot_location[0].text}"
        spot_url = surf_spot.find_all("a", href=True)[0]["href"]
        result_dict[spot_idx + 1] = {"spot_name": spot_name, "spot_url": spot_url}

    return result_dict


def get_spot_condition(spot_url: str) -> str:
    html_doc = requests.get(spot_url)
    result_soup = BeautifulSoup(html_doc.content, "html.parser")
    condition_bar = result_soup.find_all(
        "div", {"class": "quiver-colored-condition-bar"}
    )
    return condition_bar[0].text


def get_spot_last_updated(spot_url: str) -> str:
    html_doc = requests.get(spot_url)
    result_soup = BeautifulSoup(html_doc.content, "html.parser")
    last_updates = result_soup.find_all(
        "span", {"class": "quiver-forecaster-profile__update-container__last-update"}
    )
    last_updated = last_updates[0].text
    return last_updated


def pickle_dump(obj, filename: str):
    with open(filename, "wb") as outfile:
        pickle.dump(obj, outfile, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(filename: str):
    with open(filename, "rb") as infile:
        obj = pickle.load(infile)
    return obj
