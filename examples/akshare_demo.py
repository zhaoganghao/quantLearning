"""
AkShare 使用示例
演示如何使用 AkShare 获取各种金融数据
"""

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


def example_1_stock_realtime():
    """示例1: 获取股票实时行情"""
    print("=" * 60)
    print("示例1: 获取股票实时行情")
    print("=" * 60)
    
    try:
        # 获取沪深A股实时行情
        stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
        print("\n前10只股票的实时行情:")
        print(stock_zh_a_spot_df.head(10))
        print(f"\n总共获取了 {len(stock_zh_a_spot_df)} 只股票的数据")
    except Exception as e:
        print(f"获取股票实时行情失败: {e}")


def example_2_stock_history():
    """示例2: 获取股票历史数据"""
    print("\n" + "=" * 60)
    print("示例2: 获取股票历史数据")
    print("=" * 60)
    
    try:
        # 获取平安银行历史行情
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        stock_zh_a_hist_df = ak.stock_zh_a_hist(
            symbol="000001",  # 平安银行
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )
        
        print(f"\n平安银行({start_date} - {end_date})历史行情:")
        print(stock_zh_a_hist_df.head(10))
        print(f"\n数据列: {stock_zh_a_hist_df.columns.tolist()}")
        print(f"数据行数: {len(stock_zh_a_hist_df)}")
    except Exception as e:
        print(f"获取股票历史数据失败: {e}")


def example_3_stock_info():
    """示例3: 获取股票基本信息"""
    print("\n" + "=" * 60)
    print("示例3: 获取股票基本信息")
    print("=" * 60)
    
    try:
        # 获取股票基本信息
        stock_info_a_code_name_df = ak.stock_info_a_code_name()
        print("\n股票基本信息:")
        print(stock_info_a_code_name_df.head(20))
        print(f"\n总共 {len(stock_info_a_code_name_df)} 只股票")
    except Exception as e:
        print(f"获取股票基本信息失败: {e}")


def example_4_index_data():
    """示例4: 获取指数数据"""
    print("\n" + "=" * 60)
    print("示例4: 获取指数数据")
    print("=" * 60)
    
    try:
        # 获取指数实时行情
        index_zh_a_spot_df = ak.index_zh_a_spot()
        print("\n主要指数实时行情:")
        print(index_zh_a_spot_df.head(10))
        
        # 获取上证指数历史数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        index_zh_a_hist_df = ak.index_zh_a_hist(
            symbol="sh000001",  # 上证指数
            period="daily",
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"\n上证指数({start_date} - {end_date})历史数据:")
        print(index_zh_a_hist_df.head(10))
    except Exception as e:
        print(f"获取指数数据失败: {e}")


def example_5_fund_data():
    """示例5: 获取基金数据"""
    print("\n" + "=" * 60)
    print("示例5: 获取基金数据")
    print("=" * 60)
    
    try:
        # 获取开放式基金实时行情
        fund_open_fund_daily_em_df = ak.fund_open_fund_daily_em()
        print("\n开放式基金实时行情:")
        print(fund_open_fund_daily_em_df.head(10))
        print(f"\n总共 {len(fund_open_fund_daily_em_df)} 只基金")
    except Exception as e:
        print(f"获取基金数据失败: {e}")


def example_6_futures_data():
    """示例6: 获取期货数据"""
    print("\n" + "=" * 60)
    print("示例6: 获取期货数据")
    print("=" * 60)
    
    try:
        # 获取期货实时行情
        futures_zh_spot_df = ak.futures_zh_spot()
        print("\n期货实时行情:")
        print(futures_zh_spot_df.head(10))
        print(f"\n总共 {len(futures_zh_spot_df)} 个期货品种")
    except Exception as e:
        print(f"获取期货数据失败: {e}")


def example_7_macro_data():
    """示例7: 获取宏观经济数据"""
    print("\n" + "=" * 60)
    print("示例7: 获取宏观经济数据")
    print("=" * 60)
    
    try:
        # 获取中国GDP数据
        macro_china_gdp_df = ak.macro_china_gdp()
        print("\n中国GDP数据:")
        print(macro_china_gdp_df.head(10))
        
        # 获取中国CPI数据
        macro_china_cpi_df = ak.macro_china_cpi()
        print("\n中国CPI数据:")
        print(macro_china_cpi_df.head(10))
    except Exception as e:
        print(f"获取宏观经济数据失败: {e}")


def example_8_stock_news():
    """示例8: 获取财经新闻"""
    print("\n" + "=" * 60)
    print("示例8: 获取财经新闻")
    print("=" * 60)
    
    try:
        # 获取贵州茅台财经新闻
        stock_news_em_df = ak.stock_news_em(symbol="600519")
        print("\n贵州茅台财经新闻:")
        print(stock_news_em_df.head(10))
    except Exception as e:
        print(f"获取财经新闻失败: {e}")


def example_9_data_processing():
    """示例9: 数据处理与分析"""
    print("\n" + "=" * 60)
    print("示例9: 数据处理与分析")
    print("=" * 60)
    
    try:
        # 获取股票数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(
            symbol="000001",
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        
        # 数据清洗
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
        df = df.set_index('日期')
        
        # 计算收益率
        df['收益率'] = df['收盘'].pct_change()
        
        # 计算移动平均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        
        # 计算波动率
        df['波动率'] = df['收盘'].rolling(window=20).std()
        
        print("\n处理后的数据:")
        print(df[['收盘', '收益率', 'MA5', 'MA10', 'MA20', '波动率']].head(10))
        
        # 统计信息
        print("\n统计信息:")
        print(df[['收盘', '收益率']].describe())
        
        return df
    except Exception as e:
        print(f"数据处理失败: {e}")
        return None


