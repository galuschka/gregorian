""" date calculation on Gregorian calendar

This class uses the hypothetical date Mar 1st 0 as reference.
The main unit of this class is "days" - which means number of days past Mar 1st 0
Year 0 does not exist, but we assume Gregorian calendar also for years < 1600.
When starting at Mar 1st, the number of days per month has an algebraic logic:
                           |   |   |   |   |
                           v   v   v   v   v
    Mar,Apr,May,Jun,Jul:  31, 30, 31, 30, 31   ∑: 153 days
    Aug,Sep,Oct,Nov,Dec:  31, 30, 31, 30, 31   ∑: 153 days
    Jan,Feb:              31, rest             leap year day just added at end of list

So we just need integer arithmetic. Not any "if" is necessary.
"""

class Gregorian:
    def __init__(self):
        self._DAYS1970 = self.daysJan1st( 1970 )  # UNIX epoch start date
        self._WDAY0    = 2                        # hypothetical Jan 1st 0 was Wednesday
        self._DAYS1Y   = 365
        self._DAYS4Y   = self._DAYS1Y   *  4 + 1  #   1461 days - leap year every 4th year
        self._DAYS100Y = self._DAYS4Y   * 25 - 1  #  36524 days - not leap year every 100th year
        self._DAYS400Y = self._DAYS100Y *  4 + 1  # 146097 days - again leap year every 400th year

    def days2wday( self, days:int ):
        """ return week day of a "days" date
        """
        return (days + self._WDAY0) % 7  # 0:Monday, ... 6:Sunday

    def time2days( self, time:float ):
        """ convert UNIX epoch time into "days"
        """
        return int(time / 86400.0) + self._DAYS1970

    def days2time( self, days:int ):
        """ convert "days" into UNIX epoch time (0:00:00 UTC)
        """
        return (days - self._DAYS1970) * 86400.0

    def daysJan1st( self, year:int ):
        """ return number days past Mar 1st 0 until Jan 1st year
        """
        y_corr = year - 1  # jan/feb: 1 year before y
        mar1st = y_corr * 365 + (y_corr//4) - (y_corr//100) + (y_corr//400)

        return mar1st + 2*153  # days_past_mar1 is fix: 2*153

    def days( self, year:int, month:int, day:int ):
        """ return number days past Mar 1st 0 until year month day
        """
        assert 1 <= month <= 12, f'{month=} not in 1..12'
        assert 1 <=  day  <= 31,   f'{day=} not in 1..31'

        m3     = (month + 9) % 12   # 1,2 -> 10,11 / 3,4,..,12 -> 0..9
        y_corr = year - (m3 // 10)  # jan/feb: 1 year before y
        mar1st = y_corr * 365 + (y_corr//4) - (y_corr//100) + (y_corr//400)

        d153 = m3 // 5  # 153 days every 5 months
        m5   = m3 %  5
        d61  = m5 // 2  # 61 days every 2 months
        d31  = m5 %  2  # mar,may,jul etc.: 31 days
        days_past_mar1 = (d153 * 153) + (d61 * 61) + (d31 * 31) + day - 1

        return mar1st + days_past_mar1  # Mar 1st plus just arithmetic calculation

    def date( self, days:int ):
        """ invert of days(): return year.month,day of given "days"
        """
        y400  =     days // self._DAYS400Y
        days -=     y400 *  self._DAYS400Y
        y100  = min(days // self._DAYS100Y,3)  # 0..3: 146096/36524==4! - every 4th century has 1 more day
        days -=     y100 *  self._DAYS100Y
        y4    =     days // self._DAYS4Y       # 0..24: (every century has one day less - 24 is max. anyway)
        days -=     y4   *  self._DAYS4Y
        y1    = min(days // self._DAYS1Y, 3)   # 0..3: 1460/365==4! - every 4th year has 1 more day
        days -=     y1   *  self._DAYS1Y       # days here: days past Mar 1st (0..365)

        y_corr = (y400 * 400) + (y100 * 100) + (y4 * 4) + y1

        # print( f"{y_corr=} = {y400=}*400 + {y100=}*100 + {y4=}*4 + {y1=}" )

        m153  = days // 153  # 0..2: number of 5 months blocks 31,30,31,30,31
        days -= m153 *  153
        m61   = days //  61  # 0..2: number of 2 months blocks 31,30
        days -= m61  *   61
        m31   = days //  31  # 0..1: number of 31 days months
        days -= m31  *   31  # remaining days: days past 1st of month - also when February
        day   = days + 1                    # day of month 1..31
        m3 = (m153 * 5) + (m61 * 2) + m31   # 0=mar, .. 11=feb

        # print( f"{m3=} = {m153=}*5 + {m61=}*2 + {m31=} / remaining {days=}" )

        year = y_corr + (m3 // 10)          # revert y_corr for jan/feb

        month = ((m3 + 2) % 12) + 1  # 0->3, 1->4, ..., 9->12, 10->1, 11->2

        return year, month, day

    def yday( self, year:int, month:int, day:int ):
        """ year day: number of days past Jan 1st of given date (==> Jan1 = 0)
        """
        return self.days( year, month, day ) - self.daysJan1st( year )

    def wday( self, year:int, month:int, day:int ):
        """ week day of given date (0 = Monday)
        """
        return self.days2wday( self.days( year, month, day ) )
