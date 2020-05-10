# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9), "JST")

def now():
    return datetime.now(tz=JST)
