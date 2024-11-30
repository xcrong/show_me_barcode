// IndexedDB 初始化
let db;
const DB_NAME = 'SearchHistoryDB';
const STORE_NAME = 'searchHistory';
const MAX_HISTORY = 10;

const request = indexedDB.open(DB_NAME, 1);

request.onerror = (event) => {
    console.error("数据库错误:", event.target.error);
};

request.onupgradeneeded = (event) => {
    db = event.target.result;
    if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'timestamp' });
        store.createIndex('query', 'query', { unique: false });
    }
};

request.onsuccess = (event) => {
    db = event.target.result;
    loadSearchHistory();
};

// 保存搜索历史
function saveToHistory(query, result) {
    if (!db) return;

    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    const historyItem = {
        timestamp: Date.now(),
        query: query,
        result: result
    };

    store.add(historyItem);

    // 保持最多10条记录
    store.count().onsuccess = (event) => {
        const count = event.target.result;
        if (count > MAX_HISTORY) {
            store.openCursor().onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    store.delete(cursor.key);
                }
            };
        }
    };

    loadSearchHistory();
}

// 加载搜索历史
function loadSearchHistory() {
    if (!db) return;

    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.getAll();

    request.onsuccess = () => {
        const history = request.result;
        if (history.length > 0) {
            displayHistory(history);
            document.getElementById('historyContainer').classList.remove('hidden');
        } else {
            document.getElementById('historyContainer').classList.add('hidden');
        }
    };
}

// 显示历史记录
function displayHistory(history) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';

    history.sort((a, b) => b.timestamp - a.timestamp)
        .forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item p-2 rounded hover:bg-gray-50 cursor-pointer';
            div.textContent = item.query;
            div.addEventListener('click', () => {
                if (item.result) {
                    displayResult(item.result);
                } else {
                    // 如果没有缓存结果，直接用这个查询重新搜索
                    const formData = new FormData();
                    formData.append('query', item.query);
                    fetch('/search', {
                        method: 'POST',
                        body: formData
                    })
                        .then(response => response.json())
                        .then(data => {
                            displayResult(data);
                            if (!data.error) {
                                saveToHistory(item.query, data);
                            }
                        })
                        .catch(error => {
                            resultDiv.classList.remove('hidden');
                            bookInfo.classList.add('hidden');
                            errorMessage.classList.remove('hidden');
                            errorMessage.textContent = '查询出错，请稍后重试';
                        });
                }
            });
            historyList.appendChild(div);
        });
}

// DOM 元素
const searchForm = document.getElementById('searchForm');
const searchButton = document.getElementById('searchButton');
const spinner = searchButton.querySelector('.loading-spinner');
const loadingState = document.getElementById('loadingState');
const resultDiv = document.getElementById('result');
const bookInfo = document.getElementById('bookInfo');
const errorMessage = document.getElementById('errorMessage');
const queryInput = document.getElementById('query');

function setLoading(isLoading) {
    if (isLoading) {
        spinner.classList.remove('hidden');
        searchButton.disabled = true;
        searchButton.classList.add('opacity-75');
        queryInput.disabled = true;
        loadingState.classList.remove('hidden');
        resultDiv.classList.add('hidden');
    } else {
        spinner.classList.add('hidden');
        searchButton.disabled = false;
        searchButton.classList.remove('opacity-75');
        queryInput.disabled = false;
        loadingState.classList.add('hidden');
    }
}

function displayResult(data) {
    resultDiv.classList.remove('hidden');
    if (data.error) {
        bookInfo.classList.add('hidden');
        errorMessage.classList.remove('hidden');
        errorMessage.textContent = data.error;
    } else {
        bookInfo.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        document.getElementById('bookTitle').textContent = data.book;
        document.getElementById('bookIsbn').textContent = data.isbn;
        document.getElementById('barcodeImage').src = data.barcode;
    }
    // 滚动到结果区域
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 事件监听器
document.addEventListener('DOMContentLoaded', () => {
    // 清空历史记录
    document.getElementById('clearHistory').addEventListener('click', () => {
        if (!db) return;

        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        store.clear();
        document.getElementById('historyContainer').classList.add('hidden');
        // 刷新页面
        window.location.reload();
    });

    // 搜索表单提交
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = queryInput.value;

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('query', query);

            const response = await fetch('/search', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            displayResult(data);

            // 保存到历史记录
            if (!data.error) {
                saveToHistory(query, data);
            }
        } catch (error) {
            resultDiv.classList.remove('hidden');
            bookInfo.classList.add('hidden');
            errorMessage.classList.remove('hidden');
            errorMessage.textContent = '查询出错，请稍后重试';
        } finally {
            setLoading(false);
            queryInput.value = '';
        }
    });
});