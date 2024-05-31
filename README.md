<p align="center"><img src="https://socialify.git.ci/samm-o/Automatic-Trading-Platform/image?description=1&amp;descriptionEditable=An%20algorithm%20based%20automatic%20stock%20trading%20platform%20connected%20to%20Interactive%20Brokers.&amp;font=Inter&amp;language=1&amp;name=1&amp;owner=1&amp;pattern=Circuit%20Board&amp;theme=Auto" alt="project-image"></p>

# Automatic Stock Trading Platform

The Automatic stock trading platform seamlessly integrates with Interactive Brokers to automate stock trading, eliminating the need for users to constantly monitor charts. The platform leverages advanced algorithms to execute trades on selected stocks based on predefined strategies. It ensures efficient and accurate trading by continuously processing real-time data and executing trades without manual intervention. This user-friendly solution is designed to optimize trading performance, allowing users to focus on strategic planning rather than the intricacies of daily market movements.

---
## Highlights
1. **Comprehensive Dashboard**: Provides users with access to detailed information on over 12,000 US stocks.
2. **Automated Trading**: Facilitates preset order parameters for automated stock transactions, eliminating the need for manual trading.
3. **High-Speed Data Processing**: Utilizes a concurrent system to update daily prices 15x faster than traditional single-threaded implementations.
4. **Robust Data Management**: Implements a MySQL database for efficient and reliable storage of application data.

---
## Example of Pre-defined Strategy

<h4>opening range breakout</h4>

```python
for symbol in symbols:

    # Request historical data
    contract = Stock(symbol, 'SMART', 'USD')
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
    )

    # Convert historical data to pandas DataFrame
    df = util.df(bars)

    # Set the index to the timestamp column
    df.set_index('date', inplace=True)

    # Rename columns to match the existing code
    df.rename(columns={'low': 'low', 'high': 'high', 'close': 'close'}, inplace=True)

    minute_bars = df

    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low
    
    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]
    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]
        
    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            try:
                limit_price = after_opening_range_breakout.iloc[0]['close']
                quantity = calc_quantity(limit_price)
                
                messages.append(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")    
                print(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")

                # Create a contract
                contract = Stock(symbol, 'SMART', 'USD')

                # Create a market buy order
                buy = buy_order(quantity)
                
                # Create a take profit order
                take_profit_price = limit_price + opening_range
                take_profit = take_profit_order(quantity, take_profit_price)
                
                # Create a stop loss order
                stop_loss_price = limit_price - opening_range
                stop_loss = stop_order(quantity, stop_loss_price)
                
                # Create a trailing stop order (Percentage)
                trailing_stop = trailing_stop_order(quantity, 0.6)
                
```
---
## Roadmap
- [x] Automate the trading process with pre-defined strategies
- [x] Create a back trader to test algorithms and show algorithm results
- [ ] Streamline user experience by providing customization panels per order on the front-end
- [ ] Integrate Machine learning to analyze charts for the user and have it make decisions
- [ ] Possibly algo development through AI? (very ambitious!)
 
----
## FAQ

##### How fast is the data processing on the platform?
The platform features a concurrent system that updates daily prices 15 times faster than a single-threaded implementation. It takes about an hour to process a YEAR's worth of MINUTE data for the companies in the QQQ (around 100).

##### Do I need to monitor the platform constantly?

No, the platform is designed to automate trading, so you do not need to monitor it constantly. It executes trades based on predefined algorithms and parameters.

##### How do I get started with the platform?

To get started, you need to set up an account with Interactive Brokers, integrate it with the platform, and configure your trading parameters. Detailed instructions are provided in the user guide.
