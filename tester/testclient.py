#!/usr/bin/env jython

"""
Example of testing a trading strategy using the
ITesterClient returned from TesterFactory.
"""

import os
import sys

from java.util import Date
from java.lang import Thread

import org.apache.log4j as log4j

from com.dukascopy.api import IStrategy, Instrument, LoadingProgressListener, Period, OfferSide
from com.dukascopy.api.system import TesterFactory, ITesterClient, ISystemListener
from com.dukascopy.dds2.greed.util import FilePathManager
from com.dukascopy.api.feed import IBarFeedListener

from filewatcher import watch_file_for_changes

LOGIN = None
PASSWORD = None
JNLP = os.path.expanduser('~/Downloads/jforex/jforex.jnlp')

STRATEGY_PATH = os.path.expanduser('~/JForex/')

STARTDATE = (112, 0, 0)
ENDDATE = (112, 4, 24)

class SystemListener(ISystemListener):
    def onConnect(self):
        print 'Connected.'

    def onDisconnect(self):
        print 'Disconnected.'

    def onStart(self, processId):
        print 'Started %i.' % (processId,)

    def onStop(self, processId):
        print 'Stopped %i.' % (processId,)

class ProgressListener(LoadingProgressListener):
    def dataLoaded(self, start, end, currentPosition, information):
        print 'Data Loaded: ', start, end, currentPosition, information

    def loadingFinished(self, allDataLoaded, start, end, currentPosition):
        print 'Loading Finished: ', allDataLoaded, start, end, currentPosition

    def stopJob(self):
        return False

class DownloadListener(LoadingProgressListener):
    def dataLoaded(self, start, end, currentPosition, information):
        print 'Downloading: ', start, end, currentPosition, information

    def loadingFinished(self, allDataLoaded, start, end, currentPosition):
        print 'Downloading Finished: ', allDataLoaded, start, end, currentPosition

    def stopJob(self):
        return False


def load_strategy_from_module(modulepath):
    import traceback

    cls = None

    execglobals = globals().copy()
    execlocals = {}
    try:
        execfile(modulepath, execglobals, execlocals)
        execglobals.update(execlocals)
        cls = eval('Strategy', execglobals)
    except Exception, e:
        traceback.print_exc()
    return cls

def main():
    assert len(sys.argv) == 2

    strategy_module = sys.argv[1]

    path_manager = FilePathManager.getInstance()
    path_manager.setStrategiesFolderPath(STRATEGY_PATH)

    client = TesterFactory.getDefaultInstance()
    client.setSystemListener(SystemListener())
    client.connect('file://' + JNLP, LOGIN, PASSWORD)

    client.setSubscribedInstruments({Instrument.EURUSD})
    client.setInitialDeposit(Instrument.EURUSD.getSecondaryCurrency(), 5000)
    client.setDataInterval(ITesterClient.DataLoadingMethod.ALL_TICKS, Date(*STARTDATE).getTime(), Date(*ENDDATE).getTime())
    client.downloadData(DownloadListener())

    Thread.sleep(5000)

    while 1:
        strategy_class = load_strategy_from_module(strategy_module)

        if strategy_class:
            strategy = strategy_class()
            client.startStrategy(strategy, ProgressListener())

        watch_file_for_changes(strategy_module)

    #client.compileStrategy(os.path.join(STRATEGY_PATH, 'Strategy.java'), False)

if __name__ == '__main__':
    #log4j.BasicConfigurator.configure()
    main()
