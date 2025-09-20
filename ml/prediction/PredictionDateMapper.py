#Garantees that predictions are mapped to valid trading days/times

import calendar
import pandas as pd
import pandas_market_calendars as mcal

class PredictionDateMapper:
    def __init__(self, exchange="NYSE"):
        self.calendar = mcal.get_calendar(exchange)

        self.daysFuture=365
        self.daysPast = 30


        today = pd.Timestamp.utcnow().normalize()

        schedule = self.calendar.schedule(
            start_date=today - pd.Timedelta(days=self.daysPast),
            end_date=today + pd.Timedelta(days=self.daysFuture)
        )

        self.dayMap = self.precomputeIntervals(schedule, "1d")
        self.hourMap = self.precomputeIntervals(schedule, "1h")




    def mapPredictions(self, startDate, predictionPackets, interval):

        if startDate.tzinfo is None:
            startDate = startDate.tz_localize("UTC")

        if interval == "1d":
            valid_times = self.dayMap
            fmt = "%Y-%m-%d"
        elif interval == "1h":
            valid_times = self.hourMap
            fmt = "%Y-%m-%d-%H"
        else:
            raise ValueError("invalid format")

        valid_times = valid_times[valid_times > startDate]

        n_predictions = len(predictionPackets)
        if len(valid_times) < n_predictions:
            raise ValueError("not enough intervalls")

        next_times = valid_times[:n_predictions]

        for packet, ts in zip(predictionPackets, next_times):
            packet.date = ts.strftime(fmt)

        return predictionPackets


        assign_times = valid_times[:len(predictionPackets)].to_list()

        fmt = "%Y-%m-%d"
        if interval == "1d":
            fmt = "%Y-%m-%d"
        elif interval == "1h":
            fmt = "%Y-%m-%d-%H"

        for packet, ts in zip(predictionPackets, assign_times):
            packet.date = ts.strftime(fmt)

        return predictionPackets





    #private
    def precomputeIntervals(self, schedule, interval):
        intervals = []
        for market_open, market_close in zip(schedule.market_open, schedule.market_close):
            if interval == "1d":
                intervals.append(market_open)
            elif interval == "1h":
                times = pd.date_range(
                    start=market_open,
                    end=market_close,
                    freq="1H",
                    inclusive="left"
                )
                intervals.extend(times)

        return pd.DatetimeIndex(intervals).tz_convert("UTC")