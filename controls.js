/**
 * controls.js - Xử lý chức năng cho trang điều khiển
 * Hệ thống nông nghiệp thông minh
 */

// Biến lưu trạng thái hệ thống
let systemState = {
    coverMotor: false,
    waterMotor: false,
    autoMode: true,
    rainThreshold: 40,
    soilMoistureThreshold: 30
};

// Biến lưu giá trị cảm biến hiện tại
let currentSensorValues = {
    rain: 0,
    soilMoisture: 0,
    ph: 7
};

// Khi trang đã tải xong
document.addEventListener('DOMContentLoaded', function() {
    // Lấy các phần tử điều khiển
    const autoModeSwitch = document.getElementById('auto-mode-switch');
    const manualControls = document.getElementById('manual-controls');
    const coverOnBtn = document.getElementById('cover-on-btn');
    const coverOffBtn = document.getElementById('cover-off-btn');
    const waterOnBtn = document.getElementById('water-on-btn');
    const waterOffBtn = document.getElementById('water-off-btn');
    const rainThresholdInput = document.getElementById('rain-threshold');
    const soilThresholdInput = document.getElementById('soil-threshold');
    const saveThresholdsBtn = document.getElementById('save-thresholds-btn');

    // Cài đặt sự kiện cho công tắc chế độ tự động
    if (autoModeSwitch) {
        autoModeSwitch.addEventListener('change', function() {
            toggleAutoMode(this.checked);
        });
    }

    // Cài đặt sự kiện cho các nút điều khiển mái che
    if (coverOnBtn) {
        coverOnBtn.addEventListener('click', function() {
            controlCoverMotor('activate');
        });
    }
    
    if (coverOffBtn) {
        coverOffBtn.addEventListener('click', function() {
            controlCoverMotor('stop');
        });
    }

    // Cài đặt sự kiện cho các nút điều khiển tưới nước
    if (waterOnBtn) {
        waterOnBtn.addEventListener('click', function() {
            controlWaterMotor('activate');
        });
    }
    
    if (waterOffBtn) {
        waterOffBtn.addEventListener('click', function() {
            controlWaterMotor('stop');
        });
    }

    // Cài đặt sự kiện cho nút lưu ngưỡng
    if (saveThresholdsBtn) {
        saveThresholdsBtn.addEventListener('click', function() {
            saveThresholds();
        });
    }

    // Tải trạng thái hiện tại của hệ thống
    loadCurrentState();

    // Đăng ký sự kiện Socket.IO
    registerSocketEvents();
});

// Hàm chuyển đổi chế độ tự động/thủ công
function toggleAutoMode(isAuto) {
    const manualControls = document.getElementById('manual-controls');
    const autoModeStatus = document.getElementById('auto-mode-status');
    
    if (manualControls) {
        manualControls.style.display = isAuto ? 'none' : 'block';
    }
    
    if (autoModeStatus) {
        autoModeStatus.textContent = isAuto ? 'Đang bật' : 'Đang tắt';
        autoModeStatus.className = isAuto ? 'badge bg-success' : 'badge bg-secondary';
    }
    
    systemState.autoMode = isAuto;
    
    // Gửi yêu cầu đến server
    fetch('/api/mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: isAuto ? 'auto' : 'manual' })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Lỗi khi chuyển đổi chế độ:', data.message);
            // Hiển thị thông báo lỗi nếu cần
        }
    })
    .catch(error => {
        console.error('Lỗi khi gửi yêu cầu:', error);
        // Hiển thị thông báo lỗi
    });
}

// Hàm điều khiển động cơ mái che
function controlCoverMotor(action) {
    // Cập nhật UI trước để phản hồi nhanh
    updateMotorUI('cover', action === 'activate');
    
    // Gửi yêu cầu đến server
    fetch('/api/motor/cover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            systemState.coverMotor = data.cover_motor;
            updateMotorUI('cover', data.cover_motor);
        } else {
            console.error('Lỗi khi điều khiển mái che:', data.message);
            // Khôi phục UI nếu có lỗi
            updateMotorUI('cover', systemState.coverMotor);
        }
    })
    .catch(error => {
        console.error('Lỗi khi gửi yêu cầu:', error);
        // Khôi phục UI nếu có lỗi
        updateMotorUI('cover', systemState.coverMotor);
    });
}

