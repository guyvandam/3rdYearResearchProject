import sys
sys.path.append('./')
from constants import (ATR_ABNORMALITY_COLUMN, ATR_COLUMN, HIGH_COLUMN, HIGH_TIMESTAMP_COLUMN, LOW_TIMESTAMP_COLUMN,
                       LOW_COLUMN, PRECENT_CHANGE_INDECATOR, ATR_ABNORMALITY_THRESHOLD, HIGH_TO_LOW_PRECENT_CHANGE_COLUMN)



class PreProcess():
    ############################### get atr of last n sessions.
    def get_atr(self, df, n):
        copied_df = df.copy()
        high = df[HIGH_COLUMN]
        low = df[LOW_COLUMN]
        close = df['close']
        
        copied_df['tr0'] = abs(high - low)
        copied_df['tr1'] = abs(high - close.shift())
        copied_df['tr2'] = abs(low - close.shift())

        true_range = copied_df[['tr0', 'tr1', 'tr2']].max(axis=1)

        ################################ if we don't want the first 14 points to be blank. add min_periods=1
        # atr = true_range.rolling(window=n, min_periods=1, axis=0).mean() 

        atr = true_range.rolling(window=n, axis=0).mean()
        return atr

    ################################ add ATR column.
    def add_atr_column(self, df, n=14):
        df[ATR_COLUMN] = self.get_atr(df,n=n)

    ############################### add ATR abnormality column.
    def add_atr_abnormality_column(self, df):
        if not ATR_COLUMN in df.columns:
            self.add_atr_column(df)

        df[ATR_ABNORMALITY_COLUMN] = df[HIGH_COLUMN] - df[LOW_COLUMN] > df[ATR_COLUMN] * ATR_ABNORMALITY_THRESHOLD
        df[ATR_ABNORMALITY_COLUMN] = df[ATR_ABNORMALITY_COLUMN].astype(int)

    ############################### add precent change column.
    def add_precent_change_column(self, df, column_name):
        precent_change_column_name = column_name + PRECENT_CHANGE_INDECATOR
        change_series = df[column_name].pct_change().mul(100)
        df[precent_change_column_name] = change_series

    ############################### add high -> low or low -> high precent change.
    def add_high_to_low_precent_change_column(self, df, kline_size, short_df, is_add_high_low_timestamp_columns = True):
        empty_counter = 0
        resampled_df_list = list(short_df.resample(kline_size))
        df[HIGH_TO_LOW_PRECENT_CHANGE_COLUMN] = 0

        for timestamp, temp_df in resampled_df_list:
            try:
                high = df.loc[timestamp, HIGH_COLUMN]
                low = df.loc[timestamp, LOW_COLUMN]
                
                low_timestmamp = temp_df[LOW_COLUMN].idxmin()
                high_timestmap = temp_df[HIGH_COLUMN].idxmax()

                first, second = low, high
                if low_timestmamp > high_timestmap: # going from high to low, as timestamp of low is after (bigger) than timestamp of high.
                    first, second = high, low
                
                change_value = float((second - first) / first) * 100
                df.loc[timestamp, HIGH_TO_LOW_PRECENT_CHANGE_COLUMN] = change_value
                
                if is_add_high_low_timestamp_columns:
                    df.loc[timestamp, LOW_TIMESTAMP_COLUMN] = low_timestmamp
                    df.loc[timestamp, HIGH_TIMESTAMP_COLUMN] = high_timestmap
            except:
                empty_counter += 1

        
        ############################### print skiping precent
        empty_precent = (empty_counter/len(resampled_df_list)) * 100
        if empty_precent >= 10:
            print("skiping precent in H-L calculations: ", empty_precent)