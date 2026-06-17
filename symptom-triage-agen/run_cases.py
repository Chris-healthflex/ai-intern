from dataset import get_cases
from graph import app
import json


cases = get_cases()


print("Total cases:", len(cases))


results = []


for index, case in enumerate(cases, start=1):

    print(f"Processing case {index}/{len(cases)}")


    patient_id = case["patient_id"]

    message = case["message"]


    output = app.invoke(
        {
            "symptoms": message,
            "red_flags": [],
            "sources": [],
            "need_search": False,
            "emergency": False
        }
    )


    results.append(
        {
            "patient_id": patient_id,
            "message": message,
            "triage": output
        }
    )


with open(
    "triage_results.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\nCompleted")
print("Generated triage_results.json")