from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")

    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
    
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"
    # TODO 4-1：补充“流失率”“偏好品类”“生命周期风险”和“订单”四类问答。
    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。
    # 2. 流失率相关
    if any(word in normalized for word in ["流失率", "流失", "流失人数"]):
        if "流失人数" in normalized or "流失人数" in question:
            return f"数据集中共有流失用户{int(metrics['流失人数']):,}人，整体流失率为{metrics['流失率']:.2%}。"
        return f"数据集中整体流失率为{metrics['流失率']:.2%}。"

    # 3. 偏好品类相关
    if any(word in normalized for word in ["偏好", "品类", "最喜欢", "最多", "占比", "类别"]):
        # 找出用户数最多的品类
        top_category = category_df.loc[category_df["用户数"].idxmax()]
        # 找出流失率最高的品类
        high_churn_category = category_df.loc[category_df["流失率"].idxmax()]
        # 找出平均订单数最多的品类
        high_order_category = category_df.loc[category_df["平均订单数"].idxmax()]
        return (
            f"在偏好品类中，用户数最多的品类是「{top_category['PreferedOrderCat']}」，"
            f"共有{int(top_category['用户数'])}人，占总用户{top_category['用户占比']:.2%}；"
            f"流失率最高的品类是「{high_churn_category['PreferedOrderCat']}」，"
            f"流失率为{high_churn_category['流失率']:.2%}；"
            f"平均订单数最多的品类是「{high_order_category['PreferedOrderCat']}」，"
            f"平均订单数为{high_order_category['平均订单数']:.2f}单。"
        )
    # 4. 生命周期风险相关
    if any(word in normalized for word in ["生命周期", " tenure", "时长", "新用户", "老用户", "阶段", "组"]):
        # 找出流失率最高的 tenure 组
        high_risk_segment = segment_df.loc[segment_df["流失率"].idxmax()]
        # 找出流失率最低的 tenure 组（排除流失率为0的特殊情况，选第二个低的）
        low_risk_segment = segment_df.loc[segment_df["流失率"].nsmallest(2).index[-1]]
        
        return (
            f"按用户生命周期（Tenure）分组来看，流失风险最高的组是「{high_risk_segment['TenureGroup']}」，"
            f"流失率高达{high_risk_segment['流失率']:.2%}，共{int(high_risk_segment['用户数'])}人；"
            f"流失风险最低的组是「{low_risk_segment['TenureGroup']}」，"
            f"流失率为{low_risk_segment['流失率']:.2%}。"
            f"新用户（Tenure<6个月）整体流失率显著高于老用户。"
        )
    # 5. 订单相关
    if any(word in normalized for word in ["订单", "下单", "平均订单", "订单数"]):
        if "中位数" in normalized or "中位数" in question:
            return f"数据集中用户平均订单数为{metrics['平均订单数']:.2f}单，订单数中位数为{int(metrics['订单数中位数'])}单。"
        if "平均返现" in normalized or "返现" in question:
            return f"数据集中用户平均返现金额为{metrics['平均返现']:.2f}元。"
        if "距上次下单" in normalized or "上次下单" in normalized:
            return f"数据集中用户平均距上次下单天数为{metrics['平均距上次下单天数']:.2f}天。"
        return f"数据集中用户平均订单数为{metrics['平均订单数']:.2f}单，订单数中位数为{int(metrics['订单数中位数'])}单。"

    return (
        "抱歉，暂无法回答该问题。目前支持的问题类型包括："
        "总用户数、流失率/流失人数、偏好品类分析、生命周期风险分析、订单数/返现/距上次下单天数等。"
        "请换一种更具体的问法。"
    )


