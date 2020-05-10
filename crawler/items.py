import scrapy


class Race(scrapy.Item):
    # 番組表
    date = scrapy.Field()
    stadium = scrapy.Field()
    round = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    # length = scrapy.Field()
    deadline = scrapy.Field()
    racers = scrapy.Field()  # List[Racer]

    # 直前情報
    air_temperature = scrapy.Field()
    water_temperature = scrapy.Field()
    weather = scrapy.Field()
    wind_direction = scrapy.Field()
    wind_speed = scrapy.Field()
    wave_height = scrapy.Field()

    # オッズ
    # odds = scrapy.Field()  # Odds
    trifecta = scrapy.Field()

    # コンピューター予想
    predict_patterns = scrapy.Field()
    predict_confidence = scrapy.Field()

    # 結果
    result_reason = scrapy.Field()


class Racer(scrapy.Item):
    course = scrapy.Field()
    racer_id = scrapy.Field()
    grade = scrapy.Field()
    name = scrapy.Field()
    branch = scrapy.Field()
    birthplace = scrapy.Field()
    age = scrapy.Field()
    weight = scrapy.Field()
    flying = scrapy.Field()
    late = scrapy.Field()
    average_start_timing = scrapy.Field()
    global_win = scrapy.Field()
    global_quinella = scrapy.Field()
    global_trio = scrapy.Field()
    local_win = scrapy.Field()
    local_quinella = scrapy.Field()
    local_trio = scrapy.Field()
    motor_id = scrapy.Field()
    motor_quinella = scrapy.Field()
    motor_trio = scrapy.Field()
    boat_id = scrapy.Field()
    boat_quinella = scrapy.Field()
    boat_trio = scrapy.Field()

    display_time = scrapy.Field()
    display_start = scrapy.Field()
    display_entry = scrapy.Field()

    predict_mark = scrapy.Field()

    result = scrapy.Field()
    race_time = scrapy.Field()
    entry = scrapy.Field()
    start_time = scrapy.Field()


# class Odds(scrapy.Item):
#     win = scrapy.Field()  # 単勝
#     place_show = scrapy.Field()  # 複勝
#     exacta = scrapy.Field()  # 2連単
#     quinella = scrapy.Field()  # 2連複
#     trifecta = scrapy.Field()  # 3連単
#     trio = scrapy.Field()  # 3連複
#     quinella_place = scrapy.Field()  # 拡連複
