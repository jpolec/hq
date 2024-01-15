def get_sp500_df():
    """
    look at documentation!: pypi.org/project/yfinance
    """
    
    filename = f"output/dumps/SP500_temp.dump"
    
    use_disk = False
    
    # Check if file exists
    if os.path.exists(filename):
        print("Data exists on disk, checking if data is stale...")
        (df, instruments) = gu.load_file(filename)     
        
        today = datetime.today().replace(tzinfo=None)
        # Get the last updated date from the index of the DataFrame
        last_date_in_df = df.index.max().replace(tzinfo=None)  # Convert to timezone-naive datetime
        
        if today - last_date_in_df >= timedelta(days=100):
            print("Data is more than 100 days old, fetching new data...")
            use_disk = False
        else:
            print('Data is up to date, using data from disk')
            use_disk = True
    else:
        print("No data on disk, fetching new data...")
        use_disk = False
        
    if not use_disk:
        
        symbols = get_sp500_instruments()
        # To save time, let us perform ohlcv retrieval for 30 stocks
        # symbols = symbols[:10]
        ohlcvs = {}
        
        for symbol in symbols:
            symbol_df = yf.Ticker(symbol).history(period="10y") #this gives us the OHLCV Dividends + Stock Splits
            # We are interested in the OHLCV mainly, let's rename them 
            ohlcvs[symbol] = symbol_df[["Open", "High", "Low", "Close", "Volume"]].rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume"
                }
            )
            print(symbol)
            #print(ohlcvs[symbol]) #we can now get the data that we want inside a nicely formatted df
        
        #now, we want to put that all into a single dataframe.
        #since the columns need to be unique to identify the instrument, we want to add an identifier.
        #let's steal the GOOGL index as our dataframe index
        df = pd.DataFrame(index=ohlcvs["ADBE"].index)
        df.index.name = "date"
        instruments = list(ohlcvs.keys())

        dfs_to_concat = [df]  # Start with your base DataFrame

        for inst in instruments:
            inst_df = ohlcvs[inst]
            columns = list(map(lambda x: "{} {}".format(inst, x), inst_df.columns)) #this tranforms open, high... to AAPL open , AAPL high and so on
            inst_df.columns = columns  # Rename columns before concatenation
            dfs_to_concat.append(inst_df)
            
        # Concatenate all dataframes at once
        df = pd.concat(dfs_to_concat, axis=1)
        
            # inst_df = ohlcvs[inst]
            # columns = list(map(lambda x: "{} {}".format(inst, x), inst_df.columns)) #this tranforms open, high... to AAPL open , AAPL high and so on
            # df[columns] = inst_df
            
        # Save the data to disk
        print("Saving data to disk.")
        gu.save_file(filename, (df, instruments))

    return df, instruments
