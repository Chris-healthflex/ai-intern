import requests


DATASET_URL = "https://ai-stance.vercel.app/api/cases"


def get_cases():

    response = requests.get(
        DATASET_URL,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    return data["cases"]