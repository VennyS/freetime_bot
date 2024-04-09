from psycopg2.extras import DateTimeRange, Range
import datetime
import json

class timeIntervals:
    monthsDict = {
        11: "Декабрь", 0: "Январь", 1: "Февраль",
        2: "Март", 3: "Апрель", 4: "Май",
        5: "Июнь", 6: "Июль", 7: "Август",
        8: "Сентябрь", 9: "Октябрь",  10: "Ноябрь"
    }

    def __init__(self, timeRange: list[tuple] | list[dict] | str):
        self.intervals = []
        if isinstance(timeRange, list) or isinstance(timeRange, str):
            if isinstance(timeRange[0], tuple):
                for tup in timeRange:
                    for interval in tup[0]:
                        self.intervals.append(interval)
            elif isinstance(timeRange[0], dict) or isinstance(timeRange[0], str):
                if isinstance(timeRange, str): timeRange = json.loads(timeRange)
                for item in timeRange:
                    start_time_str = f"{item['year']}-{item['month']}-{item['day']} {item['startTime']}"
                    end_time_str = f"{item['year']}-{item['month']}-{item['day']} {item['endTime']}"
                    start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                    end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                    datetime_range = DateTimeRange(start_time, end_time, bounds='[]')
                    self.intervals.append(datetime_range)
            else: raise ValueError('Внутренний формат данных списка не распознан')
        else: raise ValueError('Тип данных должен быть либо списком с кортежами, либо списком с словарями')
        
    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.intervals):
            result = self.intervals[self.index]
            self.index += 1
            return result
        raise StopIteration

    def __str__(self): return self.allToJSON()

    def allToJSON(self, inARow: bool = False):
        jsonMass = []
        for interval in self.intervals:
            interval_dict = {
                "year": interval.lower.year,
                "month": interval.lower.month,
                "day": interval.lower.day,
                "name": self.monthsDict[interval.lower.month],
                "startTime": f"{interval.lower.hour:02d}:{interval.lower.minute:02d}",
                "endTime": f"{interval.upper.hour:02d}:{interval.upper.minute:02d}"
            }
            jsonMass.append(interval_dict)
        separators = (', ', ': ') if inARow else None
        indent = None if inARow else 4
        return json.dumps(jsonMass, ensure_ascii=False, separators=separators, indent=indent)

    def hideQuote(self):
        json_string = self.allToJSON(True)
        escaped_json_string = ""

        for char in json_string:
            if char == '"':
                escaped_json_string += "%22"
            elif char == ',':
                escaped_json_string += "%2C"
            elif char == ' ':
                escaped_json_string += "%20"
            elif char == ':':
                escaped_json_string += "%3A"
            else:
                escaped_json_string += char

        return escaped_json_string
    
    def toTSRange(self):
        freetime_str = ','.join([f"'[{item.lower},{item.upper}]'::tsrange" for item in self.intervals])
        # Формируем массив для PostgreSQL
        freetime_array = f"ARRAY[{freetime_str}]"
        return freetime_array