// Hàm điều khiển động cơ tưới nước
function controlWaterMotor(action) {
    // Cập nhật UI trước để phản hồi nhanh
    updateMotorUI('water', action === 'activate');
    
    // Gửi yêu cầu đến server
    fetch('/api/motor/water', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            systemState.waterMotor = data.water_motor;
            updateMotorUI('water', data.water_motor);
        } else {
            console.error('Lỗi khi điều khiển tưới nước:', data.message);
            // Khôi phục UI nếu có lỗi
            updateMotorUI('water', systemState.waterMotor);
        }
    })
    .catch(error => {
        console.error('Lỗi khi gửi yêu cầu:', error);
        // Khôi phục UI nếu có lỗi
        updateMotorUI('water', systemState.waterMotor);
    });
}

// Hàm cập nhật UI động cơ
function updateMotorUI(motorType, isActive) {
    // Cập nhật trạng thái hiển thị động cơ
    const statusElement = document.getElementById(`${motorType}-motor-status`);
    if (statusElement) {
        statusElement.textContent = isActive ? 'Đang hoạt động' : 'Không hoạt động';
        statusElement.className = `badge ${isActive ? 'bg-success' : 'bg-danger'}`;
    }
    
    // Cập nhật trạng thái nút
    const onButton = document.getElementById(`${motorType}-on-btn`);
    const offButton = document.getElementById(`${motorType}-off-btn`);
    
    if (onButton) {
        onButton.disabled = isActive;
        onButton.classList.toggle('btn-success', !isActive);
        onButton.classList.toggle('btn-secondary', isActive);
    }
    
    if (offButton) {
        offButton.disabled = !isActive;
        offButton.classList.toggle('btn-danger', isActive);
        offButton.classList.toggle('btn-secondary', !isActive);
    }
}

// Hàm lưu ngưỡng cảm biến
function saveThresholds() {
    const rainThresholdInput = document.getElementById('rain-threshold');
    const soilThresholdInput = document.getElementById('soil-threshold');
    
    if (!rainThresholdInput || !soilThresholdInput) return;
    
    const rainThreshold = parseFloat(rainThresholdInput.value);
    const soilThreshold = parseFloat(soilThresholdInput.value);
    
    // Kiểm tra giá trị hợp lệ
    if (isNaN(rainThreshold) || isNaN(soilThreshold)) {
        alert('Vui lòng nhập giá trị số hợp lệ cho các ngưỡng');
        return;
    }
    
    // Kiểm tra phạm vi giá trị
    if (rainThreshold < 0 || rainThreshold > 100 || soilThreshold < 0 || soilThreshold > 100) {
        alert('Giá trị ngưỡng phải nằm trong khoảng 0-100%');
        return;
    }
    
    // Cập nhật biến trạng thái
    systemState.rainThreshold = rainThreshold;
    systemState.soilMoistureThreshold = soilThreshold;
    
    // Gửi yêu cầu cập nhật ngưỡng đến server
    fetch('/api/thresholds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            rain_threshold: rainThreshold,
            soil_moisture_threshold: soilThreshold
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hiển thị thông báo thành công
            showAlert('Đã cập nhật ngưỡng thành công', 'success');
            // Cập nhật hiển thị cảnh báo
            updateWarningDisplay();
        } else {
            console.error('Lỗi khi cập nhật ngưỡng:', data.message);
            showAlert('Lỗi khi cập nhật ngưỡng', 'danger');
        }
    })
    .catch(error => {
        console.error('Lỗi khi gửi yêu cầu:', error);
        showAlert('Lỗi kết nối đến máy chủ', 'danger');
    });
}

// Hàm hiển thị thông báo
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    // Tạo phần tử alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Thêm vào container
    alertsContainer.appendChild(alertDiv);
    
    // Tự động xóa sau 5 giây
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// Hàm cập nhật hiển thị cảnh báo
function updateWarningDisplay() {
    // Kiểm tra các điều kiện cảnh báo dựa trên giá trị cảm biến và ngưỡng
    const rainAlert = document.getElementById('rain-alert');
    const soilAlert = document.getElementById('soil-alert');
    
    if (rainAlert) {
        if (currentSensorValues.rain > systemState.rainThreshold) {
            rainAlert.textContent = `Cảnh báo: Đang mưa (${currentSensorValues.rain.toFixed(1)}%)`;
            rainAlert.className = 'alert alert-warning';
            rainAlert.style.display = 'block';
        } else {
            rainAlert.style.display = 'none';
        }
    }
    
    if (soilAlert) {
        if (currentSensorValues.soilMoisture < systemState.soilMoistureThreshold) {
            soilAlert.textContent = `Cảnh báo: Đất khô (${currentSensorValues.soilMoisture.toFixed(1)}%)`;
            soilAlert.className = 'alert alert-danger';
            soilAlert.style.display = 'block';
        } else {
            soilAlert.style.display = 'none';
        }
    }
}

