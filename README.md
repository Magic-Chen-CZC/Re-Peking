# Re-Peking | 北京导览 AI
<img width="350" height="721" alt="截屏2026-01-08 00 25 33" src="https://github.com/user-attachments/assets/938f529f-ee07-4500-86b5-f2a3ca995c20" />
<img width="350" height="721" alt="截屏2026-01-08 00 26 03" src="https://github.com/user-attachments/assets/306265cb-856d-4613-bad7-abf0ccf86e24" />
<img width="350" height="721" alt="截屏2026-01-08 00 26 47" src="https://github.com/user-attachments/assets/01e9aa32-554f-4d6c-aa7a-fd3f6ce67d6b" />
<img width="350" height="721" alt="截屏2026-01-08 00 26 58" src="https://github.com/user-attachments/assets/f36062a8-f84c-43bf-a259-0764d0427d5e" />

## 项目概述 | Overview
中文：Re-Peking 是一套“北京导览 AI”系统，面向旅行规划与内容讲解，整合多智能体后端、微信小程序前端与数据采集/审核/向量检索流水线，提供从兴趣偏好到路线与讲解的一体化体验。

English: Re-Peking is an AI Beijing tour guide system that combines a multi-agent backend, a WeChat Mini Program frontend, and a data pipeline for collection/review/vector search to deliver end-to-end trip planning and storytelling.

## 核心功能 | Key Features
中文：
- 主题与偏好驱动的路线规划（时间预算、交通方式、节奏偏好等）
- 多智能体协作生成导览讲解与行程建议
- RAG 支撑的事实性讲解，结合本地知识库
- 数据采集、人工审核、向量入库与检索的完整链路

English:
- Preference-aware itinerary planning (time budget, transport, pace)
- Multi-agent collaboration for route design and narration
- RAG-backed factual storytelling from a local knowledge base
- End-to-end data collection, review, vectorization, and retrieval

## 系统组成 | System Components
中文：
- 后端（`bakend/`）：FastAPI + LangGraph 多智能体服务，提供 `POST /api/plan` 规划与讲解接口。
- 小程序（`miniprogram/`）：面向用户的微信小程序前端，包含路线规划、地图与社区页面。
- 数据管道（`BeijingGuideData/`）：采集小红书/文档等数据，人工审核后入库并提供检索能力。

English:
- Backend (`bakend/`): FastAPI + LangGraph multi-agent service exposing `POST /api/plan`.
- Mini Program (`miniprogram/`): WeChat Mini Program UI for planning, maps, and community content.
- Data Pipeline (`BeijingGuideData/`): Data collection, human review, vector indexing, and search.

## 体验方式 | How It’s Used
中文：
- 产品侧：用户在小程序选择兴趣、时间与出行偏好，系统生成路线与讲解。
- 运营侧：通过数据管道持续补充与审核内容，提高讲解质量与覆盖度。

English:
- Product: users select interests, time, and travel preferences in the Mini Program to receive routes and narration.
- Operations: enrich the knowledge base via the data pipeline to improve coverage and quality.

## 技术与数据简述 | Tech & Data Notes
中文：
- 后端使用 FastAPI、LangGraph，结合 Qwen/DashScope 能力。
- 检索侧使用 ChromaDB + LlamaIndex 构建向量知识库。

English:
- Backend uses FastAPI and LangGraph with Qwen/DashScope models.
- Retrieval uses ChromaDB + LlamaIndex for the vector knowledge base.

## 目录指引 | Repository Map
- `bakend/`：后端服务与多智能体编排
- `miniprogram/`：微信小程序前端
- `BeijingGuideData/`：数据采集与检索流水线

