// Hàm xác nhận xóa món ăn
function confirmDelete(id) {
    if (confirm('Bạn có chắc muốn xóa món ăn này?')) {
        deleteFood(id);
    }
}

// Hàm gọi API để xóa món ăn
function deleteFood(id) {
    fetch(`/api/food/${id}`, { 
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (response.ok) {
            // Nếu xóa thành công, reload lại trang
            window.location.reload();
        } else {
            alert('Có lỗi khi xóa món ăn');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra: ' + error);
    });
}

// Hàm để tạo món ăn ngẫu nhiên với Groq AI
function generateRandomMeal() {
    document.getElementById('generate-btn').disabled = true;
    document.getElementById('generate-status').textContent = 'Đang tạo món ăn...';
    
    // Lấy thông tin từ form
    const mealType = document.getElementById('meal_type').value;
    const calories = document.getElementById('calories').value;
    const protein = document.getElementById('protein').value;
    const fat = document.getElementById('fat').value;
    const carbs = document.getElementById('carbs').value;
    
    // Gọi API để tạo món ăn
    fetch('/api/generate-meal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            meal_type: mealType,
            calories: parseInt(calories),
            protein: parseInt(protein),
            fat: parseInt(fat),
            carbs: parseInt(carbs)
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hiển thị kết quả
        if (data && data.length > 0) {
            const meal = data[0];
            document.getElementById('name').value = meal.name;
            document.getElementById('description').value = meal.description;
            document.getElementById('preparation_time').value = meal.preparation_time;
            document.getElementById('health_benefits').value = meal.health_benefits;
            
            // Cập nhật dinh dưỡng
            document.getElementById('calories_input').value = meal.nutrition.calories;
            document.getElementById('protein_input').value = meal.nutrition.protein;
            document.getElementById('fat_input').value = meal.nutrition.fat;
            document.getElementById('carbs_input').value = meal.nutrition.carbs;
            
            // Xử lý ingredients
            const ingredientContainer = document.getElementById('ingredients-container');
            ingredientContainer.innerHTML = '';
            
            meal.ingredients.forEach((ingredient, index) => {
                addIngredientInput(ingredient.name, ingredient.amount);
            });
            
            // Xử lý preparation steps
            const preparationContainer = document.getElementById('preparation-container');
            preparationContainer.innerHTML = '';
            
            meal.preparation.forEach((step, index) => {
                addPreparationStep(step);
            });
            
            document.getElementById('generate-status').textContent = 'Món ăn đã được tạo thành công!';
        } else {
            document.getElementById('generate-status').textContent = 'Không thể tạo món ăn. Vui lòng thử lại!';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('generate-status').textContent = 'Lỗi: ' + error;
    })
    .finally(() => {
        document.getElementById('generate-btn').disabled = false;
    });
}

// Hàm để thêm input cho nguyên liệu
function addIngredientInput(name = '', amount = '') {
    const container = document.getElementById('ingredients-container');
    const index = container.children.length;
    
    const div = document.createElement('div');
    div.className = 'row mb-2';
    div.innerHTML = `
        <div class="col-md-6">
            <input type="text" class="form-control" name="ingredient_name_${index}" value="${name}" placeholder="Tên nguyên liệu">
        </div>
        <div class="col-md-4">
            <input type="text" class="form-control" name="ingredient_amount_${index}" value="${amount}" placeholder="Số lượng">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-danger" onclick="removeIngredientInput(this)">Xóa</button>
        </div>
    `;
    
    container.appendChild(div);
}

// Hàm để xóa input nguyên liệu
function removeIngredientInput(button) {
    const row = button.closest('.row');
    row.remove();
}

// Hàm thêm bước chế biến
function addPreparationStep(step = '') {
    const container = document.getElementById('preparation-container');
    const index = container.children.length;
    
    const div = document.createElement('div');
    div.className = 'row mb-2';
    div.innerHTML = `
        <div class="col-md-10">
            <input type="text" class="form-control" name="preparation_step_${index}" value="${step}" placeholder="Bước chế biến">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-danger" onclick="removePreparationStep(this)">Xóa</button>
        </div>
    `;
    
    container.appendChild(div);
}

// Hàm xóa bước chế biến
function removePreparationStep(button) {
    const row = button.closest('.row');
    row.remove();
}

// Khởi tạo khi trang được load
document.addEventListener('DOMContentLoaded', function() {
    // Thêm nguyên liệu đầu tiên nếu không có
    const ingredientsContainer = document.getElementById('ingredients-container');
    if (ingredientsContainer && ingredientsContainer.children.length === 0) {
        addIngredientInput();
    }
    
    // Thêm bước chế biến đầu tiên nếu không có
    const preparationContainer = document.getElementById('preparation-container');
    if (preparationContainer && preparationContainer.children.length === 0) {
        addPreparationStep();
    }
});
