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

    def __init__(self, timeRange: tuple[int, list] | list[int, dict] | str):
        self.intervals = []
        if isinstance(timeRange, tuple):
            if (isinstance(timeRange[1], list)):
                for interval in timeRange[1]:
                    self.intervals.append(interval)
                self.telegramid = timeRange[0]
            else: raise ValueError('Внутренний формат данных кортежа не распознан')
        elif isinstance(timeRange, list): 
            if (isinstance(timeRange[1], dict)):
                for interval in timeRange[1:]:
                    start_time_str = f"{interval['year']}-{interval['month']}-{interval['day']} {interval['startTime']}"
                    # Проверяем, если endTime равно 24
                    if interval['endTime'] == "24:00":
                        # Увеличиваем день на 1 и устанавливаем startTime в полночь
                        next_day = datetime.datetime(int(interval['year']), int(interval['month']), int(interval['day'])) + datetime.timedelta(days=1)
                        end_time_str = f"{next_day.year}-{next_day.month}-{next_day.day} 00:00"
                    else:
                        end_time_str = f"{interval['year']}-{interval['month']}-{interval['day']} {interval['endTime']}"

                    start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                    end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                    datetime_range = DateTimeRange(start_time, end_time, bounds='[]')
                    self.intervals.append(datetime_range)

                self.telegramid = timeRange[0]
            else: raise ValueError('Внутренний формат данных списка не распознан')
        elif timeRange is None: return
        else: raise ValueError('Тип данных не соответствует спецификации')
        
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
        if (self.intervals):
            jsonMass = []
            for interval in self.intervals:
                interval_dict = {
                    "year": interval.lower.year,
                    "month": interval.lower.month-1,
                    "day": interval.lower.day,
                    "name": self.monthsDict[interval.lower.month-1],
                    "startTime": f"{interval.lower.hour:02d}:{interval.lower.minute:02d}",
                    "endTime": f"{interval.upper.hour:02d}:{interval.upper.minute:02d}" if interval.upper.hour != 0 else
                    "24:00"
                }
                jsonMass.append(interval_dict)
            separators = (', ', ': ') if inARow else None
            indent = None if inARow else 4
            return json.dumps(jsonMass, ensure_ascii=False, separators=separators, indent=indent)
        else: return 'null'

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
    
    def intervalsToTSRange(self):
        freetime_str = ','.join([f"'[{item.lower},{item.upper}]'::tsrange" for item in self.intervals])
        # Формируем массив для PostgreSQL
        freetime_array = f"ARRAY[{freetime_str}]"
        return freetime_array

