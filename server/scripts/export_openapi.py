import json
from app.main import app

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
# If yaml needed:
# import yaml
# with open("openapi.yaml","w") as f:
#     yaml.safe_dump(app.openapi(), f, sort_keys=False)
