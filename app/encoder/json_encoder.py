from datetime import date, datetime

from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if obj == "None" or obj == "NaN":
            return None
        elif isinstance(obj, datetime):
            return int(obj.timestamp() * 1000)
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return JSONEncoder.default(self, obj)