def example_10_visualization(df):
    """示例10: 数据可视化"""
    print("\n" + "=" * 60)
    print("示例10: 数据可视化")
    print("=" * 60)
    
    if df is None:
        print("没有数据可供可视化")
        return
    
    try:
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 价格走势图
        axes[0, 0].plot(df.index, df['收盘'], label='收盘价', linewidth=1)
        axes[0, 0].plot(df.index, df['MA5'], label='MA5', linewidth=1, alpha=0.7)
        axes[0, 0].plot(df.index, df['MA10'], label='MA10', linewidth=1, alpha=0.7)
        axes[0, 0].plot(df.index, df['MA20'], label='MA20', linewidth=1, alpha=0.7)
        axes[0, 0].set_title('平安银行股价走势')
        axes[0, 0].set_xlabel('日期')
        axes[0, 0].set_ylabel('价格')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 收益率图
        axes[0, 1].plot(df.index, df['收益率'], label='收益率', linewidth=1)
        axes[0, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[0, 1].set_title('平安银行收益率')
        axes[0, 1].set_xlabel('日期')
        axes[0, 1].set_ylabel('收益率')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 波动率图
        axes[1, 0].plot(df.index, df['波动率'], label='波动率', linewidth=1, color='orange')
        axes[1, 0].set_title('平安银行波动率')
        axes[1, 0].set_xlabel('日期')
        axes[1, 0].set_ylabel('波动率')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 成交量图
        axes[1, 1].bar(df.index, df['成交量'], label='成交量', alpha=0.6)
        axes[1, 1].set_title('平安银行成交量')
        axes[1, 1].set_xlabel('日期')
        axes[1, 1].set_ylabel('成交量')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('akshare_visualization.png', dpi=300, bbox_inches='tight')
        print("\n图表已保存为 'akshare_visualization.png'")
        plt.show()
    except Exception as e:
        print(f"数据可视化失败: {e}")


def example_11_financial_data():
    """示例11: 获取财务数据"""
    print("\n" + "=" * 60)
    print("示例11: 获取财务数据")
    print("=" * 60)
    
    try:
        # 获取个股财务指标
        stock_financial_analysis_indicator_df = ak.stock_financial_analysis_indicator(symbol="000001")
        print("\n平安银行财务指标:")
        print(stock_financial_analysis_indicator_df.head(10))
    except Exception as e:
        print(f"获取财务数据失败: {e}")


def example_12_lhb_data():
    """示例12: 获取龙虎榜数据"""
    print("\n" + "=" * 60)
    print("示例12: 获取龙虎榜数据")
    print("=" * 60)
    
    try:
        # 获取最近一个交易日的龙虎榜数据
        stock_lhb_detail_daily_df = ak.stock_lhb_detail_daily(date="20241231")
        print("\n龙虎榜数据:")
        print(stock_lhb_detail_daily_df.head(10))
    except Exception as e:
        print(f"获取龙虎榜数据失败: {e}")


def example_13_northbound_funds():
    """示例13: 获取北向资金数据"""
    print("\n" + "=" * 60)
    print("示例13: 获取北向资金数据")
    print("=" * 60)
    
    try:
        # 获取北向资金流向
        stock_hsgt_north_net_flow_in_em_df = ak.stock_hsgt_north_net_flow_in_em(symbol="北向资金")
        print("\n北向资金流向:")
        print(stock_hsgt_north_net_flow_in_em_df.head(10))
    except Exception as e:
        print(f"获取北向资金数据失败: {e}")


def example_14_batch_download():
    """示例14: 批量下载多只股票数据"""
    print("\n" + "=" * 60)
    print("示例14: 批量下载多只股票数据")
    print("=" * 60)
    
    try:
        # 定义要下载的股票列表
        stock_list = ["000001", "000002", "600000", "600519", "000858"]
        
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
        
        all_data = {}
        
        for stock_code in stock_list:
            try:
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                all_data[stock_code] = df
                print(f"成功获取股票 {stock_code} 的数据，共 {len(df)} 条记录")
            except Exception as e:
                print(f"获取股票 {stock_code} 数据失败: {e}")
        
        print(f"\n成功获取 {len(all_data)} 只股票的数据")
        
        # 合并数据
        if all_data:
            combined_df = pd.concat(all_data.values(), keys=all_data.keys())
            print("\n合并后的数据:")
            print(combined_df.head(20))
            
            # 保存到CSV
            combined_df.to_csv('batch_stock_data.csv', encoding='utf-8-sig')
            print("\n数据已保存到 'batch_stock_data.csv'")
    except Exception as e:
        print(f"批量下载失败: {e}")


def main():
    """主函数：运行所有示例"""
    print("\n" + "=" * 60)
    print("AkShare 使用示例演示")
    print("=" * 60)
    
    # 运行各个示例
    example_1_stock_realtime()
    example_2_stock_history()
    example_3_stock_info()
    example_4_index_data()
    example_5_fund_data()
    example_6_futures_data()
    example_7_macro_data()
    example_8_stock_news()
    
    # 数据处理和可视化
    df = example_9_data_processing()
    example_10_visualization(df)
    
    # 其他数据
    example_11_financial_data()
    example_12_lhb_data()
    example_13_northbound_funds()
    example_14_batch_download()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()