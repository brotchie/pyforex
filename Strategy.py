from com.dukascopy.api import IStrategy, Instrument

print 'Reloaded'

class Strategy(IStrategy):
    def onStart(self, context):
        self.context = context
        self.context.console.getInfo().println('Python Module Initialized.')

    def onAccount(self, account):
        pass

    def onMessage(self, message):
        print message
        pass

    def onStop(self):
        self.context.console.getInfo().println('Python Strategy Stopping.')

    def onTick(self, instrument, tick):
        print tick.getAsk() - tick.getBid()
        print tick.getBidVolume(), tick.getAskVolume()

    def onBar(self, instrument, period, askbar, bidbar):
        pass
