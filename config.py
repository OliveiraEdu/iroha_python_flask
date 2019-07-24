import re

# !!!! ONLY LOWER CASE !!!! bug in iroha.
sawmill_names = ["colombia", "venezuela", "brazil", "ecuador"]

woods = ["oro", "petroleo", "gas", "dolares"]


def to_lower_case_only_letters(string):
    string = string.lower()
    string = re.sub(r'[^a-z0-9]', '', string)
    return string
