from typing import Any, Dict
import google.cloud.functions.context as func

def update_dataset(event: Dict[str, Any], context: func.Context):
    print(event)
    print(event.get("attributes"))
