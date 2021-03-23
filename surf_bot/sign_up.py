import os

from flask import request
from twilio.twiml.messaging_response import MessagingResponse

from surf_bot.constants import CONDITIONS, FPATH_CONDITION_DATA_DICT
from surf_bot.utils import (
    get_spot_condition,
    get_spot_last_updated,
    parse_search_results,
    pickle_dump,
    pickle_load,
)


class SurfSpotConditions:
    """Sign up user for their desired surf spot and condition threshold"""

    def __init__(self):
        """Init

        Mostly initialization of flag for which step of the sign up process has
        been executed
        """
        self.multiple_spots = False
        self.initial_spot_selection = True
        self.initial_condition_selection = True
        self.first_text = True
        self.spot_info_created = False

        self.results_dict = None
        self.phone_number = None
        self.current_condition = None
        if os.path.isfile(FPATH_CONDITION_DATA_DICT):
            self.condition_data_dict = pickle_load(FPATH_CONDITION_DATA_DICT)
            if self.condition_data_dict is None:
                self.condition_data_dict = {}
        else:
            self.condition_data_dict = {}
        self.spot_url = None
        self.spot_name = None

    def _reply_to_first_text(self) -> str:
        """Prompt user to enter spot location"""

        self.phone_number = request.form["From"]
        self.first_text = False

        prompt_str = (
            "Hello! You have signed up for Berk's Surfline updates. "
            "Please enter the name of the surf location that you would "
            "like status updates from"
        )
        resp = MessagingResponse()
        resp.message(prompt_str)
        return str(resp)

    def _select_surf_spot(self, message_body: str) -> str:
        """Locate the user entered surf spot. Prompt them to clarify if
        multiple results
        """

        try:
            self.results_dict = parse_search_results(message_body)
        except IndexError:
            response_str = (
                f"I'm sorry, but Surfline did not return any results for "
                f"{message_body}. Please try another spot"
            )
            resp = MessagingResponse()
            resp.message(response_str)
            return str(resp)
        self.initial_spot_selection = False
        if len(self.results_dict) > 1:
            self.multiple_spots = True
            prompt_str = (
                "\nThere was more than one result matching you search, "
                "which did you mean (enter number)?\n"
            )
            for spot_num, spot_dict in self.results_dict.items():
                spot_name = spot_dict["spot_name"]
                prompt_str += f"{spot_num}: {spot_name}\n"
            resp = MessagingResponse()
            resp.message(prompt_str)
            return str(resp)
        else:
            return "single spot"

    def _set_spot_info(self, message_body: str) -> str:
        """Initial spot url, human readable name, and current condition"""

        if self.multiple_spots:
            spot_num = int(message_body)
            self.multiple_spots = False
        else:
            spot_num = 1

        self.spot_url = self.results_dict[spot_num]["spot_url"]
        self.spot_name = self.results_dict[spot_num]["spot_name"]
        try:
            self.current_condition = get_spot_condition(self.spot_url)
        except IndexError:
            response_str = (
                "There are no status reports for this spot, please try a "
                "different location"
            )
            self.initial_spot_selection = True
            resp = MessagingResponse()
            resp.message(response_str)
            return str(resp)

        self.spot_info_created = True
        return "spot found"

    def _select_spot_condition(self) -> str:
        """Prompt user to select spot condition threshold"""

        prompt_str = (
            "Please enter the number for the minimum condition you would "
            "like updates for:\n"
        )
        for condition_idx, condition_str in enumerate(CONDITIONS):
            # Adding 1 since most user probably aren't used to 0 indexing
            prompt_str += f"{condition_idx + 1}: {condition_str}\n"
        resp = MessagingResponse()
        resp.message(prompt_str)
        self.initial_condition_selection = False
        return str(resp)

    def _reset_signup_params(self):
        """After user has completed sign up process, reset workflow flags"""

        self.initial_spot_selection = True
        self.first_text = True
        self.initial_condition_selection = True
        self.multiple_spots = False
        self.spot_info_created = False

    def sms_build(self) -> str:

        message_body = request.form["Body"]

        if self.first_text:
            return self._reply_to_first_text()

        if self.initial_spot_selection:
            spot_selection = self._select_surf_spot(message_body)
            if spot_selection != "single spot":
                return spot_selection

        if not self.spot_info_created:
            spot_info = self._set_spot_info(message_body)
            if spot_info != "spot found":
                return spot_info

        if self.initial_condition_selection:
            return self._select_spot_condition()

        condition_num = int(message_body)
        condition_threshold = CONDITIONS[condition_num - 1]

        spot_dict = self.condition_data_dict.get(self.spot_name)
        if spot_dict is None:
            self.condition_data_dict[self.spot_name] = {
                "condition": self.current_condition,
                "last_updated": get_spot_last_updated(self.spot_url),
                "user_data": [],
            }

        user_list = self.condition_data_dict[self.spot_name]["user_data"]

        user_list.append(
            {
                "phone_number": self.phone_number,
                "condition_threshold": condition_threshold,
            }
        )

        pickle_dump(self.condition_data_dict, FPATH_CONDITION_DATA_DICT)

        prompt_str = (
            f"Great! You have successfully signed up for notifications about "
            f"{self.spot_name} when conditions are greater than or equal to "
            f"{condition_threshold}"
        )
        resp = MessagingResponse()
        resp.message(prompt_str)

        self._reset_signup_params()
        return str(resp)
