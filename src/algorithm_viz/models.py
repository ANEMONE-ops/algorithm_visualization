"""
算法可视化系统 - 数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 关系
    test_cases = relationship(
        "UserTestCase", back_populates="user", cascade="all, delete-orphan"
    )
    execution_logs = relationship(
        "ExecutionLog", back_populates="user", cascade="all, delete-orphan"
    )


class UserTestCase(Base):
    """用户自定义测试数据"""

    __tablename__ = "user_test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    algorithm_type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    input_data = Column(Text, nullable=False)  # JSON 格式
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_cases")


class ExecutionLog(Base):
    """算法执行日志"""

    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    algorithm_type = Column(String(50), nullable=False)
    input_data = Column(Text, nullable=False)
    is_test_case = Column(Integer, default=0)  # 0=自定义, 1=预设测试用例
    test_case_index = Column(Integer, nullable=True)
    total_steps = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="execution_logs")
