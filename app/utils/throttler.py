import datetime
import logging
import time
class TooManyRequestsError(Exception):
    def __str__(self):
        return "More than 30 requests have been made in the last five seconds."


class Throttler(object):
    cache = {}

    def __init__(self, max_rate, window, throttle_stop=False, cache_age=1800):
        # Dict of max number of requests of the API rate limit for each source
        self.max_rate = max_rate
        # Dict of duration of the API rate limit for each source
        self.window = window
        # Whether to throw an error (when True) if the limit is reached, or wait until another request
        self.throttle_stop = throttle_stop
        # The time, in seconds, for which to cache a response
        self.cache_age = cache_age
        # Initialization
        self.next_reset_at = dict()
        self.num_requests = dict()

        now = datetime.datetime.now()
        for source in self.max_rate:
            self.next_reset_at[source] = now + datetime.timedelta(seconds=self.window.get(source))
            self.num_requests[source] = 0

    def request(self, source, method, do_cache=False):
        now = datetime.datetime.now()

        # if cache exists, no need to make api call
        key = source + method.__name__
        if do_cache and key in self.cache:
            timestamp, data = self.cache.get(key)
            logging.info('{} exists in cached @ {}'.format(key, timestamp))

            if (now - timestamp).seconds < self.cache_age:
                logging.info('retrieved cache for {}'.format(key))
                return data

        # <--- MAKE API CALLS ---> #

        # reset the count if the period passed
        if now > self.next_reset_at.get(source):
            self.num_requests[source] = 0
            self.next_reset_at[source] = now + datetime.timedelta(seconds=self.window.get(source))

        # throttle request
        def halt(wait_time):
            if self.throttle_stop:
                raise TooManyRequestsError()
            else:
                # Wait the required time, plus a bit of extra padding time.
                time.sleep(wait_time + 0.1)

        # if exceed max rate, need to wait
        if self.num_requests.get(source) >= self.max_rate.get(source):
            logging.info('back off: {} until {}'.format(source, self.next_reset_at.get(source)))
            halt((self.next_reset_at.get(source) - now).seconds)

        self.num_requests[source] += 1
        response = method()  # potential exception raise

        # cache the response
        if do_cache:
            self.cache[key] = (now, response)
            logging.info('cached instance for {}, {}'.format(source, method))

        return response