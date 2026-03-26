"""
WebSocket 路由 - 实时进度推送
"""
import asyncio
import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # task_id -> list of websocket connections
        self.active_connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """接受新连接"""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket connected for task: {task_id}")

    def disconnect(self, websocket: WebSocket, task_id: str):
        """断开连接"""
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
        logger.info(f"WebSocket disconnected for task: {task_id}")

    async def send_progress(self, task_id: str, data: dict):
        """发送进度消息"""
        if task_id in self.active_connections:
            message = json.dumps(data, ensure_ascii=False)
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket 端点

    消息格式:
    {
        "status": "fetching|analyzing|generating|writing|completed|failed",
        "progress": 0-100,
        "message": "当前操作描述",
        "current_step": "步骤详情"
    }
    """
    await manager.connect(websocket, task_id)

    try:
        while True:
            # 等待客户端消息（可用于心跳或控制）
            data = await websocket.receive_text()

            # 处理心跳 - 返回 JSON 格式
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, task_id)


async def broadcast_progress(
    task_id: str,
    status: str,
    progress: int,
    message: str = "",
    current_step: str = "",
    **extra
):
    """
    广播进度消息

    Args:
        task_id: 任务 ID
        status: 状态
        progress: 进度 (0-100)
        message: 消息
        current_step: 当前步骤
        **extra: 额外数据
    """
    data = {
        "status": status,
        "progress": progress,
        "message": message,
        "current_step": current_step,
        **extra
    }
    await manager.send_progress(task_id, data)
