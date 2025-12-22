// ==================== API BASE URL ====================
const API_BASE = '';

// ==================== STATE ====================
let categories = [];
let questions = [];
let models = { gemini: [], huggingface: [], all: [] };
let selectedModels = [];

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadInitialData();
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewName = item.dataset.view;
            switchView(viewName);
            
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    // View'a göre veri yükle
    switch(viewName) {
        case 'dashboard':
            loadStats();
            break;
        case 'categories':
            loadCategories();
            break;
        case 'questions':
            loadQuestions();
            break;
        case 'test':
            loadTestView();
            break;
        case 'results':
            loadResults();
            break;
    }
}

async function loadInitialData() {
    showLoading('Veriler yükleniyor...');
    try {
        await Promise.all([
            loadStats(),
            loadModels()
        ]);
    } catch (error) {
        console.error('Initial load error:', error);
    }
    hideLoading();
}

// ==================== API FUNCTIONS ====================
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ==================== STATS ====================
async function loadStats() {
    try {
        const stats = await fetchAPI('/api/stats');
        
        document.getElementById('stat-categories').textContent = stats.total_categories;
        document.getElementById('stat-questions').textContent = stats.total_questions;
        document.getElementById('stat-results').textContent = stats.total_results;
        document.getElementById('stat-models').textContent = models.all?.length || 0;
        
        // Model stats
        const container = document.getElementById('model-stats-container');
        if (stats.model_stats && stats.model_stats.length > 0) {
            container.innerHTML = stats.model_stats.map(s => `
                <div class="model-stat-card">
                    <h4>${s.model_name}</h4>
                    <div class="provider">${s.provider === 'gemini' ? '🌟 Gemini' : '🤗 Hugging Face'}</div>
                    <div class="stats">
                        <div class="stat">
                            <span class="stat-num">${s.test_count}</span>
                            <span class="stat-name">Test</span>
                        </div>
                        <div class="stat">
                            <span class="stat-num">${s.avg_response_time}s</span>
                            <span class="stat-name">Ort. Süre</span>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><div class="icon">📊</div><p>Henüz test sonucu yok</p></div>';
        }
    } catch (error) {
        console.error('Stats load error:', error);
    }
}

// ==================== MODELS ====================
async function loadModels() {
    try {
        models = await fetchAPI('/api/models');
        document.getElementById('model-count').textContent = models.all?.length || 0;
        document.getElementById('stat-models').textContent = models.all?.length || 0;
    } catch (error) {
        console.error('Models load error:', error);
    }
}

// ==================== CATEGORIES ====================
async function loadCategories() {
    try {
        categories = await fetchAPI('/api/categories');
        renderCategories();
        updateCategoryFilters();
    } catch (error) {
        console.error('Categories load error:', error);
    }
}

function renderCategories() {
    const container = document.getElementById('categories-container');
    
    if (categories.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📁</div>
                <p>Kategori bulunamadı. Veritabanını seed edin.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = categories.map(c => `
        <div class="category-card" onclick="showCategoryDetails(${c.id})">
            <span class="code">${c.category_code}</span>
            <h3>${c.category_name}</h3>
            <p class="description">${c.description || ''}</p>
            <div class="meta">
                <span>🔴 ${c.error_count} Hata Tipi</span>
                <span>❓ ${c.question_count} Soru</span>
            </div>
        </div>
    `).join('');
}

async function showCategoryDetails(categoryId) {
    try {
        const category = await fetchAPI(`/api/categories/${categoryId}`);
        
        const card = document.querySelector(`[onclick="showCategoryDetails(${categoryId})"]`);
        
        // Toggle error types
        let errorList = card.querySelector('.error-types-list');
        if (errorList) {
            errorList.remove();
        } else {
            const html = `
                <div class="error-types-list">
                    <h4>Hata Tipleri:</h4>
                    ${category.error_types.map(e => `<span class="error-type-tag">${e.error_type}</span>`).join('')}
                </div>
            `;
            card.insertAdjacentHTML('beforeend', html);
        }
    } catch (error) {
        console.error('Category details error:', error);
    }
}

function updateCategoryFilters() {
    const selects = [
        document.getElementById('question-category-filter'),
        document.getElementById('new-question-category')
    ];
    
    selects.forEach(select => {
        if (!select) return;
        const firstOption = select.querySelector('option');
        select.innerHTML = '';
        if (firstOption && firstOption.value === '') {
            select.appendChild(firstOption);
        }
        
        categories.forEach(c => {
            const option = document.createElement('option');
            option.value = c.id;
            option.textContent = `${c.category_code} - ${c.category_name}`;
            select.appendChild(option);
        });
    });
}

// ==================== QUESTIONS ====================
async function loadQuestions() {
    if (categories.length === 0) {
        await loadCategories();
    }
    
    try {
        const categoryFilter = document.getElementById('question-category-filter').value;
        const endpoint = categoryFilter 
            ? `/api/questions?category_id=${categoryFilter}`
            : '/api/questions';
        
        questions = await fetchAPI(endpoint);
        renderQuestions();
        updateQuestionSelects();
    } catch (error) {
        console.error('Questions load error:', error);
    }
}

function renderQuestions() {
    const container = document.getElementById('questions-container');
    
    if (questions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">❓</div>
                <p>Henüz soru eklenmemiş. "Yeni Soru Ekle" butonuna tıklayın.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = questions.map(q => `
        <div class="question-card">
            <div class="content">
                <span class="category-badge">${q.category_code}</span>
                <p class="question-text">${q.question_text}</p>
                <div class="meta">
                    <span>📅 ${new Date(q.created_at).toLocaleDateString('tr-TR')}</span>
                    <span>🧪 ${q.result_count} Test</span>
                </div>
            </div>
            <div class="actions">
                <button class="btn btn-primary btn-sm" onclick="quickTest(${q.id})">🚀 Test</button>
                <button class="btn btn-danger btn-sm" onclick="deleteQuestion(${q.id})">🗑️</button>
            </div>
        </div>
    `).join('');
}

function updateQuestionSelects() {
    const selects = [
        document.getElementById('test-question-select'),
        document.getElementById('result-question-filter')
    ];
    
    selects.forEach(select => {
        if (!select) return;
        const firstOption = select.querySelector('option');
        select.innerHTML = '';
        if (firstOption) {
            select.appendChild(firstOption);
        }
        
        questions.forEach(q => {
            const option = document.createElement('option');
            option.value = q.id;
            option.textContent = `[${q.category_code}] ${q.question_text.substring(0, 60)}...`;
            select.appendChild(option);
        });
    });
}

function showAddQuestionModal() {
    if (categories.length === 0) {
        alert('Önce kategoriler yüklenmelidir!');
        return;
    }
    document.getElementById('add-question-modal').classList.add('active');
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
    document.getElementById('new-question-text').value = '';
}

async function addQuestion() {
    const categoryId = document.getElementById('new-question-category').value;
    const questionText = document.getElementById('new-question-text').value.trim();
    
    if (!categoryId || !questionText) {
        alert('Lütfen tüm alanları doldurun!');
        return;
    }
    
    showLoading('Soru ekleniyor...');
    
    try {
        await fetchAPI('/api/questions', {
            method: 'POST',
            body: JSON.stringify({
                category_id: parseInt(categoryId),
                question_text: questionText
            })
        });
        
        closeModal();
        await loadQuestions();
        await loadStats();
    } catch (error) {
        alert('Soru eklenirken hata oluştu!');
    }
    
    hideLoading();
}

async function deleteQuestion(questionId) {
    if (!confirm('Bu soruyu silmek istediğinize emin misiniz?')) return;
    
    showLoading('Soru siliniyor...');
    
    try {
        await fetchAPI(`/api/questions/${questionId}`, { method: 'DELETE' });
        await loadQuestions();
        await loadStats();
    } catch (error) {
        alert('Soru silinirken hata oluştu!');
    }
    
    hideLoading();
}

// ==================== TEST VIEW ====================
async function loadTestView() {
    if (questions.length === 0) {
        await loadQuestions();
    }
    
    // Gemini modelleri
    const geminiContainer = document.getElementById('gemini-models');
    geminiContainer.innerHTML = models.gemini.map(m => `
        <label class="model-checkbox" data-model="${m}" data-provider="gemini">
            <input type="checkbox" value="${m}">
            ${m}
        </label>
    `).join('');
    
    // Hugging Face modelleri
    const hfContainer = document.getElementById('huggingface-models');
    hfContainer.innerHTML = models.huggingface.map(m => `
        <label class="model-checkbox" data-model="${m}" data-provider="huggingface">
            <input type="checkbox" value="${m}">
            ${m.split('/').pop()}
        </label>
    `).join('');
    
    // Checkbox event listeners
    document.querySelectorAll('.model-checkbox').forEach(cb => {
        cb.addEventListener('click', (e) => {
            e.preventDefault();
            cb.classList.toggle('selected');
            const input = cb.querySelector('input');
            input.checked = !input.checked;
        });
    });
}

function selectAllModels() {
    document.querySelectorAll('.model-checkbox').forEach(cb => {
        cb.classList.add('selected');
        cb.querySelector('input').checked = true;
    });
}

function deselectAllModels() {
    document.querySelectorAll('.model-checkbox').forEach(cb => {
        cb.classList.remove('selected');
        cb.querySelector('input').checked = false;
    });
}

async function runTest() {
    const questionId = document.getElementById('test-question-select').value;
    if (!questionId) {
        alert('Lütfen bir soru seçin!');
        return;
    }
    
    const selectedCheckboxes = document.querySelectorAll('.model-checkbox.selected');
    if (selectedCheckboxes.length === 0) {
        alert('Lütfen en az bir model seçin!');
        return;
    }
    
    const resultsContainer = document.getElementById('test-results');
    resultsContainer.innerHTML = '';
    
    showLoading('Testler çalıştırılıyor...');
    
    for (const cb of selectedCheckboxes) {
        const modelName = cb.dataset.model;
        const provider = cb.dataset.provider;
        
        document.getElementById('loading-text').textContent = `Test: ${modelName}...`;
        
        try {
            const result = await fetchAPI('/api/test', {
                method: 'POST',
                body: JSON.stringify({
                    question_id: parseInt(questionId),
                    model_name: modelName,
                    provider: provider
                })
            });
            
            const cardClass = result.success ? 'success' : 'error';
            const cardHtml = `
                <div class="test-result-card ${cardClass}">
                    <div class="header">
                        <span class="model-name">${result.model_name}</span>
                        <span class="provider-badge">${provider === 'gemini' ? '🌟 Gemini' : '🤗 HuggingFace'}</span>
                    </div>
                    ${result.success 
                        ? `<div class="response">${result.response}</div>
                           <div class="response-time">⏱️ Yanıt süresi: ${result.response_time}s</div>`
                        : `<div class="response" style="color: var(--error)">❌ Hata: ${result.error}</div>`
                    }
                </div>
            `;
            resultsContainer.insertAdjacentHTML('beforeend', cardHtml);
        } catch (error) {
            const errorHtml = `
                <div class="test-result-card error">
                    <div class="header">
                        <span class="model-name">${modelName}</span>
                        <span class="provider-badge">${provider}</span>
                    </div>
                    <div class="response" style="color: var(--error)">❌ Bağlantı hatası: ${error.message}</div>
                </div>
            `;
            resultsContainer.insertAdjacentHTML('beforeend', errorHtml);
        }
    }
    
    hideLoading();
    await loadStats();
}

async function quickTest(questionId) {
    // Test view'a geç
    switchView('test');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector('[data-view="test"]').classList.add('active');
    
    // Görünümü yükle
    await loadTestView();
    
    // Soruyu seç
    document.getElementById('test-question-select').value = questionId;
}

// ==================== RESULTS ====================
async function loadResults() {
    if (questions.length === 0) {
        await loadQuestions();
    }
    
    try {
        const questionFilter = document.getElementById('result-question-filter').value;
        const endpoint = questionFilter 
            ? `/api/results?question_id=${questionFilter}`
            : '/api/results';
        
        const results = await fetchAPI(endpoint);
        renderResults(results);
    } catch (error) {
        console.error('Results load error:', error);
    }
}

function renderResults(results) {
    const container = document.getElementById('results-container');
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📋</div>
                <p>Henüz test sonucu yok.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = results.map(r => `
        <div class="result-card">
            <div class="header">
                <div class="question-info">
                    <p class="question-text">${r.question_text}</p>
                    <div class="model-info">
                        <span class="model-name">${r.model_name}</span>
                        <span>${r.model_provider === 'gemini' ? '🌟 Gemini' : '🤗 HuggingFace'}</span>
                    </div>
                </div>
                <button class="btn btn-danger btn-sm" onclick="deleteResult(${r.id})">🗑️</button>
            </div>
            <div class="response">${r.response}</div>
            <div class="meta">
                <span>⏱️ ${r.response_time}s</span>
                <span>📅 ${new Date(r.tested_at).toLocaleString('tr-TR')}</span>
            </div>
        </div>
    `).join('');
}

async function deleteResult(resultId) {
    if (!confirm('Bu sonucu silmek istediğinize emin misiniz?')) return;
    
    showLoading('Sonuç siliniyor...');
    
    try {
        await fetchAPI(`/api/results/${resultId}`, { method: 'DELETE' });
        await loadResults();
        await loadStats();
    } catch (error) {
        alert('Sonuç silinirken hata oluştu!');
    }
    
    hideLoading();
}

// ==================== LOADING ====================
function showLoading(text = 'Yükleniyor...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}
