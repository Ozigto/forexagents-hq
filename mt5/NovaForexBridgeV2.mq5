#property strict
#property version "2.00"
#property description "Read-only ForexAgents HQ bridge: exports ticks + closed H1/H4 candles. No trading."

input int UpdateSeconds = 30;
input int CandleCount = 120;

string symbols[] = {"EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD","XAUUSD"};
ENUM_TIMEFRAMES frames[] = {PERIOD_H1, PERIOD_H4};
string frameNames[] = {"H1", "H4"};

string ResolveSymbol(string base)
{
   if(SymbolSelect(base, true))
      return base;
   int total = SymbolsTotal(false);
   for(int i=0; i<total; i++)
   {
      string candidate = SymbolName(i, false);
      if(StringFind(candidate, base) == 0)
      {
         if(SymbolSelect(candidate, true))
            return candidate;
      }
   }
   total = SymbolsTotal(true);
   for(int j=0; j<total; j++)
   {
      string selected = SymbolName(j, true);
      if(StringFind(selected, base) == 0)
      {
         if(SymbolSelect(selected, true))
            return selected;
      }
   }
   return "";
}

int OnInit()
{
   EventSetTimer(UpdateSeconds);
   for(int i=0; i<ArraySize(symbols); i++)
      ResolveSymbol(symbols[i]);
   Print("NovaForexBridgeV2 started READ-ONLY. Exports ticks and closed H1/H4 candles. No trading functions.");
   ExportMarketData();
   ExportCandles();
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   EventKillTimer();
}

void OnTimer()
{
   ExportMarketData();
   ExportCandles();
}

void ExportMarketData()
{
   int handle = FileOpen("nova_forex_market.csv", FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
   if(handle == INVALID_HANDLE)
   {
      Print("NovaForexBridgeV2: market FileOpen failed. Error=", GetLastError());
      return;
   }
   FileWrite(handle, "symbol", "bid", "ask", "spread_points", "tick_time", "server_time", "status");
   datetime server_time = TimeTradeServer();
   for(int i=0; i<ArraySize(symbols); i++)
   {
      string symbol = symbols[i];
      string actual = ResolveSymbol(symbol);
      if(actual == "")
      {
         FileWrite(handle, symbol, "", "", "", "", TimeToString(server_time,TIME_DATE|TIME_SECONDS), "SYMBOL_NOT_AVAILABLE");
         continue;
      }
      MqlTick tick;
      if(!SymbolInfoTick(actual, tick) || tick.time <= 0)
      {
         FileWrite(handle, actual, "", "", "", "", TimeToString(server_time,TIME_DATE|TIME_SECONDS), "NO_TICK");
         continue;
      }
      double point = SymbolInfoDouble(actual,SYMBOL_POINT);
      double spread = 0;
      if(point > 0)
         spread = (tick.ask-tick.bid)/point;
      long age = 0;
      if(server_time > tick.time)
         age = (long)(server_time-tick.time);
      string status = "LIVE";
      if(age > 300)
         status = "STALE_OR_MARKET_CLOSED";
      FileWrite(handle, actual, DoubleToString(tick.bid,8), DoubleToString(tick.ask,8), DoubleToString(spread,1), TimeToString(tick.time,TIME_DATE|TIME_SECONDS), TimeToString(server_time,TIME_DATE|TIME_SECONDS), status);
   }
   FileClose(handle);
}

void ExportCandles()
{
   int handle = FileOpen("nova_forex_candles.csv", FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
   if(handle == INVALID_HANDLE)
   {
      Print("NovaForexBridgeV2: candles FileOpen failed. Error=", GetLastError());
      return;
   }
   FileWrite(handle, "symbol", "timeframe", "time", "open", "high", "low", "close", "tick_volume", "is_closed", "server_time");
   datetime server_time = TimeTradeServer();
   for(int s=0; s<ArraySize(symbols); s++)
   {
      string symbol = symbols[s];
      string actual = ResolveSymbol(symbol);
      if(actual == "")
         continue;
      for(int f=0; f<ArraySize(frames); f++)
      {
         MqlRates rates[];
         ArraySetAsSeries(rates, true);
         int copied = CopyRates(actual, frames[f], 0, CandleCount + 1, rates);
         if(copied <= 1)
            continue;
         // rates[0] is the forming candle. Export it as not closed for visibility, then closed history.
         for(int i=copied-1; i>=0; i--)
         {
            bool is_closed = (i != 0);
            FileWrite(
               handle,
               actual,
               frameNames[f],
               TimeToString(rates[i].time,TIME_DATE|TIME_SECONDS),
               DoubleToString(rates[i].open,8),
               DoubleToString(rates[i].high,8),
               DoubleToString(rates[i].low,8),
               DoubleToString(rates[i].close,8),
               IntegerToString((int)rates[i].tick_volume),
               is_closed ? "true" : "false",
               TimeToString(server_time,TIME_DATE|TIME_SECONDS)
            );
         }
      }
   }
   FileClose(handle);
}
