from datetime import date, datetime

from simplejson import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs["ensure_ascii"] = False
        kwargs["ignore_nan"] = True
        super().__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, datetime):
            return int(obj.timestamp() * 1000)
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)