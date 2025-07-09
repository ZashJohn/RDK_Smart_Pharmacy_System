from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Any


from pathlib import Path
from typing import List, Dict, Any
from ultralytics import YOLO

def predict_to_json(
        model_path: str,
        source: str,
) -> List[Dict[str, Any]]:
    """
    使用YOLO模型进行预测，并返回包含检测结果的JSON格式数据

    参数:
        model_path: 训练好的模型路径
        source: 要预测的图像或目录路径

    返回:
        包含所有预测结果的JSON格式数据列表，按图片顺序标记方向索引（从0开始）
        格式: [
            {
                "direction": 0,
                "detections": [
                    {"class_name": "person", "center_x": 100.5, "center_y": 200.3},
                    ...
                ]
            },
            ...
        ]
    """
    # 加载模型
    model = YOLO(model_path)

    # 进行预测（不保存图像和结果）
    results = model.predict(source=source, save=True, save_txt=False)

    # 准备JSON数据
    json_data = []

    for idx, result in enumerate(results):  # 使用enumerate获取方向索引
        boxes = result.boxes

        # 当前图像的检测结果
        image_detections = {
            "direction": idx,  # 替换为从0开始的整数索引
            "detections": []
        }

        for box in boxes:
            # 获取中心点坐标（xywh格式中的cx, cy）
            cx, cy, _, _ = box.xywh[0].tolist()

            # 获取类别名称
            cls_id = box.cls.item()
            cls_name = model.names[int(cls_id)]

            detection = {
                "class_name": cls_name,
                "center_x": round(cx, 2),
                "center_y": round(cy, 2)
            }

            image_detections["detections"].append(detection)

        json_data.append(image_detections)

    return json_data

if __name__ == '__main__':
    model_path = "asset/models/best.pt"  # 替换为你的模型路径
    image_path = "asset/testimgs"  # 替换为你的图片路径

    # 调用函数
    results = predict_to_json(model_path, image_path)

    # 打印结果
    print(results)