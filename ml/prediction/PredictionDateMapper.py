#Garantees that predictions are mapped to valid trading days/times

import calendar
import pandas as pd
import pandas_market_calendars as mcal

class PredictionDateMapper:
    def __init__(self, exchange="NYSE"):
        self.calendar = mcal.get_calendar(exchange)

        self.daysFuture = 365
        self.daysPast = 30

        today = pd.Timestamp.utcnow().normalize()

        schedule = self.calendar.schedule(
            start_date=today - pd.Timedelta(days=self.daysPast),
            end_date=today + pd.Timedelta(days=self.daysFuture)
        )

        self.dayMap = self.precomputeIntervals(schedule, "1d")
        self.hourMap = self.precomputeIntervals(schedule, "1h")

    # private
    def precomputeIntervals(self, schedule, interval):
        intervals = []

        for market_open, market_close in zip(schedule.market_open, schedule.market_close):
            market_open_et = market_open.tz_convert("America/New_York")
            market_close_et = market_close.tz_convert("America/New_York")

            pre_open_et = market_open_et.replace(hour=4, minute=0, second=0, microsecond=0)    # Pre-Market 04:00 ET
            post_close_et = market_close_et.replace(hour=20, minute=0, second=0, microsecond=0)  # After-Hours 20:00 ET

            if interval == "1d":
                midnight_utc = pre_open_et.tz_convert("UTC").normalize()
                intervals.append(midnight_utc)
            elif interval == "1h":
                times = pd.date_range(
                    start=pre_open_et,
                    end=post_close_et,
                    freq="1h",
                    inclusive="left"
                )

                times = times.tz_convert("UTC")
                intervals.extend(times)

        return pd.DatetimeIndex(intervals)



    def mapPredictions(self, startDate, predictionPackets, interval):

        if startDate.tzinfo is None:
            startDate = startDate.tz_localize("UTC")

        if interval == "1d":
            valid_times = self.dayMap
        elif interval == "1h":
            valid_times = self.hourMap
        else:
            raise ValueError("invalid format")

        valid_times = (
            valid_times[valid_times > startDate] 
            if interval == "1h" 
            else pd.DatetimeIndex([ts for ts in valid_times if ts.date() > startDate.date()])
        )
        n_predictions = len(predictionPackets)
        if len(valid_times) < n_predictions:
            raise ValueError("not enough intervalls")

        next_times = valid_times[:n_predictions]

        for packet, ts in zip(predictionPackets, next_times):
            packet.date = ts.replace(minute=0, second=0, microsecond=0)

        return predictionPackets