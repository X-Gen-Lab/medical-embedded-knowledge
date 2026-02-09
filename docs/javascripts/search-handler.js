/**
 * 自定义搜索结果处理脚本
 * Custom Search Results Handler
 * 
 * 功能 (Features):
 * - 处理搜索无结果情况 (Handle no search results)
 * - 显示搜索建议 (Show search suggestions)
 * - 提供热门搜索词 (Provide popular search terms)
 * - 提供分类浏览链接 (Provide category browsing links)
 * 
 * 需求 (Requirements): 6.2
 */

document.addEventListener('DOMContentLoaded', function() {
    // 热门搜索词列表
    const popularSearches = [
        { term: 'RTOS', url: '/technical-knowledge/rtos/' },
        { term: 'IEC 62304', url: '/regulatory-standards/iec-62304/' },
        { term: 'MISRA C', url: '/software-engineering/coding-standards/' },
        { term: '风险管理', url: '/regulatory-standards/iso-14971/' },
        { term: 'I2C', url: '/technical-knowledge/hardware-interfaces/' },
        { term: '测试策略', url: '/software-engineering/testing-strategy/' }
    ];

    // 分类浏览链接
    const categoryLinks = [
        { name: '核心技术知识', url: '/technical-knowledge/' },
        { name: '法规与标准', url: '/regulatory-standards/' },
        { name: '软件工程实践', url: '/software-engineering/' },
        { name: '学习路径', url: '/learning-paths/' },
        { name: '实践案例', url: '/case-studies/' }
    ];

    // 监听搜索事件
    const searchInput = document.querySelector('[data-md-component="search-query"]');
    if (searchInput) {
        // 使用 MutationObserver 监听搜索结果容器的变化
        const searchResults = document.querySelector('[data-md-component="search-result"]');
        if (searchResults) {
            const observer = new MutationObserver(function(mutations) {
                handleSearchResults();
            });

            observer.observe(searchResults, {
                childList: true,
                subtree: true
            });
        }
    }

    /**
     * 处理搜索结果
     * Handle search results
     */
    function handleSearchResults() {
        const resultsContainer = document.querySelector('[data-md-component="search-result"]');
        if (!resultsContainer) return;

        // 检查是否有搜索结果
        const resultItems = resultsContainer.querySelectorAll('.md-search-result__item');
        const noResultsMessage = resultsContainer.querySelector('.md-search-result__meta');

        // 如果显示"未找到结果"消息
        if (noResultsMessage && noResultsMessage.textContent.includes('0')) {
            // 获取当前搜索词
            const searchQuery = document.querySelector('[data-md-component="search-query"]')?.value || '';
            
            // 创建自定义无结果内容
            const customContent = createNoResultsContent(searchQuery);
            
            // 插入自定义内容
            if (!resultsContainer.querySelector('.custom-no-results')) {
                resultsContainer.appendChild(customContent);
            }
        } else {
            // 如果有结果，移除自定义无结果内容
            const customNoResults = resultsContainer.querySelector('.custom-no-results');
            if (customNoResults) {
                customNoResults.remove();
            }
        }
    }

    /**
     * 创建无结果内容
     * Create no results content
     * 
     * @param {string} query - 搜索关键词
     * @returns {HTMLElement} - 无结果内容元素
     */
    function createNoResultsContent(query) {
        const container = document.createElement('div');
        container.className = 'custom-no-results';
        container.style.cssText = 'padding: 1rem; margin-top: 1rem; border-top: 1px solid var(--md-default-fg-color--lightest);';

        // 标题
        const title = document.createElement('h3');
        title.textContent = `未找到与"${query}"相关的结果`;
        title.style.cssText = 'font-size: 1.2rem; margin-bottom: 1rem; color: var(--md-default-fg-color);';
        container.appendChild(title);

        // 搜索建议
        const suggestionsTitle = document.createElement('p');
        suggestionsTitle.innerHTML = '<strong>搜索建议：</strong>';
        suggestionsTitle.style.cssText = 'margin-bottom: 0.5rem;';
        container.appendChild(suggestionsTitle);

        const suggestionsList = document.createElement('ul');
        suggestionsList.style.cssText = 'margin-left: 1.5rem; margin-bottom: 1rem;';
        const suggestions = [
            '检查关键词拼写是否正确',
            '尝试使用更通用的关键词',
            '使用同义词或相关术语',
            '尝试使用中英文切换搜索'
        ];
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsList.appendChild(li);
        });
        container.appendChild(suggestionsList);

        // 热门搜索
        const popularTitle = document.createElement('h4');
        popularTitle.textContent = '热门搜索';
        popularTitle.style.cssText = 'font-size: 1rem; margin-top: 1.5rem; margin-bottom: 0.5rem;';
        container.appendChild(popularTitle);

        const popularList = document.createElement('ul');
        popularList.style.cssText = 'margin-left: 1.5rem; margin-bottom: 1rem;';
        popularSearches.forEach(item => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = item.url;
            link.textContent = item.term;
            link.style.cssText = 'color: var(--md-primary-fg-color); text-decoration: none;';
            link.addEventListener('mouseenter', function() {
                this.style.textDecoration = 'underline';
            });
            link.addEventListener('mouseleave', function() {
                this.style.textDecoration = 'none';
            });
            li.appendChild(link);
            popularList.appendChild(li);
        });
        container.appendChild(popularList);

        // 分类浏览
        const categoryTitle = document.createElement('h4');
        categoryTitle.textContent = '按分类浏览';
        categoryTitle.style.cssText = 'font-size: 1rem; margin-top: 1.5rem; margin-bottom: 0.5rem;';
        container.appendChild(categoryTitle);

        const categoryList = document.createElement('ul');
        categoryList.style.cssText = 'margin-left: 1.5rem;';
        categoryLinks.forEach(item => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = item.url;
            link.textContent = item.name;
            link.style.cssText = 'color: var(--md-primary-fg-color); text-decoration: none;';
            link.addEventListener('mouseenter', function() {
                this.style.textDecoration = 'underline';
            });
            link.addEventListener('mouseleave', function() {
                this.style.textDecoration = 'none';
            });
            li.appendChild(link);
            categoryList.appendChild(li);
        });
        container.appendChild(categoryList);

        return container;
    }
});
