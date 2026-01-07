# Attractions 图片目录

## 图片命名规则

图片文件名应与 POI ID 一致，格式为：`{poi_id}.png`

例如：
- `xishiku.png` - 西什库教堂
- `gugong.png` - 故宫
- `shejitan.png` - 社稷坛
- `baiyunguan.png` - 白云观
- `default.png` - 默认占位图（必需）

## 默认图片

**必须提供 `default.png`** 作为占位图，当找不到对应 POI ID 的图片时会自动使用。

建议规格：
- 尺寸：800x600 或更高
- 格式：PNG（支持透明）或 JPG
- 大小：< 500KB

## 添加新景点图片

1. 获取 POI ID（从后端 API 返回的 `poi_id` 字段）
2. 准备图片，命名为 `{poi_id}.png`
3. 放入此目录
4. 小程序会自动加载对应图片

## 现有图片列表

- `xishiku.png` ✅
- `gugong.png` ✅
- `shejitan.png` ✅
- `baiyunguan.png` ✅
- `default.png` ⚠️ **需要添加**
