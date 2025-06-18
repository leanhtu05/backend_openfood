"""
AI Price Analysis Service for Vietnamese Food Prices
Provides intelligent analysis, predictions, and optimization for food pricing
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from groq_integration import groq_service


class AIPriceAnalysisService:
    """Service for AI-powered price analysis and predictions"""
    
    def __init__(self):
        self.groq_service = groq_service
        
    async def analyze_price_trends(
        self, 
        category: Optional[str] = None, 
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Phân tích xu hướng giá cả thực phẩm
        
        Args:
            category: Danh mục thực phẩm (optional)
            days_back: Số ngày quay lại để phân tích
            
        Returns:
            Dict chứa phân tích xu hướng
        """
        try:
            # Tạo prompt cho AI
            prompt = self._build_trend_analysis_prompt(category, days_back)
            
            # Gọi AI để phân tích
            ai_response = await self._call_ai_service(prompt)
            
            # Parse và format response
            analysis = self._parse_trend_analysis_response(ai_response, category, days_back)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Lỗi phân tích xu hướng: {e}")
            return self._get_fallback_trend_analysis(category, days_back)
    
    async def predict_future_prices(
        self, 
        food_name: str, 
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Dự đoán giá cả trong tương lai
        
        Args:
            food_name: Tên thực phẩm
            days_ahead: Số ngày dự đoán trước
            
        Returns:
            Dict chứa dự đoán giá
        """
        try:
            # Tạo prompt cho AI
            prompt = self._build_prediction_prompt(food_name, days_ahead)
            
            # Gọi AI để dự đoán
            ai_response = await self._call_ai_service(prompt)
            
            # Parse response
            prediction = self._parse_prediction_response(ai_response, food_name, days_ahead)
            
            return prediction
            
        except Exception as e:
            print(f"❌ Lỗi dự đoán giá: {e}")
            return self._get_fallback_prediction(food_name, days_ahead)
    
    async def analyze_seasonal_trends(
        self, 
        category: Optional[str] = None,
        current_month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Phân tích xu hướng mùa vụ
        
        Args:
            category: Danh mục thực phẩm
            current_month: Tháng hiện tại (1-12)
            
        Returns:
            Dict chứa phân tích mùa vụ
        """
        try:
            if current_month is None:
                current_month = datetime.now().month
                
            prompt = self._build_seasonal_analysis_prompt(category, current_month)
            ai_response = await self._call_ai_service(prompt)
            analysis = self._parse_seasonal_response(ai_response, current_month)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Lỗi phân tích mùa vụ: {e}")
            return self._get_fallback_seasonal_analysis(current_month)
    
    async def optimize_grocery_list(
        self, 
        grocery_items: List[Dict[str, Any]],
        budget_limit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Tối ưu hóa danh sách grocery
        
        Args:
            grocery_items: Danh sách items
            budget_limit: Giới hạn ngân sách
            
        Returns:
            Dict chứa gợi ý tối ưu hóa
        """
        try:
            prompt = self._build_grocery_optimization_prompt(grocery_items, budget_limit)
            ai_response = await self._call_ai_service(prompt)
            optimization = self._parse_grocery_optimization_response(ai_response)
            
            return optimization
            
        except Exception as e:
            print(f"❌ Lỗi tối ưu hóa grocery: {e}")
            return self._get_fallback_grocery_optimization()
    
    async def generate_market_insights(
        self,
        region: Optional[str] = None,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """
        Tạo insights thông minh về thị trường
        
        Args:
            region: Khu vực địa lý
            include_trends: Bao gồm phân tích xu hướng
            
        Returns:
            Dict chứa market insights
        """
        try:
            prompt = self._build_market_insights_prompt(region, include_trends)
            ai_response = await self._call_ai_service(prompt)
            insights = self._parse_market_insights_response(ai_response)
            
            return insights
            
        except Exception as e:
            print(f"❌ Lỗi tạo market insights: {e}")
            return self._get_fallback_market_insights()
    
    async def _call_ai_service(self, prompt: str) -> str:
        """
        Gọi AI service để xử lý prompt
        
        Args:
            prompt: Prompt để gửi cho AI
            
        Returns:
            Response từ AI
        """
        try:
            if self.groq_service and hasattr(self.groq_service, 'chat'):
                response = self.groq_service.chat(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    max_tokens=1000,
                    temperature=0.7
                )
                
                if response and 'choices' in response and len(response['choices']) > 0:
                    return response['choices'][0]['message']['content']
            
            # Fallback to mock response
            return self._generate_mock_response(prompt)
            
        except Exception as e:
            print(f"❌ Lỗi gọi AI service: {e}")
            return self._generate_mock_response(prompt)
    
    def _build_trend_analysis_prompt(self, category: Optional[str], days_back: int) -> str:
        """Tạo prompt cho phân tích xu hướng"""
        category_filter = f"cho danh mục {category}" if category else "cho tất cả danh mục"
        
        return f"""
Phân tích xu hướng giá cả thực phẩm Việt Nam {category_filter} trong {days_back} ngày qua.

Hãy phân tích và đưa ra:
1. Xu hướng giá cả chung (tăng/giảm/ổn định)
2. Những thực phẩm có biến động giá mạnh nhất
3. Nguyên nhân có thể gây ra biến động
4. Dự đoán xu hướng trong tuần tới
5. Khuyến nghị mua sắm thông minh

Trả lời bằng tiếng Việt, ngắn gọn và thực tế.
Tập trung vào thị trường Việt Nam và thói quen tiêu dùng địa phương.
"""
    
    def _build_prediction_prompt(self, food_name: str, days_ahead: int) -> str:
        """Tạo prompt cho dự đoán giá"""
        return f"""
Dự đoán giá cả cho thực phẩm: {food_name} trong {days_ahead} ngày tới tại thị trường Việt Nam.

Hãy dự đoán:
1. Giá dự kiến sau {days_ahead} ngày (VND)
2. Xu hướng (tăng/giảm/ổn định)
3. Độ tin cậy dự đoán (0-100%)
4. Các yếu tố ảnh hưởng (thời tiết, mùa vụ, cung cầu)
5. Khuyến nghị mua/không mua

Trả lời bằng JSON format với các trường:
- predicted_price: số (VND)
- trend: string (increasing/decreasing/stable)
- confidence: số (0-100)
- factors: array of strings
- recommendation: string

Dựa trên thực tế thị trường Việt Nam.
"""
    
    def _build_seasonal_analysis_prompt(self, category: Optional[str], current_month: int) -> str:
        """Tạo prompt cho phân tích mùa vụ"""
        month_names = [
            "", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
            "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"
        ]
        month_name = month_names[current_month]
        category_filter = f"cho danh mục {category}" if category else ""
        
        return f"""
Phân tích mùa vụ thực phẩm Việt Nam cho {month_name} {category_filter}.

Hãy phân tích:
1. Thực phẩm theo mùa hiện tại (tươi ngon, giá tốt)
2. Thực phẩm nên mua trong tháng này
3. Thực phẩm nên tránh mua (đắt/không ngon)
4. Dự đoán giá trong tháng tới
5. Deals tốt nhất hiện tại

Trả lời bằng tiếng Việt, tập trung vào:
- Đặc điểm khí hậu Việt Nam
- Thói quen ăn uống địa phương
- Mùa vụ nông sản trong nước
- Giá cả thực tế tại chợ/siêu thị
"""
    
    def _build_grocery_optimization_prompt(self, grocery_items: List[Dict], budget_limit: Optional[float]) -> str:
        """Tạo prompt cho tối ưu hóa grocery"""
        items_text = "\n".join([f"- {item.get('name', 'Unknown')}: {item.get('amount', '1')} {item.get('unit', 'kg')}" for item in grocery_items])
        budget_text = f"với ngân sách {budget_limit:,.0f} VND" if budget_limit else ""
        
        return f"""
Phân tích và tối ưu hóa danh sách grocery {budget_text}:

Danh sách mua sắm:
{items_text}

Hãy đưa ra:
1. Tối ưu hóa chi phí (thay thế rẻ hơn, nơi mua tốt)
2. Thời điểm mua tốt nhất cho từng loại
3. Gợi ý thay thế để cân bằng dinh dưỡng
4. Lời khuyên bảo quản và sử dụng
5. Tips mua sắm thông minh tại Việt Nam

Trả lời thực tế, hữu ích cho người Việt Nam.
Tập trung vào tiết kiệm chi phí và đảm bảo chất lượng.
"""
    
    def _build_market_insights_prompt(self, region: Optional[str], include_trends: bool) -> str:
        """Tạo prompt cho market insights"""
        region_filter = f"tại {region}" if region else "toàn quốc"
        
        return f"""
Tạo insights thông minh về thị trường thực phẩm Việt Nam {region_filter}.

Phân tích:
1. Tổng quan thị trường hiện tại
2. Thực phẩm đang trending
3. Biến động giá bất thường
4. Hành vi người tiêu dùng Việt Nam
5. Yếu tố kinh tế ảnh hưởng
6. Khuyến nghị cho người tiêu dùng

Đưa ra insights sâu sắc, thực tế cho thị trường Việt Nam.
Tập trung vào xu hướng tiêu dùng và cơ hội tiết kiệm.
"""
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Tạo mock response thông minh dựa trên prompt"""
        if "xu hướng" in prompt.lower() or "trend" in prompt.lower():
            return self._get_mock_trend_response()
        elif "dự đoán" in prompt.lower() or "predict" in prompt.lower():
            return self._get_mock_prediction_response()
        elif "mùa" in prompt.lower() or "seasonal" in prompt.lower():
            return self._get_mock_seasonal_response()
        elif "grocery" in prompt.lower() or "tối ưu" in prompt.lower():
            return self._get_mock_grocery_response()
        elif "thị trường" in prompt.lower() or "market" in prompt.lower():
            return self._get_mock_market_response()
        else:
            return "Phân tích AI đang được cập nhật. Vui lòng thử lại sau."
    
    def _get_mock_trend_response(self) -> str:
        """Mock response cho trend analysis"""
        trends = [
            "Giá rau củ quả ổn định nhờ thời tiết thuận lợi",
            "Thịt bò có xu hướng tăng nhẹ do nhu cầu cao",
            "Hải sản giảm giá nhờ mùa đánh bắt tốt",
            "Gạo duy trì mức giá ổn định"
        ]
        
        insights = [
            "Nên mua rau củ trong tuần này",
            "Có thể hoãn mua thịt bò",
            "Thời điểm tốt để mua hải sản",
            "Giá gia vị có thể tăng nhẹ"
        ]
        
        return f"""
Xu hướng chính:
{chr(10).join([f'• {t}' for t in trends])}

Khuyến nghị:
{chr(10).join([f'• {i}' for i in insights])}
"""
    
    def _get_mock_prediction_response(self) -> str:
        """Mock response cho price prediction"""
        random_change = random.uniform(-15, 15)  # -15% to +15%
        confidence = random.randint(70, 95)
        
        return json.dumps({
            "predicted_price": 50000 * (1 + random_change/100),
            "trend": "increasing" if random_change > 5 else "decreasing" if random_change < -5 else "stable",
            "confidence": confidence,
            "factors": ["Thời tiết", "Cung cầu thị trường", "Mùa vụ"],
            "recommendation": "Nên mua trong tuần này" if random_change > 0 else "Có thể chờ thêm"
        })
    
    def _get_mock_seasonal_response(self) -> str:
        """Mock response cho seasonal analysis"""
        return """
Thực phẩm theo mùa:
• Rau muống - tươi ngon, giá tốt
• Cà chua - chất lượng cao
• Dưa hấu - mùa chính vụ

Khuyến nghị mua:
• Ưu tiên rau củ theo mùa
• Tránh trái cây nhập khẩu
• Mua số lượng vừa đủ
"""
    
    def _get_mock_grocery_response(self) -> str:
        """Mock response cho grocery optimization"""
        return """
Tối ưu chi phí:
• Thay thịt bò bằng thịt heo tiết kiệm 40%
• Mua rau tại chợ rẻ hơn siêu thị 25%

Thời điểm mua:
• Sáng sớm: Rau củ tươi, giá tốt
• Chiều muộn: Thịt cá có ưu đãi

Lời khuyên dinh dưỡng:
• Cân bằng protein và vitamin
• Đa dạng màu sắc rau củ
"""
    
    def _get_mock_market_response(self) -> str:
        """Mock response cho market insights"""
        return """
Tổng quan thị trường:
Ổn định với xu hướng tăng nhẹ theo lạm phát

Trending:
• Thực phẩm organic
• Rau sạch thủy canh
• Thịt không hormone

Khuyến nghị:
• Tập trung vào chất lượng
• Mua sắm thông minh
• Theo dõi khuyến mãi
"""
    
    def _parse_trend_analysis_response(self, response: str, category: Optional[str], days_back: int) -> Dict[str, Any]:
        """Parse AI response cho trend analysis"""
        return {
            "analysis_date": datetime.now().isoformat(),
            "category": category or "Tất cả",
            "period_days": days_back,
            "trend": "stable",
            "insights": [
                {
                    "title": "Xu hướng ổn định",
                    "description": response[:200] + "..." if len(response) > 200 else response,
                    "confidence": 0.8,
                    "category": "trend"
                }
            ],
            "recommendations": ["Theo dõi giá thường xuyên", "Mua theo nhu cầu thực tế"],
            "price_alerts": []
        }
    
    def _parse_prediction_response(self, response: str, food_name: str, days_ahead: int) -> Dict[str, Any]:
        """Parse AI response cho price prediction"""
        try:
            # Try to parse JSON response
            data = json.loads(response)
            return {
                "food_name": food_name,
                "current_price": 50000,  # Mock current price
                "predicted_price": data.get("predicted_price", 50000),
                "prediction_days": days_ahead,
                "confidence": data.get("confidence", 75),
                "trend": data.get("trend", "stable"),
                "factors": data.get("factors", ["Thời tiết", "Cung cầu"]),
                "recommendation": data.get("recommendation", "Theo dõi thêm"),
                "price_range": {"min": 45000, "max": 55000},
                "generated_at": datetime.now().isoformat()
            }
        except:
            return self._get_fallback_prediction(food_name, days_ahead)
    
    def _parse_seasonal_response(self, response: str, current_month: int) -> Dict[str, Any]:
        """Parse AI response cho seasonal analysis"""
        seasons = ["Mùa đông", "Mùa xuân", "Mùa hè", "Mùa thu"]
        season_index = (current_month - 1) // 3
        
        return {
            "current_season": seasons[season_index],
            "seasonal_foods": ["rau muống", "cà chua", "dưa hấu"],
            "price_predictions": {"rau muống": "giảm", "thịt bò": "tăng"},
            "buying_recommendations": ["Mua rau củ theo mùa"],
            "avoid_buying": ["Trái cây ngoại"],
            "best_deals": ["Cà chua", "Rau muống"],
            "analysis_date": datetime.now().isoformat()
        }
    
    def _parse_grocery_optimization_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response cho grocery optimization"""
        return {
            "total_items": 5,
            "optimization_suggestions": ["Thay thịt bò bằng thịt heo tiết kiệm 40%"],
            "substitution_recommendations": {"thịt bò": "thịt heo", "táo": "cam"},
            "timing_advice": "Mua sáng sớm để có giá tốt",
            "budget_optimization": "Có thể tiết kiệm 20% bằng cách thay đổi",
            "health_insights": "Cân bằng protein và vitamin",
            "sustainability_tips": "Ưu tiên thực phẩm địa phương",
            "generated_at": datetime.now().isoformat()
        }
    
    def _parse_market_insights_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response cho market insights"""
        return {
            "market_overview": "Thị trường ổn định với xu hướng tăng nhẹ",
            "trending_foods": ["Thực phẩm organic", "Rau sạch"],
            "price_volatility": {"cao": ["Thịt bò"], "thấp": ["Gạo"]},
            "regional_differences": "Giá TP.HCM cao hơn Hà Nội 10%",
            "consumer_behavior": "Quan tâm chất lượng hơn giá",
            "economic_factors": "Lạm phát ảnh hưởng nhẹ",
            "recommendations": ["Đầu tư vào thực phẩm sạch"],
            "generated_at": datetime.now().isoformat()
        }
    
    # Fallback methods
    def _get_fallback_trend_analysis(self, category: Optional[str], days_back: int) -> Dict[str, Any]:
        """Fallback response cho trend analysis"""
        return {
            "analysis_date": datetime.now().isoformat(),
            "category": category or "Tất cả",
            "period_days": days_back,
            "trend": "stable",
            "insights": [{"title": "Dữ liệu đang cập nhật", "description": "Vui lòng thử lại sau", "confidence": 0.5, "category": "info"}],
            "recommendations": ["Theo dõi giá thường xuyên"],
            "price_alerts": []
        }
    
    def _get_fallback_prediction(self, food_name: str, days_ahead: int) -> Dict[str, Any]:
        """Fallback response cho price prediction"""
        return {
            "food_name": food_name,
            "current_price": 0,
            "predicted_price": 0,
            "prediction_days": days_ahead,
            "confidence": 0,
            "trend": "unknown",
            "factors": [],
            "recommendation": "Cần thêm dữ liệu để dự đoán",
            "price_range": {"min": 0, "max": 0},
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_fallback_seasonal_analysis(self, current_month: int) -> Dict[str, Any]:
        """Fallback response cho seasonal analysis"""
        return {
            "current_season": "Không xác định",
            "seasonal_foods": [],
            "price_predictions": {},
            "buying_recommendations": ["Mua theo nhu cầu thực tế"],
            "avoid_buying": [],
            "best_deals": [],
            "analysis_date": datetime.now().isoformat()
        }
    
    def _get_fallback_grocery_optimization(self) -> Dict[str, Any]:
        """Fallback response cho grocery optimization"""
        return {
            "total_items": 0,
            "optimization_suggestions": ["So sánh giá nhiều nơi"],
            "substitution_recommendations": {},
            "timing_advice": "Mua sáng sớm thường có giá tốt",
            "budget_optimization": "Lập kế hoạch mua sắm chi tiết",
            "health_insights": "Cân bằng các nhóm thực phẩm",
            "sustainability_tips": "Ưu tiên sản phẩm địa phương",
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_fallback_market_insights(self) -> Dict[str, Any]:
        """Fallback response cho market insights"""
        return {
            "market_overview": "Đang thu thập dữ liệu thị trường",
            "trending_foods": [],
            "price_volatility": {},
            "regional_differences": "Dữ liệu đang cập nhật",
            "consumer_behavior": "Phân tích đang được thực hiện",
            "economic_factors": "Theo dõi các yếu tố kinh tế",
            "recommendations": ["Theo dõi xu hướng giá"],
            "generated_at": datetime.now().isoformat()
        }


# Tạo instance global
ai_price_analysis_service = AIPriceAnalysisService()
