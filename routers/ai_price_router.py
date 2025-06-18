"""
AI Price Analysis Router
Provides endpoints for AI-powered price analysis and predictions
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging

from models import (
    PriceTrendAnalysisRequest, PriceTrendAnalysisResponse,
    PricePredictionRequest, PricePredictionResponse,
    GroceryOptimizationRequest, GroceryOptimizationResponse,
    SeasonalAnalysisRequest, SeasonalAnalysisResponse,
    MarketInsightsRequest, MarketInsightsResponse,
    TokenPayload
)
from auth_utils import get_optional_current_user
from services.ai_price_analysis_service import ai_price_analysis_service

# Setup logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai-price", tags=["AI Price Analysis"])


@router.post("/analyze-trends", response_model=PriceTrendAnalysisResponse)
async def analyze_price_trends(
    request: PriceTrendAnalysisRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Phân tích xu hướng giá cả thực phẩm bằng AI
    
    Args:
        request: Yêu cầu phân tích xu hướng
        user: Thông tin người dùng (optional)
        
    Returns:
        PriceTrendAnalysisResponse: Kết quả phân tích xu hướng
    """
    try:
        logger.info(f"Analyzing price trends for category: {request.category}, days_back: {request.days_back}")
        
        # Gọi AI service để phân tích
        analysis = await ai_price_analysis_service.analyze_price_trends(
            category=request.category,
            days_back=request.days_back
        )
        
        # Convert to response model
        response = PriceTrendAnalysisResponse(**analysis)
        
        logger.info(f"Price trend analysis completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing price trends: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi phân tích xu hướng giá: {str(e)}"
        )


@router.post("/predict-price", response_model=PricePredictionResponse)
async def predict_food_price(
    request: PricePredictionRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Dự đoán giá cả thực phẩm trong tương lai bằng AI
    
    Args:
        request: Yêu cầu dự đoán giá
        user: Thông tin người dùng (optional)
        
    Returns:
        PricePredictionResponse: Kết quả dự đoán giá
    """
    try:
        logger.info(f"Predicting price for food: {request.food_name}, days_ahead: {request.days_ahead}")
        
        # Gọi AI service để dự đoán
        prediction = await ai_price_analysis_service.predict_future_prices(
            food_name=request.food_name,
            days_ahead=request.days_ahead
        )
        
        # Convert to response model
        response = PricePredictionResponse(**prediction)
        
        logger.info(f"Price prediction completed successfully for {request.food_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error predicting price for {request.food_name}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi dự đoán giá cho {request.food_name}: {str(e)}"
        )


@router.post("/analyze-seasonal", response_model=SeasonalAnalysisResponse)
async def analyze_seasonal_trends(
    request: SeasonalAnalysisRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Phân tích xu hướng mùa vụ thực phẩm bằng AI
    
    Args:
        request: Yêu cầu phân tích mùa vụ
        user: Thông tin người dùng (optional)
        
    Returns:
        SeasonalAnalysisResponse: Kết quả phân tích mùa vụ
    """
    try:
        logger.info(f"Analyzing seasonal trends for category: {request.category}, month: {request.current_month}")
        
        # Gọi AI service để phân tích
        analysis = await ai_price_analysis_service.analyze_seasonal_trends(
            category=request.category,
            current_month=request.current_month
        )
        
        # Convert to response model
        response = SeasonalAnalysisResponse(**analysis)
        
        logger.info(f"Seasonal analysis completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing seasonal trends: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi phân tích mùa vụ: {str(e)}"
        )


@router.post("/optimize-grocery", response_model=GroceryOptimizationResponse)
async def optimize_grocery_list(
    request: GroceryOptimizationRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Tối ưu hóa danh sách grocery bằng AI
    
    Args:
        request: Yêu cầu tối ưu hóa grocery
        user: Thông tin người dùng (optional)
        
    Returns:
        GroceryOptimizationResponse: Kết quả tối ưu hóa
    """
    try:
        logger.info(f"Optimizing grocery list with {len(request.grocery_items)} items")
        
        # Gọi AI service để tối ưu hóa
        optimization = await ai_price_analysis_service.optimize_grocery_list(
            grocery_items=request.grocery_items,
            budget_limit=request.budget_limit
        )
        
        # Convert to response model
        response = GroceryOptimizationResponse(**optimization)
        
        logger.info(f"Grocery optimization completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing grocery list: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi tối ưu hóa danh sách grocery: {str(e)}"
        )


@router.post("/market-insights", response_model=MarketInsightsResponse)
async def generate_market_insights(
    request: MarketInsightsRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Tạo insights thông minh về thị trường thực phẩm bằng AI
    
    Args:
        request: Yêu cầu market insights
        user: Thông tin người dùng (optional)
        
    Returns:
        MarketInsightsResponse: Kết quả market insights
    """
    try:
        logger.info(f"Generating market insights for region: {request.region}")
        
        # Gọi AI service để tạo insights
        insights = await ai_price_analysis_service.generate_market_insights(
            region=request.region,
            include_trends=request.include_trends
        )
        
        # Convert to response model
        response = MarketInsightsResponse(**insights)
        
        logger.info(f"Market insights generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error generating market insights: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi tạo market insights: {str(e)}"
        )


# GET endpoints for convenience
@router.get("/analyze-trends", response_model=PriceTrendAnalysisResponse)
async def analyze_price_trends_get(
    category: Optional[str] = Query(None, description="Danh mục thực phẩm"),
    days_back: int = Query(30, description="Số ngày quay lại", ge=1, le=365),
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Phân tích xu hướng giá cả (GET method)
    """
    request = PriceTrendAnalysisRequest(category=category, days_back=days_back)
    return await analyze_price_trends(request, user)


@router.get("/predict-price", response_model=PricePredictionResponse)
async def predict_food_price_get(
    food_name: str = Query(..., description="Tên thực phẩm"),
    days_ahead: int = Query(7, description="Số ngày dự đoán", ge=1, le=30),
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Dự đoán giá cả thực phẩm (GET method)
    """
    request = PricePredictionRequest(food_name=food_name, days_ahead=days_ahead)
    return await predict_food_price(request, user)


@router.get("/analyze-seasonal", response_model=SeasonalAnalysisResponse)
async def analyze_seasonal_trends_get(
    category: Optional[str] = Query(None, description="Danh mục thực phẩm"),
    current_month: Optional[int] = Query(None, description="Tháng hiện tại", ge=1, le=12),
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Phân tích xu hướng mùa vụ (GET method)
    """
    request = SeasonalAnalysisRequest(category=category, current_month=current_month)
    return await analyze_seasonal_trends(request, user)


@router.get("/market-insights", response_model=MarketInsightsResponse)
async def generate_market_insights_get(
    region: Optional[str] = Query(None, description="Khu vực địa lý"),
    include_trends: bool = Query(True, description="Bao gồm phân tích xu hướng"),
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """
    Tạo market insights (GET method)
    """
    request = MarketInsightsRequest(region=region, include_trends=include_trends)
    return await generate_market_insights(request, user)


@router.get("/health")
async def health_check():
    """
    Health check endpoint cho AI Price Analysis service
    """
    try:
        # Test basic functionality
        test_analysis = await ai_price_analysis_service.analyze_price_trends(
            category="test", 
            days_back=1
        )
        
        return {
            "status": "healthy",
            "service": "AI Price Analysis",
            "ai_service_available": bool(ai_price_analysis_service.groq_service),
            "timestamp": test_analysis.get("analysis_date", "unknown")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "AI Price Analysis",
            "error": str(e),
            "ai_service_available": False
        }
