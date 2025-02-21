from datetime import date, datetime

import pandas as pd
import simplejson
from flask.json.provider import JSONProvider


class CustomJSONProvider(JSONProvider):

    def __init__(self, app):
        super().__init__(app)

    def dumps(self, obj, **kwargs):
        kwargs["ensure_ascii"] = False
        kwargs["ignore_nan"] = True
        kwargs['default'] = self.default
        return simplejson.dumps(obj, **kwargs)

    def loads(self, s, **kwargs):
        return simplejson.loads(s, **kwargs)

    @staticmethod
    def default(obj):
        if pd.isnull(obj):
            return None
        if isinstance(obj, datetime):
            return int(obj.timestamp() * 1000)
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
