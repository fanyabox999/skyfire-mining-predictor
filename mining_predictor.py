import json
import time
from typing import Dict, List, Tuple
from enum import Enum

# 故障风险等级
class RiskLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"

class MiningEquipmentPredictor:
    """Skyfire 矿业设备预测性维护服务"""
    def __init__(self):
        # 设备正常阈值（可根据实际设备型号调整）
        self.normal_thresholds = {
            "vibration": 4.5,    # 振动加速度 (mm/s²)
            "temperature": 85,   # 轴承温度 (°C)
            "oil_pressure": 0.35 # 油压 (MPa)
        }
        # 历史故障特征库
        self.fault_patterns = {
            "bearing_wear": {"vibration": 6.0, "temperature": 90, "trend": "rising"},
            "hydraulic_leak": {"oil_pressure": 0.2, "trend": "falling"}
        }
    
    def predict_risk(self, equipment_id: str, sensor_data: Dict[str, float], history_data: List[Dict] = None) -> Dict:
        """
        预测设备故障风险
        :param equipment_id: 设备ID
        :param sensor_data: 当前传感器数据 {"vibration": 5.2, "temperature": 88, "oil_pressure": 0.38}
        :param history_data: 过去24小时历史数据（可选）
        :return: 风险分析结果
        """
        risk_score = 0
        risk_factors = []
        predicted_faults = []
        
        # 1. 单指标阈值检查
        for metric, value in sensor_data.items():
            if metric in self.normal_thresholds:
                threshold = self.normal_thresholds[metric]
                if value > threshold * 1.2:
                    risk_score += 50
                    risk_factors.append(f"{metric}严重超标（当前{value}，阈值{threshold}）")
                elif value > threshold:
                    risk_score += 20
                    risk_factors.append(f"{metric}轻微超标（当前{value}，阈值{threshold}）")
        
        # 2. 历史趋势分析（如果有历史数据）
        if history_data and len(history_data) >= 12:
            trend = self._analyze_trend(history_data)
            if trend == "rising":
                risk_score += 25
                risk_factors.append("指标呈上升趋势")
            elif trend == "falling":
                risk_score += 25
                risk_factors.append("指标呈下降趋势")
        
        # 3. 故障模式匹配
        for fault_name, pattern in self.fault_patterns.items():
            match = True
            for metric, threshold in pattern.items():
                if metric == "trend":
                    continue
                if metric in sensor_data and sensor_data[metric] < threshold:
                    match = False
                    break
            if match:
                predicted_faults.append(fault_name)
                risk_score += 30
        
        # 4. 确定风险等级
        if risk_score >= 70:
            level = RiskLevel.DANGER
            suggestion = "立即停机检查，重点排查：" + "、".join(predicted_faults)
        elif risk_score >= 30:
            level = RiskLevel.WARNING
            suggestion = "计划内维护，关注：" + "、".join(risk_factors)
        else:
            level = RiskLevel.SAFE
            suggestion = "设备运行正常"
        
        return {
            "equipment_id": equipment_id,
            "risk_level": level.value,
            "risk_score": min(risk_score, 100),
            "risk_factors": risk_factors,
            "predicted_faults": predicted_faults,
            "suggestion": suggestion,
            "timestamp": time.time()
        }
    
    def _analyze_trend(self, history_data: List[Dict]) -> str:
        """简单趋势分析：上升/下降/稳定"""
        if len(history_data) < 2:
            return "stable"
        first_avg = sum(d["vibration"] for d in history_data[:6]) / 6
        last_avg = sum(d["vibration"] for d in history_data[-6:]) / 6
        if last_avg > first_avg * 1.1:
            return "rising"
        elif last_avg < first_avg * 0.9:
            return "falling"
        return "stable"

# -------------- 快速使用示例 --------------
if __name__ == "__main__":
    predictor = MiningEquipmentPredictor()
    
    # 模拟传感器数据（挖掘机）
    sensor_data = {
        "vibration": 5.8,
        "temperature": 92,
        "oil_pressure": 0.36
    }
    
    # 模拟历史数据（过去24小时，每2小时一条）
    history_data = [
        {"vibration": 4.2 + i*0.15, "temperature": 80 + i*0.8}
        for i in range(12)
    ]
    
    # 预测风险
    result = predictor.predict_risk("excavator_001", sensor_data, history_data)
    print("风险分析结果：", json.dumps(result, indent=2, ensure_ascii=False))
