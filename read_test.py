from pathlib import Path
from geometry import Point, Triangle
import json

dir_path = Path("logs/")

# for file_path in dir_path.glob("*.json"):
for file_path in [Path("logs/test_write_log.json")]:
    with file_path.open("r", encoding="utf-8") as f:
        data = []
        raw = json.load(f)
        for inputs, outputs in raw:
            inputs_raw = json.loads(inputs)
            # inputs = json.loads(inputs, object_hook=Point.from_json) # WHY CANT I? ISNT DEC LIKE THIS?
            outputs_raw = json.loads(outputs)

            inputs = [Point.from_json(obj) for obj in inputs_raw]
            outputs = [Triangle.from_json(obj) for obj in outputs_raw]

            data.append((inputs, outputs))

            # data.append(
            # [
            # json.loads(inputs, object_hook=Point.from_json),
            # json.loads(
            # outputs,
            # object_hook=Triangle.from_json,
            # ),
            # ]
            # )

    print(f"--- {file_path.name} ---")
    print(data)
