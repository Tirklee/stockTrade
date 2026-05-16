document.addEventListener('DOMContentLoaded', function () {
    const selectAll = document.getElementById('select-all');
    const pageInput = document.querySelector('.pagination-page-input');
    const perPageInput = document.querySelector('.pagination-per-page-input');
    const maxPage = pageInput ? parseInt(pageInput.getAttribute('max'), 10) : 1;

    // Initialize toasts
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(function(toastElement) {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    });

    if (selectAll) {
        selectAll.addEventListener('change', function () {
            document.querySelectorAll('.select-record').forEach(function (checkbox) {
                checkbox.checked = selectAll.checked;
            });
        });
    }

    function changePerPage() {
        if (!perPageInput) {
            return;
        }
        const perPageValue = parseInt(perPageInput.value, 10);
        if (Number.isNaN(perPageValue) || perPageValue < 1) {
            alert('请输入有效的每页条数');
            return;
        }
        const params = new URLSearchParams(window.location.search);
        params.set('per_page', perPageValue);
        params.set('page', 1);
        window.location.search = params.toString();
    }

    function jumpPage() {
        if (!pageInput) {
            return;
        }
        const pageValue = parseInt(pageInput.value, 10);
        if (Number.isNaN(pageValue)) {
            alert('请输入正确的页码');
            return;
        }
        const targetPage = Math.max(1, Math.min(pageValue, maxPage));
        if (targetPage !== pageValue) {
            pageInput.value = targetPage;
        }
        const params = new URLSearchParams(window.location.search);
        params.set('page', targetPage);
        params.set('per_page', perPageInput ? perPageInput.value : '{{ current_per_page }}');
        window.location.search = params.toString();
    }

    if (pageInput) {
        pageInput.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                jumpPage();
            }
        });
    }

    if (perPageInput) {
        perPageInput.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                changePerPage();
            }
        });
    }

    window.changePerPage = changePerPage;
    window.jumpPage = jumpPage;

    const batchUpdateButton = document.querySelector('button[name="action"][value="update"][formaction*="bulk_action"]');
    if (batchUpdateButton) {
        batchUpdateButton.addEventListener('click', function () {
            const selectedCheckboxes = document.querySelectorAll('.select-record:checked');
            if (selectedCheckboxes.length === 0) {
                showToast('请先勾选要修改的记录。', 'warning');
                return;
            }
            ['trade_type', 'quantity', 'trade_price', 'trade_basis'].forEach(function(name) {
                const input = document.querySelector('[name="' + name + '"]');
                if (input) {
                    input.removeAttribute('required');
                }
            });
            var mainForm = document.getElementById('main-form');
            mainForm.querySelectorAll('input[name="selected_ids"]').forEach(function(el) { el.remove(); });
            selectedCheckboxes.forEach(function(checkbox) {
                var hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'selected_ids';
                hidden.value = checkbox.value;
                mainForm.appendChild(hidden);
            });
            var originalAction = mainForm.getAttribute('action');
            mainForm.setAttribute('action', batchUpdateButton.getAttribute('formaction') || originalAction);
            mainForm.submit();
            mainForm.setAttribute('action', originalAction);
        });
    }

    function getTableCellValue(cells, key) {
        const mapping = {
            trade_time: cells[2]?.textContent.trim() || '',
            stock_code: cells[3]?.textContent.trim() || '',
            stock_name: cells[4]?.textContent.trim() || '',
            trade_type: cells[5]?.textContent.trim() || '',
            quantity: cells[6]?.textContent.trim() || '',
            opening_price: cells[7]?.textContent.trim() || '',
            closing_price: cells[8]?.textContent.trim() || '',
            high_price: cells[9]?.textContent.trim() || '',
            low_price: cells[10]?.textContent.trim() || '',
            change_ratio: cells[11]?.textContent.trim() || '',
            trade_price: cells[12]?.textContent.trim() || '',
            commission_fee: cells[13]?.textContent.trim() || '',
            profit_loss: cells[14]?.textContent.trim() || '',
            trade_basis: cells[15]?.textContent.trim() || ''
        };
        return mapping[key] || '';
    }

    function normalizeValue(value, key) {
        const numberKeys = new Set(['quantity', 'opening_price', 'closing_price', 'high_price', 'low_price', 'change_ratio', 'trade_price', 'commission_fee', 'profit_loss']);
        const text = value.replace('%', '').trim();
        if (numberKeys.has(key)) {
            const number = parseFloat(text);
            return Number.isFinite(number) ? number : null;
        }
        return text.toLowerCase();
    }

    const sortPriorities = [];

    function updateSortIndicators() {
        document.querySelectorAll('th.sortable').forEach(function(th) {
            const indicator = th.querySelector('.sort-indicator');
            const priority = sortPriorities.find(function(item) {
                return item.key === th.dataset.sortKey;
            });
            if (priority) {
                const order = sortPriorities.indexOf(priority) + 1;
                indicator.textContent = priority.dir === 'asc' ? `▲${order}` : `▼${order}`;
                th.classList.add('sorted');
                th.dataset.sortDir = priority.dir;
            } else {
                indicator.textContent = '';
                th.classList.remove('sorted');
                th.dataset.sortDir = '';
            }
        });
    }

    function sortTable() {
        const table = document.querySelector('.table-responsive table');
        if (!table) {
            return;
        }
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        let sortedRows = rows;

        if (sortPriorities.length > 0) {
            sortedRows = rows.slice().sort(function(a, b) {
                const cellsA = a.querySelectorAll('td');
                const cellsB = b.querySelectorAll('td');
                for (const sortItem of sortPriorities) {
                    const valueA = normalizeValue(getTableCellValue(cellsA, sortItem.key), sortItem.key);
                    const valueB = normalizeValue(getTableCellValue(cellsB, sortItem.key), sortItem.key);

                    if (valueA === null && valueB === null) {
                        continue;
                    }
                    if (valueA === null) {
                        return 1;
                    }
                    if (valueB === null) {
                        return -1;
                    }
                    if (valueA < valueB) {
                        return sortItem.dir === 'asc' ? -1 : 1;
                    }
                    if (valueA > valueB) {
                        return sortItem.dir === 'asc' ? 1 : -1;
                    }
                }
                return 0;
            });
        }

        tbody.innerHTML = '';
        sortedRows.forEach(function(row) {
            tbody.appendChild(row);
        });
    }

    document.querySelectorAll('th.sortable').forEach(function(th) {
        th.addEventListener('click', function() {
            const key = th.dataset.sortKey;
            if (!key) {
                return;
            }
            const existingIndex = sortPriorities.findIndex(function(item) {
                return item.key === key;
            });
            let direction = 'asc';
            if (existingIndex >= 0) {
                direction = sortPriorities[existingIndex].dir === 'asc' ? 'desc' : 'asc';
                sortPriorities.splice(existingIndex, 1);
            }
            sortPriorities.push({ key: key, dir: direction });
            updateSortIndicators();
            sortTable();
        });
    });

    function showToast(message, type = 'warning') {
        const toastContainer = document.querySelector('.toast-container') || document.createElement('div');
        if (!document.querySelector('.toast-container')) {
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const toastElement = document.createElement('div');
        toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        toastElement.setAttribute('data-bs-delay', '3000');
        toastElement.setAttribute('data-bs-autohide', 'true');
        
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastElement);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    function confirmBulkDelete(button) {
        const selectedCheckboxes = document.querySelectorAll('.select-record:checked');
        if (selectedCheckboxes.length === 0) {
            showToast('请先勾选要删除的记录。', 'warning');
            return false;
        }

        const mainForm = document.getElementById('main-form');
        const originalAction = mainForm.getAttribute('action');
        const bulkAction = button.getAttribute('formaction') || originalAction;

        document.getElementById('deleteCount').textContent = selectedCheckboxes.length;

        const modal = new bootstrap.Modal(document.getElementById('bulkDeleteModal'));
        modal.show();

        const confirmBtn = document.getElementById('confirmDeleteBtn');
        const handleConfirm = function() {
            // Remove any stale selected_ids and action before submitting
            mainForm.querySelectorAll('input[name="selected_ids"], input[name="action"]').forEach(function(el) { el.remove(); });
            selectedCheckboxes.forEach(function(checkbox) {
                var hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'selected_ids';
                hidden.value = checkbox.value;
                mainForm.appendChild(hidden);
            });
            // type="button" doesn't submit with form.submit(), so add action as hidden field
            var actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = button.value;
            mainForm.appendChild(actionInput);
            modal.hide();
            confirmBtn.removeEventListener('click', handleConfirm);
            var originalAction = mainForm.getAttribute('action');
            mainForm.setAttribute('action', button.getAttribute('formaction') || originalAction);
            mainForm.submit();
            mainForm.setAttribute('action', originalAction);
        };
        confirmBtn.addEventListener('click', handleConfirm);

        document.getElementById('bulkDeleteModal').addEventListener('hidden.bs.modal', function() {
            confirmBtn.removeEventListener('click', handleConfirm);
        });

        return false;
    }

    window.confirmBulkDelete = confirmBulkDelete;

    function confirmSingleDelete(deleteUrl) {
        const modal = new bootstrap.Modal(document.getElementById('singleDeleteModal'));
        modal.show();
        const confirmBtn = document.getElementById('confirmSingleDeleteBtn');
        const handleConfirm = function() {
            modal.hide();
            confirmBtn.removeEventListener('click', handleConfirm);
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = deleteUrl;
            document.body.appendChild(form);
            form.submit();
        };
        confirmBtn.addEventListener('click', handleConfirm);
        document.getElementById('singleDeleteModal').addEventListener('hidden.bs.modal', function() {
            confirmBtn.removeEventListener('click', handleConfirm);
        });
        return false;
    }

    window.confirmSingleDelete = confirmSingleDelete;

    // 为所有删除按钮添加事件监听
    document.querySelectorAll('.delete-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const deleteUrl = this.getAttribute('data-delete-url');
            if (deleteUrl) {
                confirmSingleDelete(deleteUrl);
            }
        });
    });

    // ====== 股票名称搜索功能 ======
    const stockCodeInput = document.getElementById('stock_code_input');
    const stockNameInput = document.getElementById('stock_name_input');
    const stockSearchResults = document.getElementById('stock_search_results');
    const tradePriceInput = document.getElementById('trade_price');

    // 防抖函数
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 根据名称搜索股票
    async function searchStockByName() {
        const name = stockNameInput ? stockNameInput.value.trim() : '';
        if (!name || name.length < 2) {
            if (stockSearchResults) stockSearchResults.style.display = 'none';
            return;
        }

        try {
            const response = await fetch('/stock_search?name=' + encodeURIComponent(name));
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                // 显示搜索结果下拉框（格式：股票代码-股票名称）
                let html = '';
                data.results.forEach(function(item) {
                    html += `<a class="dropdown-item small py-1 px-2" href="#" data-code="${item.stock_code}" data-name="${item.stock_name}" style="line-height: 1.4;">
                        <span class="fw-bold text-primary">${item.stock_code}</span><span class="text-muted mx-1">-</span><span>${item.stock_name}</span>
                    </a>`;
                });
                
                if (stockSearchResults) {
                    stockSearchResults.innerHTML = html;
                    stockSearchResults.style.display = 'block';
                    
                    // 绑定点击事件
                    stockSearchResults.querySelectorAll('.dropdown-item').forEach(function(item) {
                        item.addEventListener('click', function(e) {
                            e.preventDefault();
                            const code = this.getAttribute('data-code');
                            const name = this.getAttribute('data-name');
                            
                            if (stockCodeInput) stockCodeInput.value = code;
                            if (stockNameInput) stockNameInput.value = name;
                            stockSearchResults.style.display = 'none';
                            
                            // 自动获取股票信息
                            fetchStockInfoByCode(code);
                        });
                    });
                }
            } else {
                if (stockSearchResults) stockSearchResults.style.display = 'none';
            }
        } catch (error) {
            console.warn('搜索股票失败:', error);
        }
    }

    // 根据代码获取股票信息（同时回填股票名称）
    async function fetchStockInfoByCode(stockCode) {
        if (!stockCode || stockCode.length !== 6) {
            return;
        }

        try {
            // 识别资产类型（股票还是基金）
            const identifyResponse = await fetch('/api/stock/identify?code=' + encodeURIComponent(stockCode));
            let assetType = 'stock';
            if (identifyResponse.ok) {
                const identifyData = await identifyResponse.json();
                if (identifyData.type === 'fund') {
                    assetType = 'fund';
                }
            }
            
            // 更新资产类型显示
            const assetTypeDisplay = document.getElementById('asset_type_display');
            const assetTypeInput = document.getElementById('asset_type_input');
            if (assetTypeDisplay) {
                assetTypeDisplay.value = assetType === 'fund' ? '基金' : '股票';
            }
            if (assetTypeInput) {
                assetTypeInput.value = assetType;
            }

            const response = await fetch('/stock_info?stock_code=' + encodeURIComponent(stockCode));
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            
            if (data && data.stock_name) {
                // 回填股票名称（如果名称输入框为空或用户刚输入代码）
                if (stockNameInput && !stockNameInput.value.trim()) {
                    stockNameInput.value = data.stock_name;
                }
                
                // 自动填充交易价格
                if (tradePriceInput && !tradePriceInput.value.trim()) {
                    const currentPrice = data.current_price || data.closing_price || data.opening_price || 0;
                    if (currentPrice > 0) {
                        tradePriceInput.value = currentPrice.toFixed(3);
                        tradePriceInput.classList.add('bg-light');
                        setTimeout(() => tradePriceInput.classList.remove('bg-light'), 1000);
                    }
                }
                
                showToast('已选择: ' + data.stock_name + ' (' + stockCode + ')', 'success');
            }
        } catch (error) {
            console.warn('获取股票信息失败:', error);
        }
    }

    // 监听股票名称输入
    if (stockNameInput) {
        stockNameInput.addEventListener('input', debounce(searchStockByName, 400));
        // 点击其他地方隐藏搜索结果
        document.addEventListener('click', function(e) {
            if (stockSearchResults && !stockNameInput.contains(e.target) && !stockSearchResults.contains(e.target)) {
                stockSearchResults.style.display = 'none';
            }
        });
    }

    // 监听股票代码输入（实时检测，6位数字时自动获取信息并回填名称）
    if (stockCodeInput) {
        stockCodeInput.addEventListener('input', debounce(function() {
            const code = stockCodeInput.value.trim();
            if (code.length === 6 && /^\d{6}$/.test(code)) {
                fetchStockInfoByCode(code);
            }
        }, 500));
        
        stockCodeInput.addEventListener('blur', function() {
            const code = stockCodeInput.value.trim();
            if (code.length === 6 && /^\d{6}$/.test(code)) {
                fetchStockInfoByCode(code);
            }
        });
    }

    // 页面加载时如果已有股票代码，自动获取
    if (stockCodeInput && stockCodeInput.value.trim()) {
        fetchStockInfoByCode(stockCodeInput.value.trim());
    }

    // ====== 券商佣金计算功能 ======
    const brokerSelect = document.getElementById('broker_select');
    const quantityInput = document.getElementById('quantity_input');
    const commissionRateInput = document.getElementById('commission_rate_input');
    const commissionFeeInput = document.getElementById('commission_fee_input');
    const brokerConfigHint = document.getElementById('broker_config_hint');
    const tradeTypeSelect = document.getElementById('trade_type_input'); // 交易类型下拉框
    const profitLossDisplay = document.getElementById('profit_loss_display'); // 盈亏显示区域

    // 动态加载券商列表
    let brokerConfig = {};

    async function loadBrokers() {
        try {
            const response = await fetch('/api/brokers');
            if (!response.ok) throw new Error('获取券商列表失败');
            
            const data = await response.json();
            if (data.brokers && Array.isArray(data.brokers)) {
                // 清空现有选项（保留"请选择"和"自定义佣金"）
                brokerSelect.innerHTML = '<option value="">请选择券商</option><option value="custom">自定义佣金</option>';
                
                // 添加从API获取的券商
                data.brokers.forEach(function(broker) {
                    const option = document.createElement('option');
                    option.value = broker.id;
                    option.textContent = broker.name + ' (' + broker.description + ')';
                    brokerSelect.appendChild(option);
                    
                    // 保存券商配置到内存
                    brokerConfig[broker.id] = {
                        rate: broker.rate,
                        minFee: broker.min_fee,
                        name: broker.name
                    };
                });
                
                // 显示配置文件路径提示
                if (brokerConfigHint) {
                    brokerConfigHint.textContent = '(配置: ' + data.config_file + ')';
                }
            }
        } catch (error) {
            console.warn('加载券商列表失败:', error);
            showToast('加载券商列表失败，使用默认配置', 'warning');
        }
    }

    // 页面加载时获取券商列表
    loadBrokers();

    function calculateCommission() {
        const broker = brokerSelect ? brokerSelect.value : '';
        const quantity = parseInt(quantityInput ? quantityInput.value : '0', 10);
        const price = parseFloat(tradePriceInput ? tradePriceInput.value : '0');
        
        if (quantity <= 0 || price <= 0) {
            if (commissionFeeInput) commissionFeeInput.value = '0.000';
            return;
        }

        let rate = 0;
        let minFee = 5;
        
        if (broker && broker !== 'custom' && brokerConfig[broker]) {
            rate = brokerConfig[broker].rate;
            minFee = brokerConfig[broker].minFee;
        } else if (broker === 'custom') {
            // 自定义佣金
            const customRate = parseFloat(commissionRateInput ? commissionRateInput.value : '0');
            if (customRate > 0) {
                rate = customRate;
            }
            minFee = 1; // 自定义最低佣金为1元
        }

        if (rate <= 0) {
            return;
        }

        const amount = quantity * price;  // 成交金额
        const commission = amount * (rate / 10000);  // 佣金 = 成交金额 × (佣金比例/10000)
        const finalFee = Math.max(commission, minFee);  // 取较高值
        
        if (commissionFeeInput) {
            commissionFeeInput.value = finalFee.toFixed(3);
        }
    }

    // 绑定事件
    if (brokerSelect) {
        brokerSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                // 显示佣金比例输入框
                if (commissionRateInput) {
                    commissionRateInput.removeAttribute('readonly');
                    commissionRateInput.placeholder = '请输入万分之一佣金，如: 1.5';
                }
            } else {
                // 隐藏佣金比例输入框
                if (commissionRateInput) {
                    commissionRateInput.setAttribute('readonly', 'true');
                    commissionRateInput.value = '';
                }
            }
            calculateCommission();
        });
    }

    if (quantityInput) {
        quantityInput.addEventListener('input', calculateCommission);
    }

    if (tradePriceInput) {
        tradePriceInput.addEventListener('input', calculateCommission);
    }

    if (commissionRateInput) {
        commissionRateInput.addEventListener('input', calculateCommission);
    }

    // 页面加载时初始化佣金比例输入框状态
    if (brokerSelect && brokerSelect.value === 'custom') {
        if (commissionRateInput) commissionRateInput.removeAttribute('readonly');
    } else {
        if (commissionRateInput) commissionRateInput.setAttribute('readonly', 'true');
    }

    // ====== 实时盈亏计算功能 ======
    let currentPosition = null;

    async function loadCurrentPosition() {
        if (!stockCodeInput) return null;
        const stockCode = stockCodeInput.value.trim();
        if (!stockCode || stockCode.length !== 6) {
            currentPosition = null;
            return null;
        }

        try {
            const response = await fetch('/api/position/pnl?stock_code=' + encodeURIComponent(stockCode));
            if (!response.ok) {
                currentPosition = null;
                return null;
            }
            const data = await response.json();
            
            if (data.positions && data.positions.length > 0) {
                const buyPositions = data.positions.filter(p => p.trade_type === 'buy');
                if (buyPositions.length > 0) {
                    const totalQuantity = buyPositions.reduce((sum, p) => sum + p.quantity, 0);
                    const totalCost = buyPositions.reduce((sum, p) => sum + (p.cost_price || 0) * p.quantity, 0);
                    const avgCost = totalCost / totalQuantity;
                    
                    const sellPositions = data.positions.filter(p => p.trade_type === 'sell');
                    const soldQuantity = sellPositions.reduce((sum, p) => sum + p.quantity, 0);
                    
                    currentPosition = {
                        avgCost: avgCost,
                        totalQuantity: totalQuantity,
                        soldQuantity: soldQuantity,
                        remainingQuantity: totalQuantity - soldQuantity
                    };
                    return currentPosition;
                }
            }
            
            currentPosition = null;
            return null;
        } catch (error) {
            console.warn('加载持仓信息失败:', error);
            currentPosition = null;
            return null;
        }
    }

    async function calculateProfitLoss() {
        const profitLossDisplay = document.getElementById('profit_loss_display');
        if (!profitLossDisplay) return;
        
        const tradeType = tradeTypeSelect ? tradeTypeSelect.value : '';
        const quantity = parseInt(quantityInput ? quantityInput.value : '0', 10);
        const price = parseFloat(tradePriceInput ? tradePriceInput.value : '0');
        
        if (tradeType !== 'sell') {
            profitLossDisplay.innerHTML = '<span class="text-muted">仅卖出时可计算盈亏</span>';
            return;
        }
        
        if (quantity <= 0 || price <= 0) {
            profitLossDisplay.innerHTML = '<span class="text-muted">请输入卖出数量和价格</span>';
            return;
        }
        
        if (!currentPosition || currentPosition.remainingQuantity <= 0) {
            profitLossDisplay.innerHTML = '<span class="text-warning">该股票暂无持仓</span>';
            return;
        }
        
        const costPrice = currentPosition.avgCost;
        const profitLoss = (price - costPrice) * quantity;
        const profitLossRate = costPrice > 0 ? (profitLoss / (costPrice * quantity) * 100) : 0;
        
        const isProfit = profitLoss >= 0;
        const pnlClass = isProfit ? 'text-danger' : 'text-success';
        const pnlSign = isProfit ? '+' : '';
        
        profitLossDisplay.innerHTML = '<div class="d-flex align-items-center gap-3"><div><small class="text-muted">成本价</small><div class="fw-bold">' + costPrice.toFixed(3) + '</div></div><div><small class="text-muted">卖出数量</small><div class="fw-bold">' + quantity + '</div></div><div><small class="text-muted">盈亏金额</small><div class="fw-bold ' + pnlClass + '">' + pnlSign + '¥' + profitLoss.toFixed(2) + '</div></div><div><small class="text-muted">盈亏比例</small><div class="fw-bold ' + pnlClass + '">' + pnlSign + profitLossRate.toFixed(2) + '%</div></div></div>';
    }

    if (stockCodeInput) {
        stockCodeInput.addEventListener('input', debounce(async function() {
            const code = stockCodeInput.value.trim();
            if (code.length === 6 && /^\d{6}$/.test(code)) {
                await loadCurrentPosition();
                calculateProfitLoss();
            } else {
                currentPosition = null;
                const profitLossDisplay = document.getElementById('profit_loss_display');
                if (profitLossDisplay) profitLossDisplay.innerHTML = '<span class="text-muted">请先选择股票</span>';
            }
        }, 500));
        
        stockCodeInput.addEventListener('blur', debounce(async function() {
            const code = stockCodeInput.value.trim();
            if (code.length === 6 && /^\d{6}$/.test(code)) {
                await loadCurrentPosition();
                calculateProfitLoss();
            }
        }, 200));
    }

    if (stockSearchResults) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.classList && node.classList.contains('dropdown-item')) {
                            node.addEventListener('click', async function() {
                                setTimeout(async function() {
                                    await loadCurrentPosition();
                                    calculateProfitLoss();
                                }, 300);
                            });
                        }
                    });
                }
            });
        });
        observer.observe(stockSearchResults, { childList: true });
    }

    if (tradeTypeSelect) {
        tradeTypeSelect.addEventListener('change', function() {
            loadCurrentPosition().then(function() {
                calculateProfitLoss();
            });
        });
    }

    if (quantityInput) {
        quantityInput.addEventListener('input', calculateProfitLoss);
    }

    if (tradePriceInput) {
        tradePriceInput.addEventListener('input', calculateProfitLoss);
    }

    loadCurrentPosition().then(function() {
        calculateProfitLoss();
    });

    // ====== 辅助函数 ======
    // 计算移动平均线
    function calculateMA(dayCount, data) {
        const result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < dayCount - 1) {
                result.push('-');
                continue;
            }
            let sum = 0;
            for (let j = 0; j < dayCount; j++) {
                sum += parseFloat(data[i - j]);
            }
            result.push((sum / dayCount).toFixed(3));
        }
        return result;
    }

    // ====== 股票图表功能（使用第三方股票图片） ======
    const chartContainer = document.getElementById('stock_chart_container');
    const imgContainer = document.getElementById('stock_iframe_container');
    let currentStockCode = null;

    async function loadStockChart(stockCode) {
        if (!stockCode || stockCode.length !== 6) {
            if (chartContainer) chartContainer.style.display = 'none';
            return;
        }

        currentStockCode = stockCode;
        if (chartContainer) chartContainer.style.display = 'block';

        try {
            // 获取实时行情
            const realtimeResponse = await fetch('/api/stock/realtime?code=' + encodeURIComponent(stockCode));
            let realtimeData = null;
            if (realtimeResponse.ok) {
                realtimeData = await realtimeResponse.json();
            }

            // 检查股票代码是否已更改
            if (currentStockCode !== stockCode) {
                return;
            }

            // 更新股票信息显示
            if (realtimeData && !realtimeData.error) {
                document.getElementById('stock_chart_name').textContent = realtimeData.name || stockCode;
                document.getElementById('stock_chart_code').textContent = realtimeData.code || stockCode;
                document.getElementById('stock_chart_price').textContent = realtimeData.current ? realtimeData.current.toFixed(3) : '--';

                const changePct = realtimeData.change_pct || 0;
                const changeEl = document.getElementById('stock_chart_change');
                changeEl.textContent = (changePct >= 0 ? '+' : '') + changePct.toFixed(2) + '%';
                changeEl.className = 'badge ' + (changePct >= 0 ? 'bg-danger' : 'bg-success');

                document.getElementById('stock_open').textContent = realtimeData.open ? realtimeData.open.toFixed(3) : '--';
                document.getElementById('stock_high').textContent = realtimeData.high ? realtimeData.high.toFixed(3) : '--';
                document.getElementById('stock_low').textContent = realtimeData.low ? realtimeData.low.toFixed(3) : '--';
                document.getElementById('stock_volume').textContent = realtimeData.volume ? realtimeData.volume.toLocaleString() : '--';
            }

            // 使用新浪财经股票图片
            if (imgContainer) {
                // 判断是沪市还是深市
                let sinaCode;
                if (stockCode.startsWith('6') || stockCode.startsWith('9')) {
                    sinaCode = 'sh' + stockCode;
                } else {
                    sinaCode = 'sz' + stockCode;
                }
                
                // 新浪财经分时图图片
                const minuteImgUrl = `https://image.sinajs.cn/newchart/min/n/${sinaCode}.gif?v=${Date.now()}`;
                
                // 新浪财经日K线图图片
                const dailyImgUrl = `https://image.sinajs.cn/newchart/daily/n/${sinaCode}.gif?v=${Date.now()}`;
                
                // 创建包含两张图片的布局
                imgContainer.innerHTML = `
                    <div class="stock-charts-wrapper">
                        <div class="stock-chart-item">
                            <div class="chart-label">分时图</div>
                            <img src="${minuteImgUrl}" alt="分时图" class="stock-chart-img" onerror="this.style.display='none'" />
                        </div>
                        <div class="stock-chart-item">
                            <div class="chart-label">日K线</div>
                            <img src="${dailyImgUrl}" alt="日K线" class="stock-chart-img" onerror="this.style.display='none'" />
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.warn('加载股票图表失败:', error);
        }
    }

    // 监听股票代码输入
    if (stockCodeInput) {
        stockCodeInput.addEventListener('input', debounce(function() {
            const code = stockCodeInput.value.trim();
            if (code.length === 6 && /^\d{6}$/.test(code)) {
                loadStockChart(code);
            } else {
                if (chartContainer) chartContainer.style.display = 'none';
                currentStockCode = null;
            }
        }, 600));

        stockCodeInput.addEventListener('blur', function() {
            const code = stockCodeInput.value.trim();
            if (code.length === 6 && /^\d{6}$/.test(code)) {
                loadStockChart(code);
            }
        });
    }

    // 监听从搜索结果选择的股票
    if (stockSearchResults) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.classList && node.classList.contains('dropdown-item')) {
                            node.addEventListener('click', function() {
                                const code = this.getAttribute('data-code');
                                if (code) {
                                    setTimeout(function() {
                                        loadStockChart(code);
                                    }, 100);
                                }
                            });
                        }
                    });
                }
            });
        });

        observer.observe(stockSearchResults, { childList: true });
    }

    // 页面加载时如果已有股票代码，加载图表
    if (stockCodeInput && stockCodeInput.value.trim()) {
        const code = stockCodeInput.value.trim();
        if (code.length === 6 && /^\d{6}$/.test(code)) {
            loadStockChart(code);
        }
    }

    // ====== 加载总体盈亏数据 ======
    async function loadPortfolioSummary() {
        try {
            const response = await fetch('/api/portfolio/summary');
            if (!response.ok) return;
            
            const data = await response.json();
            
            const totalAssets = data.total_assets || 0;
            const totalPnl = data.total_pnl || 0;
            const totalCost = data.total_cost || 0;
            const pnlRate = data.pnl_rate || 0;
            
            document.getElementById('total_assets').textContent = '¥' + totalAssets.toFixed(2);
            document.getElementById('total_cost').textContent = '¥' + totalCost.toFixed(2);
            
            const pnlEl = document.getElementById('total_pnl');
            const pnlCard = document.getElementById('pnl_card');
            const pnlSign = totalPnl >= 0 ? '+' : '';
            pnlEl.textContent = pnlSign + '¥' + totalPnl.toFixed(2);
            pnlEl.className = 'fs-5 fw-bold ' + (totalPnl >= 0 ? 'text-danger' : 'text-success');
            if (pnlCard) {
                pnlCard.className = 'card ' + (totalPnl >= 0 ? 'border-danger' : 'border-success');
            }
            
            const rateEl = document.getElementById('total_pnl_rate');
            rateEl.textContent = pnlSign + pnlRate.toFixed(2) + '%';
            rateEl.className = 'fs-5 fw-bold ' + (totalPnl >= 0 ? 'text-danger' : 'text-success');
        } catch (error) {
            console.warn('加载总体盈亏失败:', error);
        }
    }

    // 页面加载时获取总体盈亏
    loadPortfolioSummary();

    // ====== 盈亏按钮点击显示详情 ======
    document.querySelectorAll('.pnl-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const stockCode = this.getAttribute('data-stock-code');
            const stockName = this.getAttribute('data-stock-name');
            
            if (!stockCode || stockCode.length !== 6) {
                showToast('无效的股票代码', 'warning');
                return;
            }
            
            showStockDetailModal(stockCode, stockName);
        });
    });

    // 显示股票详情模态框
    async function showStockDetailModal(stockCode, stockName) {
        const modal = new bootstrap.Modal(document.getElementById('stockDetailModal'));
        
        // 设置基本信息
        document.getElementById('modal_stock_name').textContent = stockName || stockCode;
        document.getElementById('modal_stock_code').textContent = stockCode;
        
        // 显示模态框
        modal.show();
        
        // 清空之前的数据
        document.getElementById('modal_position_table').innerHTML = '<tr><td colspan="7" class="text-center text-muted">加载中...</td></tr>';
        document.getElementById('modal_total_pnl').textContent = '--';
        document.getElementById('modal_total_pnl_rate').textContent = '--';
        
        // 加载股票图表
        await loadModalStockChart(stockCode);
        
        // 获取持仓盈亏数据
        await loadPositionData(stockCode);
    }

    // 加载模态框中的股票图表
    async function loadModalStockChart(stockCode) {
        const chartContainer = document.getElementById('modal_stock_chart');
        if (!chartContainer) return;
        
        chartContainer.innerHTML = '<div class="d-flex align-items-center justify-content-center h-100 text-muted">加载中...</div>';
        
        try {
            // 获取实时数据
            const realtimeResponse = await fetch('/api/stock/realtime?code=' + encodeURIComponent(stockCode));
            let realtimeData = null;
            if (realtimeResponse.ok) {
                realtimeData = await realtimeResponse.json();
            }
            
            // 更新行情信息
            if (realtimeData && !realtimeData.error) {
                document.getElementById('modal_stock_open').textContent = realtimeData.open ? realtimeData.open.toFixed(3) : '--';
                document.getElementById('modal_stock_high').textContent = realtimeData.high ? realtimeData.high.toFixed(3) : '--';
                document.getElementById('modal_stock_low').textContent = realtimeData.low ? realtimeData.low.toFixed(3) : '--';
                document.getElementById('modal_stock_volume').textContent = realtimeData.volume ? realtimeData.volume.toLocaleString() : '--';
            }
            
            // 生成股票图片
            let sinaCode;
            if (stockCode.startsWith('6') || stockCode.startsWith('9')) {
                sinaCode = 'sh' + stockCode;
            } else {
                sinaCode = 'sz' + stockCode;
            }
            
            const minuteImgUrl = `https://image.sinajs.cn/newchart/min/n/${sinaCode}.gif?v=${Date.now()}`;
            const dailyImgUrl = `https://image.sinajs.cn/newchart/daily/n/${sinaCode}.gif?v=${Date.now()}`;
            
            chartContainer.innerHTML = `
                <div class="stock-charts-wrapper" style="height: 100%;">
                    <div class="stock-chart-item">
                        <div class="chart-label">分时图</div>
                        <img src="${minuteImgUrl}" alt="分时图" class="stock-chart-img" style="height: calc(100% - 20px);" onerror="this.style.display='none'" />
                    </div>
                    <div class="stock-chart-item">
                        <div class="chart-label">日K线</div>
                        <img src="${dailyImgUrl}" alt="日K线" class="stock-chart-img" style="height: calc(100% - 20px);" onerror="this.style.display='none'" />
                    </div>
                </div>
            `;
        } catch (error) {
            chartContainer.innerHTML = '<div class="d-flex align-items-center justify-content-center h-100 text-muted">加载失败</div>';
            console.warn('加载股票图表失败:', error);
        }
    }

    // 加载持仓盈亏数据
    async function loadPositionData(stockCode) {
        const tbody = document.getElementById('modal_position_table');
        if (!tbody) return;
        
        try {
            const response = await fetch('/api/position/pnl?stock_code=' + encodeURIComponent(stockCode));
            if (!response.ok) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">加载失败</td></tr>';
                return;
            }
            
            const data = await response.json();
            
            if (!data.positions || data.positions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">暂无持仓数据</td></tr>';
                document.getElementById('modal_total_pnl').textContent = '--';
                document.getElementById('modal_total_pnl_rate').textContent = '--';
                return;
            }
            
            let html = '';
            let totalCost = 0;
            let totalPnL = 0;
            
            data.positions.forEach(function(pos) {
                const pnlClass = pos.pnl >= 0 ? 'text-danger' : 'text-success';
                const pnlSign = pos.pnl >= 0 ? '+' : '';
                
                html += '<tr>';
                html += '<td>' + pos.trade_time + '</td>';
                html += '<td>' + (pos.trade_type === 'buy' ? '买入' : '卖出') + '</td>';
                html += '<td class="text-end">' + pos.quantity + '</td>';
                html += '<td class="text-end">' + (pos.cost_price || 0).toFixed(3) + '</td>';
                html += '<td class="text-end">' + (pos.current_price || 0).toFixed(3) + '</td>';
                html += '<td class="text-end ' + pnlClass + '">' + pnlSign + (pos.pnl || 0).toFixed(2) + '</td>';
                html += '<td class="text-end ' + pnlClass + '">' + pnlSign + (pos.pnl_rate || 0).toFixed(2) + '%</td>';
                html += '</tr>';
                
                if (pos.trade_type === 'buy') {
                    totalCost += pos.cost_price * pos.quantity;
                    totalPnL += pos.pnl || 0;
                }
            });
            
            tbody.innerHTML = html;
            
            // 计算合计
            const avgCost = data.positions.filter(p => p.trade_type === 'buy').reduce((sum, p) => sum + p.cost_price * p.quantity, 0) /
                            data.positions.filter(p => p.trade_type === 'buy').reduce((sum, p) => sum + p.quantity, 0);
            const lastPrice = data.positions[0]?.current_price || 0;
            const totalPnLFinal = data.positions.filter(p => p.trade_type === 'buy').reduce((sum, p) => sum + (p.pnl || 0), 0);
            const pnlRate = avgCost > 0 ? ((lastPrice - avgCost) / avgCost * 100) : 0;
            
            const totalPnLClass = totalPnLFinal >= 0 ? 'text-danger' : 'text-success';
            const totalPnLSign = totalPnLFinal >= 0 ? '+' : '';
            
            document.getElementById('modal_total_pnl').className = 'text-end fw-bold ' + totalPnLClass;
            document.getElementById('modal_total_pnl').textContent = totalPnLSign + totalPnLFinal.toFixed(2);
            document.getElementById('modal_total_pnl_rate').className = 'text-end fw-bold ' + totalPnLClass;
            document.getElementById('modal_total_pnl_rate').textContent = totalPnLSign + pnlRate.toFixed(2) + '%';
            
        } catch (error) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">加载失败: ' + error.message + '</td></tr>';
            console.warn('加载持仓数据失败:', error);
        }
    }

    // ====== 卖出按钮事件 ======
    let currentSellStock = null;

    // 监听盈亏模态框中的卖出按钮
    document.getElementById('modal_sell_btn').addEventListener('click', function() {
        const stockCode = document.getElementById('modal_stock_code').textContent;
        const stockName = document.getElementById('modal_stock_name').textContent;
        
        // 获取持仓信息
        fetch('/api/position/pnl?stock_code=' + encodeURIComponent(stockCode))
            .then(response => response.json())
            .then(data => {
                if (data.position_qty > 0) {
                    currentSellStock = {
                        stock_code: stockCode,
                        stock_name: stockName,
                        position_qty: data.position_qty,
                        avg_cost: data.avg_cost,
                        current_price: data.current_price
                    };
                    
                    // 填充卖出表单
                    document.getElementById('sell_stock_code').value = stockCode;
                    document.getElementById('sell_stock_name').value = stockName;
                    document.getElementById('sell_price').value = data.current_price.toFixed(3);
                    document.getElementById('sell_available_qty').textContent = data.position_qty;
                    document.getElementById('sell_quantity').max = data.position_qty;
                    document.getElementById('sell_quantity').value = Math.min(100, data.position_qty);
                    
                    // 计算预估盈亏
                    calculateSellProfitLoss();
                    
                    // 显示卖出模态框
                    const sellModal = new bootstrap.Modal(document.getElementById('sellModal'));
                    sellModal.show();
                } else {
                    showToast('该股票没有持仓，无法卖出', 'warning');
                }
            });
    });

    // 加载券商到卖出表单
    async function loadSellBrokers() {
        try {
            const response = await fetch('/api/brokers');
            if (!response.ok) return;
            
            const data = await response.json();
            const sellBrokerSelect = document.getElementById('sell_broker');
            sellBrokerSelect.innerHTML = '<option value="">请选择券商</option>';
            
            if (Array.isArray(data)) {
                data.forEach(function(broker) {
                    const option = document.createElement('option');
                    option.value = broker.id;
                    option.textContent = broker.name + ' (' + broker.description + ')';
                    sellBrokerSelect.appendChild(option);
                    
                    brokerConfig[broker.id] = {
                        rate: broker.rate,
                        minFee: broker.min_fee,
                        name: broker.name
                    };
                });
            }
        } catch (error) {
            console.warn('加载券商失败:', error);
        }
    }
    loadSellBrokers();

    // 计算卖出预估盈亏
    function calculateSellProfitLoss() {
        const price = parseFloat(document.getElementById('sell_price').value) || 0;
        const quantity = parseInt(document.getElementById('sell_quantity').value) || 0;
        
        if (currentSellStock && price > 0 && quantity > 0) {
            const pnl = (price - currentSellStock.avg_cost) * quantity;
            const pnlRate = (pnl / (currentSellStock.avg_cost * quantity)) * 100;
            const pnlSign = pnl >= 0 ? '+' : '';
            const pnlClass = pnl >= 0 ? 'text-danger' : 'text-success';
            
            document.getElementById('sell_estimated_pnl').className = 'fw-bold ' + pnlClass;
            document.getElementById('sell_estimated_pnl').textContent = pnlSign + '¥' + pnl.toFixed(2) + ' (' + pnlSign + pnlRate.toFixed(2) + '%)';
        } else {
            document.getElementById('sell_estimated_pnl').textContent = '--';
        }
    }

    // 监听卖出表单变化
    document.getElementById('sell_quantity').addEventListener('input', function() {
        calculateSellProfitLoss();
        calculateSellCommission();
    });

    // 计算卖出佣金
    function calculateSellCommission() {
        const quantity = parseInt(document.getElementById('sell_quantity').value) || 0;
        const price = parseFloat(document.getElementById('sell_price').value) || 0;
        const broker = document.getElementById('sell_broker').value;
        
        if (quantity <= 0 || price <= 0) {
            document.getElementById('sell_commission_fee').value = '0.000';
            return;
        }

        let rate = 0;
        let minFee = 5;
        
        if (broker && brokerConfig[broker]) {
            rate = brokerConfig[broker].rate;
            minFee = brokerConfig[broker].minFee;
        }

        if (rate <= 0) {
            return;
        }

        const amount = quantity * price;
        const commission = amount * (rate / 10000);
        const finalFee = Math.max(commission, minFee);
        
        document.getElementById('sell_commission_fee').value = finalFee.toFixed(3);
    }

    document.getElementById('sell_broker').addEventListener('change', calculateSellCommission);

    // 监听卖出模态框关闭，重置表单
    document.getElementById('sellModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('sellForm').reset();
        document.getElementById('sell_commission_fee').value = '0.000';
        document.getElementById('sell_estimated_pnl').textContent = '--';
        currentSellStock = null;
    });

    // 卖出表单提交
    document.getElementById('sellForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!currentSellStock) {
            showToast('股票信息错误', 'danger');
            return;
        }

        const quantity = parseInt(document.getElementById('sell_quantity').value) || 0;
        if (quantity <= 0 || quantity > currentSellStock.position_qty) {
            showToast('卖出数量无效', 'danger');
            return;
        }

        const trade_price = parseFloat(document.getElementById('sell_price').value) || 0;
        const commission_fee = parseFloat(document.getElementById('sell_commission_fee').value) || 0;
        const trade_basis = document.getElementById('sell_basis').value.trim();

        if (!trade_basis) {
            showToast('请填写卖出依据', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/sell', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    stock_code: currentSellStock.stock_code,
                    stock_name: currentSellStock.stock_name,
                    quantity: quantity,
                    trade_price: trade_price,
                    commission_fee: commission_fee,
                    trade_basis: trade_basis
                })
            });

            const result = await response.json();
            
            if (result.success) {
                showToast('卖出成功', 'success');
                bootstrap.Modal.getInstance(document.getElementById('sellModal')).hide();
                
                // 刷新页面数据
                loadPortfolioSummary();
                loadPositionData(currentSellStock.stock_code);
            } else {
                showToast(result.message || '卖出失败', 'danger');
            }
        } catch (error) {
            showToast('卖出失败: ' + error.message, 'danger');
        }
    });
});
