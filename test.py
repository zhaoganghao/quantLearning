#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首助广告位报表接口请求脚本
"""

import hashlib
import time
import urllib.parse
import requests
from typing import Dict, Optional


class ShouzhuAdspaceReportClient:
    """首助广告位报表接口客户端"""

    def __init__(self, app_id: str, secret: str, host: str = "https://mvapi.qihoo.net"):
        """
        初始化客户端

        Args:
            app_id: 应用ID，需要找开发同学申请
            secret: 密钥，需要找开发同学申请
            host: 接口地址，默认测试环境
        """
        self.app_id = app_id
        self.secret = secret
        self.host = host.rstrip('/')

    def _generate_sign(self, params: Dict[str, str]) -> str:
        """
        生成签名

        Args:
            params: 请求参数字典

        Returns:
            签名字符串
        """
        # 按照ASCII码排序
        sorted_params = sorted(params.items())

        # 拼接参数字符串，value需要urlencode
        params_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted_params])

        # 计算MD5签名
        sign_str = params_str + self.secret
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        return sign

    def get_report(
            self,
            start_date: str,
            end_date: str,
            advertiser_ids: Optional[str] = None
    ) -> Dict:
        """
        获取广告位报表

        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            advertiser_ids: 广告主ID列表，逗号分隔，为空则不过滤

        Returns:
            接口返回数据
        """
        # 构建请求参数
        params = {
            'appId': self.app_id,
            'timestamp': str(int(time.time())),
            'startDate': start_date,
            'endDate': end_date,
        }

        # 可选参数
        if advertiser_ids:
            params['advertiserIds'] = advertiser_ids

        # 生成签名
        sign = self._generate_sign(params)
        params['sign'] = sign

        # 构建请求URL
        url = f"{self.host}/mv/ssp/report/shouzhuAdspace"

        # 发送请求
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            print(response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'code': 500,
                'msg': f'请求失败: {str(e)}',
                'data': None
            }


def main():
    """主函数示例"""

    # 配置信息（需要找开发同学申请）
    APP_ID = "shouzhu"  # 替换为实际的appId
    SECRET = "ffvg5mC0j4820934234hi2u4i24320-0-83"  # 替换为实际的secret

    # 创建客户端实例
    client = ShouzhuAdspaceReportClient(
        app_id=APP_ID,
        secret=SECRET,
        host="http://mvapi.qihoo.net"  # 测试环境
        # host="https://mvapi.qihoo.net"  # 线上环境
    )

    # 请求参数
    start_date = "2026-1-11"
    end_date = "2026-1-11"
    advertiser_ids = "1,2,3"  # 可选，为空则不过滤

    # 发送请求
    print(f"正在请求广告位报表数据...")
    print(f"时间范围: {start_date} ~ {end_date}")
    print(f"广告主ID: {advertiser_ids if advertiser_ids else '不过滤'}")
    print("-" * 50)

    result = client.get_report(
        start_date=start_date,
        end_date=end_date,
        advertiser_ids=advertiser_ids
    )

    # 打印结果
    print(f"响应码: {result.get('code')}")
    print(f"响应消息: {result.get('msg')}")
    print(f"数据条数: {len(result.get('data', []))}")
    print("-" * 50)

    # 打印详细数据
    if result.get('code') == 200 and result.get('data'):
        print("报表数据:")
        print(
            f"{'日期':<12} {'应用ID':<10} {'应用名称':<20} {'广告位ID':<10} {'广告位名称':<15} {'广告主ID':<12} {'展示数':<10} {'点击数':<10} {'收入':<10}")
        print("-" * 120)

        for item in result['data']:
            print(f"{item.get('date', ''):<12} "
                  f"{item.get('publisherId', ''):<10} "
                  f"{item.get('publisherName', ''):<20} "
                  f"{item.get('adspaceId', ''):<10} "
                  f"{item.get('adspaceName', ''):<15} "
                  f"{item.get('advertiserId', ''):<12} "
                  f"{item.get('ns', 0):<10} "
                  f"{item.get('nc', 0):<10} "
                  f"{item.get('income', 0):<10.2f}")
    else:
        print("请求失败或无数据")


if __name__ == "__main__":
    main()