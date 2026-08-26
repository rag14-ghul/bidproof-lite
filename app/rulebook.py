import yaml
from pathlib import Path
from typing import Union, Dict, Any
from app.models import Rulebook

def parse_rulebook_dict(data: Dict[str, Any]) -> Rulebook:
    bid_date = data.get("meta", {}).get("bid_date", "")
    if "rules" in data and isinstance(data["rules"], list):
        for rule in data["rules"]:
            if "check" in rule and isinstance(rule["check"], dict):
                check_val = rule["check"].get("value")
                if isinstance(check_val, str) and "{bid_date}" in check_val:
                    rule["check"]["value"] = check_val.replace("{bid_date}", str(bid_date))
    return Rulebook.model_validate(data)

def load_rulebook(source: Union[str, Path, Dict[str, Any]]) -> Rulebook:
    if isinstance(source, dict):
        return parse_rulebook_dict(source)
    
    if isinstance(source, (str, Path)):
        s_str = str(source)
        if "\n" in s_str or len(s_str) > 255:
            data = yaml.safe_load(s_str)
        else:
            try:
                path = Path(s_str)
                if path.is_file():
                    with open(path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                else:
                    data = yaml.safe_load(s_str)
            except Exception:
                data = yaml.safe_load(s_str)
    else:
        raise ValueError(f"Invalid rulebook source type: {type(source)}")
        
    return parse_rulebook_dict(data)
