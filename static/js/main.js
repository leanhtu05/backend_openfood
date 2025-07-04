// Main JavaScript file for OpenFood application

// Food creation functions
function generateRandomMeal() {
    const generateBtn = document.getElementById('generate-btn');
    const statusDiv = document.getElementById('generate-status');
    
    // Get form values
    const mealType = document.getElementById('meal_type').value;
    const cuisineStyle = document.getElementById('cuisine_style').value;
    const calories = document.getElementById('calories').value;
    const protein = document.getElementById('protein').value;
    const fat = document.getElementById('fat').value;
    const carbs = document.getElementById('carbs').value;
    
    // Disable button and show loading
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Đang tạo...';
    statusDiv.innerHTML = '<div class="text-info">🤖 AI đang tạo món ăn cho bạn...</div>';
    
    // Simulate AI generation (replace with actual API call)
    setTimeout(() => {
        // Sample generated data
        const generatedMeal = {
            name: "Cơm Gà Xối Sài Gòn",
            description: "Món cơm gà truyền thống với hương vị đặc trưng của Sài Gòn",
            preparation_time: "30 phút",
            health_benefits: "Giàu protein, cung cấp năng lượng cho cả ngày",
            ingredients: ["Gạo tám xoan", "Thịt gà", "Hành tây", "Tỏi", "Nước mắm"],
            preparation_steps: ["Nấu cơm", "Luộc thịt gà", "Xào hành tỏi", "Trình bày"]
        };
        
        // Fill form with generated data
        document.getElementById('name').value = generatedMeal.name;
        document.getElementById('description').value = generatedMeal.description;
        document.getElementById('preparation_time').value = generatedMeal.preparation_time;
        document.getElementById('health_benefits').value = generatedMeal.health_benefits;
        
        // Update nutrition values
        document.getElementById('calories_input').value = calories;
        document.getElementById('protein_input').value = protein;
        document.getElementById('fat_input').value = fat;
        document.getElementById('carbs_input').value = carbs;
        
        // Clear existing ingredients and steps
        document.getElementById('ingredients-container').innerHTML = '';
        document.getElementById('preparation-container').innerHTML = '';
        
        // Add generated ingredients
        generatedMeal.ingredients.forEach(ingredient => {
            addIngredientInput(ingredient);
        });
        
        // Add generated preparation steps
        generatedMeal.preparation_steps.forEach(step => {
            addPreparationStep(step);
        });
        
        // Reset button and show success
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="me-1">🤖</span> Tạo món ăn với AI';
        statusDiv.innerHTML = '<div class="text-success">✅ Đã tạo món ăn thành công!</div>';
        
        // Clear status after 3 seconds
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 3000);
    }, 2000);
}

function addIngredientInput(value = '') {
    const container = document.getElementById('ingredients-container');
    const index = container.children.length;
    
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <input type="text" class="form-control" name="ingredients[]" placeholder="Tên nguyên liệu" value="${value}">
        <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.remove()">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    container.appendChild(div);
}

function addPreparationStep(value = '') {
    const container = document.getElementById('preparation-container');
    const index = container.children.length + 1;
    
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <span class="input-group-text">Bước ${index}</span>
        <input type="text" class="form-control" name="preparation_steps[]" placeholder="Mô tả bước thực hiện" value="${value}">
        <button type="button" class="btn btn-outline-danger" onclick="removePreparationStep(this)">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    container.appendChild(div);
}

function removePreparationStep(button) {
    button.parentElement.remove();
    
    // Update step numbers
    const container = document.getElementById('preparation-container');
    const steps = container.querySelectorAll('.input-group-text');
    steps.forEach((step, index) => {
        step.textContent = `Bước ${index + 1}`;
    });
}

// Food deletion confirmation
function confirmDelete(id) {
    if (confirm('Bạn có chắc muốn xóa món ăn này?')) {
        window.location.href = `/food/delete/${id}`;
    }
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Loading spinner utility
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Đang xử lý...';
    element.disabled = true;
    
    return () => {
        element.innerHTML = originalContent;
        element.disabled = false;
    };
}