// Hàm tải trạng thái hiện tại của hệ thống
function loadCurrentState() {
    // Tải dữ liệu hiện tại từ server
    fetch('/api/latest-data')
        .then(response => response.json())
        .then(data => {
            // Cập nhật trạng thái động cơ
            if (data.motor_state) {
                systemState.coverMotor = data.motor_state.cover_motor_active;
                systemState.waterMotor = data.motor_state.water_motor_active;
                
                // Cập nhật UI
                updateMotorUI('cover', systemState.coverMotor);
                updateMotorUI('water', systemState.waterMotor);
            }
            
            // Cập nhật trạng thái chế độ tự động
            const autoModeSwitch = document.getElementById('auto-mode-switch');
            if (autoModeSwitch && data.auto_mode !== undefined) {
                systemState.autoMode = data.auto_mode;
                autoModeSwitch.checked = systemState.autoMode;
                toggleAutoMode(systemState.autoMode);
            }
            
            // Cập nhật giá trị ngưỡng
            if (data.thresholds) {
                systemState.rainThreshold = data.thresholds.rain_threshold;
                systemState.soilMoistureThreshold = data.thresholds.soil_moisture_threshold;
                
                const rainThresholdInput = document.getElementById('rain-threshold');
                const soilThresholdInput = document.getElementById('soil-threshold');
                
                if (rainThresholdInput) {
                    rainThresholdInput.value = systemState.rainThreshold;
                }
                
                if (soilThresholdInput) {
                    soilThresholdInput.value = systemState.soilMoistureThreshold;
                }
            }
            
            // Cập nhật giá trị cảm biến
            if (data.sensor_data) {
                currentSensorValues.rain = data.sensor_data.rain_percent;
                currentSensorValues.soilMoisture = data.sensor_data.soil_moisture_percent;
                currentSensorValues.ph = data.sensor_data.ph_value;
                
                // Cập nhật hiển thị cảm biến
                updateSensorDisplay();
                
                // Cập nhật hiển thị cảnh báo
                updateWarningDisplay();
            }
        })
        .catch(error => {
            console.error('Lỗi khi tải trạng thái hiện tại:', error);
            showAlert('Không thể tải trạng thái hệ thống. Vui lòng làm mới trang.', 'danger');
        });
}

// Hàm cập nhật hiển thị cảm biến
function updateSensorDisplay() {
    const rainValue = document.getElementById('current-rain');
    const soilValue = document.getElementById('current-soil');
    const phValue = document.getElementById('current-ph');
    
    if (rainValue) {
        rainValue.textContent = currentSensorValues.rain.toFixed(1) + '%';
    }
    
    if (soilValue) {
        soilValue.textContent = currentSensorValues.soilMoisture.toFixed(1) + '%';
    }
    
    if (phValue) {
        phValue.textContent = currentSensorValues.ph.toFixed(1);
    }
}

// Đăng ký sự kiện Socket.IO
function registerSocketEvents() {
    if (typeof socket === 'undefined') {
        console.error('Socket.IO chưa được khởi tạo');
        return;
    }
    
    // Cập nhật khi nhận dữ liệu cảm biến mới
    socket.on('sensor_data', function(data) {
        currentSensorValues.rain = data.rain;
        currentSensorValues.soilMoisture = data.soil_moisture;
        currentSensorValues.ph = data.ph;
        
        // Cập nhật hiển thị
        updateSensorDisplay();
        updateWarningDisplay();
    });
    
    // Cập nhật khi trạng thái động cơ thay đổi
    socket.on('motor_state', function(data) {
        systemState.coverMotor = data.cover_motor;
        systemState.waterMotor = data.water_motor;
        
        // Cập nhật UI
        updateMotorUI('cover', systemState.coverMotor);
        updateMotorUI('water', systemState.waterMotor);
    });
}
