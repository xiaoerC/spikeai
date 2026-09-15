"""用户个人中心与资产钱包路由控制层。

提供个人资料查询、每日签到领星元、资产流水明细与邀请福利查询。

Usage:
    GET  /api/v1/user/profile
    POST /api/v1/user/daily-reward
    GET  /api/v1/user/wallet/transactions
    GET  /api/v1/user/invite-info
"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.user import (
    DailyRewardResponse,
    InviteInfoResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    WalletTransactionResponse,
)
from app.services.auth_service import AuthService
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["用户与资产 (User & Wallet)"])


@router.get(
    "/profile",
    response_model=ApiResponse[UserProfileResponse],
    summary="获取当前登录用户完整资料",
    description="返回包含 UID、经验等级、11 项成就勋章及钱包余额等与前端个人中心 100% 对齐的数据。",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserProfileResponse]:
    """获取用户个人资料。"""
    dto = AuthService.to_profile_response(current_user)
    return ApiResponse(code=0, message="success", data=dto)


@router.put(
    "/profile",
    response_model=ApiResponse[UserProfileResponse],
    summary="更新当前登录用户资料与昵称",
    description="支持设置/修改用户显示昵称 (2~20字符) 与头像，设置后将 is_custom_username 设为 True。",
)
async def update_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[UserProfileResponse]:
    """更新用户昵称或资料。"""
    updated = await AuthService.update_profile(
        db=db,
        user_id=current_user.id,
        req=payload,
    )
    return ApiResponse(code=0, message="资料更新成功", show_message=True, data=updated)



@router.post(
    "/daily-reward",
    response_model=ApiResponse[DailyRewardResponse],
    summary="每日签到领星元",
    description="每日可签到领取一次 +50 星元与 +50 玩家经验值，不可重复签到。",
)
async def claim_daily_reward(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[DailyRewardResponse]:
    """每日签到领取奖励。"""
    result = await WalletService.claim_daily_reward(db=db, user_id=current_user.id)
    return ApiResponse(code=0, message=result.message, show_message=True, data=result)


@router.get(
    "/wallet/transactions",
    response_model=ApiResponse[PaginatedResponse[WalletTransactionResponse]],
    summary="分页获取资产流水明细",
    description="按时间倒序拉取星元/月华消耗、充值、签到与打赏记录。",
)
async def get_wallet_transactions(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[PaginatedResponse[WalletTransactionResponse]]:
    """拉取资产流水记录。"""
    paginated = await WalletService.get_wallet_transactions(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(code=0, message="success", data=paginated)


@router.get(
    "/invite-info",
    response_model=ApiResponse[InviteInfoResponse],
    summary="获取我的邀请码与福利信息",
    description="返回专属邀请码、完整邀请链接及累计成功邀请人数与获得奖励。",
)
async def get_invite_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[InviteInfoResponse]:
    """查询邀请统计。"""
    # 统计成功邀请人数
    count_stmt = select(func.count(User.id)).where(User.invited_by == current_user.id)
    invited_count = (await db.execute(count_stmt)).scalar_one() or 0

    base_url = "https://naro.ai"
    invite_url = f"{base_url}/login?invite={current_user.invite_code}"

    dto = InviteInfoResponse(
        invite_code=current_user.invite_code,
        invite_url=invite_url,
        invited_count=invited_count,
        reward_earned_star=invited_count * 100,
    )
    return ApiResponse(code=0, message="success", data=dto)
