import re
from datetime import timedelta
from itertools import permutations
from urllib.parse import parse_qs, urlsplit

import scrapy
from more_itertools import chunked, flatten
from scrapy.http import Response

from . import now
from ..items import Racer, Race


def parse_query_params(url):
    params = parse_qs(urlsplit(url).query)
    return {k: v[0] for k, v in params.items() if v}


def transpose(it, chunk):
    return list(flatten(zip(*chunked(it, chunk))))


class HistorySpider(scrapy.Spider):
    name = "history"
    domain = "www.boatrace.jp"
    allowed_domains = [domain]
    date = now() - timedelta(days=1)
    start_urls = [
        f"https://www.boatrace.jp/owpc/pc/race/index?hd={date.strftime('%Y%m%d')}"
    ]

    def get_url(self, url):
        return "https://" + self.domain + url

    def parse(self, response: Response):
        params = parse_query_params(response.url)
        stadium_urls = response.css("td.is-alignL a::attr('href')").re(r".*raceindex.*")
        self.logger.info(f"{params['hd']}: {len(stadium_urls)} stadiums")
        for stadium_url in stadium_urls:
            yield scrapy.Request(
                url=self.get_url(stadium_url), callback=self.parse_stadium
            )

        # さらに前日へ
        url = response.css("li.title2_navsLeft a::attr('href')").get()
        yield scrapy.Request(url=self.get_url(url), callback=self.parse)

    def parse_stadium(self, response: Response):
        race_urls = response.css("ul.textLinks3 a::attr('href')").re(".*racelist.*")
        # params = parse_query_params(response.url)
        # self.logger.info(f"{params['hd']}, {params['jcd']}: {len(race_urls)} races")

        for race_url in race_urls:
            url = self.get_url(race_url)
            yield scrapy.Request(url=url, callback=self.parse_program)

    def parse_program(self, response: Response):
        item = Race()

        # メタ情報
        params = parse_query_params(response.url)
        item["date"] = params["hd"]
        item["round"] = params["rno"]
        item["stadium"] = params["jcd"]
        self.logger.info(f"{params['hd']}, {params['jcd']}, {params['rno']}")

        item["title"] = response.css("h2.heading2_titleName::text").get()
        detail = (
            response.css("span.heading2_titleDetail::text")
            .get()
            .replace("\u3000", "")
            .split()
        )
        item["subtitle"] = detail[0]
        item["deadline"] = response.css(
            f"div.table1.h-mt10 tbody td:nth-child({int(params['rno']) + 1})::text"
        ).get()

        # レーサー一覧
        metas = response.css("tbody.is-fs12 td div.is-fs11").xpath("string()").getall()
        names = response.css("tbody.is-fs12 td div.is-fs18").xpath("string()").getall()
        scores = response.css("tbody.is-fs12 td.is-lineH2").xpath("string()").getall()
        racers = []
        for i, (meta, name, score) in enumerate(
            zip(chunked(metas, 2), names, chunked(scores, 5))
        ):
            racer = Racer()
            racer["course"] = i + 1
            racer["name"] = "".join(name.split())
            racer["racer_id"], _, racer["grade"] = meta[0].split()
            racer["branch"], racer["birthplace"], racer["age"], racer["weight"] = (
                meta[1].replace("/", " ").split()
            )
            racer["flying"], racer["late"], racer["average_start_timing"] = score[
                0
            ].split()
            racer["global_win"], racer["global_quinella"], racer["global_trio"] = score[
                1
            ].split()
            racer["local_win"], racer["local_quinella"], racer["local_trio"] = score[
                2
            ].split()
            racer["motor_id"], racer["motor_quinella"], racer["motor_trio"] = score[
                3
            ].split()
            racer["boat_id"], racer["boat_quinella"], racer["boat_trio"] = score[
                4
            ].split()
            racers.append(racer)
        item["racers"] = racers
        # item["odds"] = Odds()
        url = self.get_url(
            response.css("ul.tab3_tabs li:nth-child(2) a::attr('href')").get()
        )
        yield scrapy.Request(
            url=url, callback=self.parse_odds3t, meta={"item": item},
        )

    def parse_odds3t(self, response: Response):
        def convert(odds):
            try:
                return float(odds)
            except:
                return 0

        """3連単"""
        item = response.meta["item"]

        odds = response.css("td.oddsPoint::text").getall()
        patterns = transpose(permutations(range(1, 7), 3), 20)
        item["trifecta"] = {
            "-".join(map(str, p)): convert(o)
            for p, o in sorted(zip(patterns, odds), key=lambda x: x[0])
        }

        # 直前情報の取得へ
        url = self.get_url(
            response.css("ul.tab3_tabs li:nth-child(3) a::attr('href')").get()
        )
        yield scrapy.Request(
            url=url, callback=self.parse_beforeinfo, meta={"item": item},
        )

        # # 3連複の取得へ
        # url = self.get_url(
        #     response.css("ul.tab4_tabs li:nth-child(2) a::attr('href')").get()
        # )
        # yield scrapy.Request(
        #     url=url, callback=self.parse_odds3f, meta={"item": item},
        # )

    # def parse_odds3f(self, response: Response):
    #     """3連複"""
    #     item = response.meta["item"]
    #
    #     odds = response.css("td.oddsPoint::text").getall()
    #     patterns = [
    #         (1, 2, 3),
    #         (1, 2, 4),
    #         (1, 2, 5),
    #         (1, 2, 6),
    #         (1, 3, 4),
    #         (2, 3, 4),
    #         (1, 3, 5),
    #         (2, 3, 5),
    #         (1, 3, 6),
    #         (2, 3, 6),
    #         (1, 4, 5),
    #         (2, 4, 5),
    #         (3, 4, 5),
    #         (1, 4, 6),
    #         (2, 4, 6),
    #         (3, 4, 6),
    #         (1, 5, 6),
    #         (2, 5, 6),
    #         (3, 5, 6),
    #         (4, 5, 6),
    #     ]
    #     item["odds"]["trio"] = {
    #         "=".join(map(str, p)): float(o)
    #         for p, o in sorted(zip(patterns, odds), key=lambda x: x[0])
    #     }
    #
    #     # 2連単・2連複の取得へ
    #     url = self.get_url(
    #         response.css("ul.tab4_tabs li:nth-child(3) a::attr('href')").get()
    #     )
    #     yield scrapy.Request(
    #         url=url, callback=self.parse_odds2tf, meta={"item": item},
    #     )
    #
    # def parse_odds2tf(self, response: Response):
    #     """2連単・2連複"""
    #     item = response.meta["item"]
    #
    #     odds = response.css("td.oddsPoint::text").getall()
    #     exacta = odds[:30]
    #     patterns = transpose(permutations(range(1, 7), 2), 5)
    #     item["odds"]["exacta"] = {
    #         "-".join(map(str, p)): float(o)
    #         for p, o in sorted(zip(patterns, exacta), key=lambda x: x[0])
    #     }
    #
    #     quinella = odds[30:]
    #     patterns = [
    #         (1, 2),
    #         (1, 3),
    #         (2, 3),
    #         (1, 4),
    #         (2, 4),
    #         (3, 4),
    #         (1, 5),
    #         (2, 5),
    #         (3, 5),
    #         (4, 5),
    #         (1, 6),
    #         (2, 6),
    #         (3, 6),
    #         (4, 6),
    #         (5, 6),
    #     ]
    #     item["odds"]["quinella"] = {
    #         "=".join(map(str, p)): float(o)
    #         for p, o in sorted(zip(patterns, quinella), key=lambda x: x[0])
    #     }
    #
    #     # 直前情報の取得へ
    #     url = self.get_url(
    #         response.css("ul.tab3_tabs li:nth-child(3) a::attr('href')").get()
    #     )
    #     yield scrapy.Request(
    #         url=url, callback=self.parse_beforeinfo, meta={"item": item},
    #     )

    def parse_beforeinfo(self, response: Response):
        """直前情報"""
        item = response.meta["item"]
        display_times = response.css(
            ".table1 table.is-w748 tbody td:nth-child(5)::text"
        ).getall()
        for i, d in enumerate(display_times):
            item["racers"][i]["display_time"] = d

        display_starts = response.css(".table1_boatImage1").xpath("string()").getall()
        for i, row in enumerate(display_starts):
            num, timing = row.split()
            num = int(num)
            item["racers"][num - 1]["display_entry"] = i + 1
            item["racers"][num - 1]["display_time"] = timing

        item["weather"] = (
            response.css(".weather1_bodyUnitLabelTitle").xpath("string()").getall()[1]
        )

        air, wind, water, wave = (
            response.css(".weather1_bodyUnitLabelData").xpath("string()").getall()
        )
        item["air_temperature"] = air
        item["wind_speed"] = wind
        item["water_temperature"] = water
        item["wave_height"] = wave

        wind_direction = response.css(
            ".weather1_bodyUnit.is-windDirection p::attr('class')"
        ).re("is-wind(\d+)")
        if wind_direction:
            item["wind_direction"] = wind_direction[0]
        else:
            item["wind_direction"] = None

        # コンピューター予想の取得へ
        url = self.get_url(
            response.css("ul.tab3_tabs li:nth-child(4) a::attr('href')").get()
        )
        yield scrapy.Request(
            url=url, callback=self.parse_pcexpect, meta={"item": item},
        )

    def parse_pcexpect(self, response: Response):
        """コンピュータ予想"""
        item = response.meta["item"]
        focuses = response.css(".numberSet2_row").xpath("string()").getall()
        focuses = list(map(lambda x: "".join(x.split()), focuses))
        item["predict_patterns"] = focuses

        item["predict_confidence"] = response.css(
            ".state2 .state2_lv::attr('class')"
        ).re("is-lv(\d)")[0]

        marks = response.css(".table1 .is-fs12 tr:first-child td:first-child").getall()
        for i, mark in enumerate(marks):
            match = re.search(r"icon_mark1_(\d+)\.png", mark)
            if match:
                item["racers"][i]["predict_mark"] = match[1]
            else:
                item["racers"][i]["predict_mark"] = None

        # 結果の取得へ
        url = self.get_url(
            response.css("ul.tab3_tabs li:nth-child(6) a::attr('href')").get()
        )
        yield scrapy.Request(
            url=url, callback=self.parse_result, meta={"item": item},
        )

    def parse_result(self, response: Response):
        item = response.meta["item"]
        results = (
            response.css("table.is-w495 tbody tr td").xpath("string()").getall()[:24]
        )
        for (result, boat_number, _, time) in chunked(results, 4):
            item["racers"][int(boat_number) - 1]["result"] = result
            item["racers"][int(boat_number) - 1]["race_time"] = time.strip()

        starts = (
            response.css("table.is-h292__3rdadd tbody tr").xpath("string()").getall()
        )
        starts = list(map(lambda x: x.split(), starts))
        for i, row in enumerate(starts):
            boat_number = int(row[0])
            start_time = row[1]
            item["racers"][boat_number - 1]["entry"] = i + 1
            item["racers"][boat_number - 1]["start_time"] = start_time

        item["result_reason"] = (
            response.css("table.is-h108__3rdadd td").xpath("string()").get()
        )
        yield item
