#! /usr/bin/env python3

# Server to aggregate logs.

import logging
import logging.handlers
import zipfile
import sys, os, time

import zmq

class TimedCompressedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Extended version of TimedRotatingFileHandler that compress logs on rollover.

    """
    def doRollover(self):
        """
        Do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.

        subclassed to add zip compression to doRollover        
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
             for s in self.getFilesToDelete():
                 os.remove(s)
        self.mode = 'w'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    newRolloverAt = newRolloverAt - 3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt

        # adding compression functionality
        if os.path.exists(dfn + ".zip"):
            os.remove(dfn + ".zip")
        file = zipfile.ZipFile(dfn + ".zip", "w")
        file.write(dfn, os.path.basename(dfn), zipfile.ZIP_DEFLATED)
        file.close()
        os.remove(dfn)

if __name__ == '__main__':

    # zmq setup
    # uses zmq pattern of pipeline.
    # Server is the "pull" context
    # (Clients are the "push" context
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    incoming_port = sys.argv[1] if len(sys.argv) >1 and (sys.argv[1] < 65535) else "5555"
    receiver.bind("tcp://*:{}".format(incoming_port))

    # logging setup
    logformatter = logging.Formatter('%(asctime)s;%(message)s')
    if not os.path.exists("logs/"):
        os.makedirs("logs/")
    file_path = "logs/aggregator.log"
    handler = TimedCompressedRotatingFileHandler(file_path,
                                                when='s', # minutes
                                                interval=10)
    handler.setFormatter(logformatter)
    logger = logging.getLogger("Log Aggregator, Timed Rotating")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Work loop
    while True:
        # wait for next request from client
        message = receiver.recv()
        print("received log: %s" % message)

        # write message to compressed filesystem
        logger.info(message)

