# region imports
from AlgorithmImports import *
# endregion

class FirstAlgoTesting(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 9, 18)
        self.SetCash(100000)
        self.ticker = self.AddEquity("SPY", Resolution.Minute)
        self.newma = self.SMA(self.ticker.Symbol, 100)
        self.rsi = self.RSI(self.ticker.Symbol,14, Resolution.Minute)

        self.Consolidate(self.ticker.Symbol, timedelta(minutes = 30), self.OnDataConsolidated)

        self.SetWarmup(100)

    def OnData(self, data: Slice):
        pass

    def OnDataConsolidated(self, bar):
        self.currentbar = bar
        self.Plot("30 min Chart", "Close", self.currentbar.Close)
