"""This should be run in a cron job to check for spot condition updates"""

from surf_bot.constants import (
    CONDITIONS,
    FPATH_CONDITION_DATA_DICT,
    TWILIO_CLIENT,
    TWILIO_PHONE_NUMBER,
)
from surf_bot.utils import (
    get_spot_condition,
    get_spot_last_updated,
    parse_search_results,
    pickle_dump,
    pickle_load,
)


def main():
    """Main"""

    condition_data_dict = pickle_load(FPATH_CONDITION_DATA_DICT)
    for spot_name, location_dict in condition_data_dict.items():
        # spot_name should only return 1 result since that's how the data_dict
        # is initialized
        result_dict = parse_search_results(spot_name)
        spot_url = result_dict[1]["spot_url"]
        last_updated = get_spot_last_updated(spot_url)
        new_condition = get_spot_condition(spot_url)

        # New update!
        if last_updated != location_dict["last_updated"]:
            new_condition_index = CONDITIONS.index(new_condition)
            user_data = location_dict["user_data"]
            for user_data_dict in user_data:
                threshold_index = CONDITIONS.index(
                    user_data_dict["condition_threshold"]
                )
                if new_condition_index >= threshold_index:
                    phone_number = user_data_dict["phone_number"]
                    TWILIO_CLIENT.messages.create(
                        to=phone_number,
                        from_=TWILIO_PHONE_NUMBER,
                        body=f"SURF ALERT: {spot_name} is now {new_condition}!",
                    )
        condition_data_dict[spot_name]["condition"] = new_condition
        condition_data_dict[spot_name]["last_updated"] = last_updated

    pickle_dump(condition_data_dict, FPATH_CONDITION_DATA_DICT)


if __name__ == "__main__":
    main()
