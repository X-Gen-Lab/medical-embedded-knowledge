/**
 * GitHub Community Statistics Module
 * Fetches and displays repository statistics and contributor information from GitHub API
 */

// Configuration
const communityConfig = {
  repo: 'X-Gen-Lab/medical-embedded-knowledge',
  apiBase: 'https://api.github.com',
  cacheKeyPrefix: 'medical-embedded-community',
  cacheDuration: 3600000 // 1 hour in milliseconds
};

/**
 * Get cached data from localStorage
 * @param {string} key - Cache key
 * @returns {*|null} Cached value or null if expired/not found
 */
function getCachedData(key) {
  try {
    const cached = localStorage.getItem(key);
    if (!cached) return null;
    
    const data = JSON.parse(cached);
    const now = Date.now();
    
    // Check if cache is expired
    if (now - data.timestamp > communityConfig.cacheDuration) {
      localStorage.removeItem(key);
      return null;
    }
    
    return data.value;
  } catch (error) {
    console.error('Failed to get cached data:', error);
    return null;
  }
}

/**
 * Cache data to localStorage
 * @param {string} key - Cache key
 * @param {*} value - Value to cache
 */
function setCachedData(key, value) {
  try {
    const data = {
      value,
      timestamp: Date.now()
    };
    localStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.error('Failed to cache data:', error);
  }
}

/**
 * Fetch GitHub repository statistics
 * @returns {Promise<Object|null>} Repository statistics or null on error
 */
async function fetchGitHubStats() {
  // Try to get from cache first
  const cached = getCachedData(`${communityConfig.cacheKeyPrefix}-stats`);
  if (cached) {
    return cached;
  }
  
  const apiUrl = `${communityConfig.apiBase}/repos/${communityConfig.repo}`;
  
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }
    
    const data = await response.json();
    const stats = {
      stars: data.stargazers_count,
      forks: data.forks_count,
      watchers: data.subscribers_count,
      openIssues: data.open_issues_count,
      lastUpdate: data.updated_at,
      language: data.language,
      size: data.size
    };
    
    // Cache the data
    setCachedData(`${communityConfig.cacheKeyPrefix}-stats`, stats);
    return stats;
  } catch (error) {
    console.error('Failed to fetch GitHub stats:', error);
    return null;
  }
}

/**
 * Fetch repository contributors
 * @returns {Promise<Array>} List of contributors
 */
async function fetchContributors() {
  // Try to get from cache first
  const cached = getCachedData(`${communityConfig.cacheKeyPrefix}-contributors`);
  if (cached) {
    return cached;
  }
  
  const apiUrl = `${communityConfig.apiBase}/repos/${communityConfig.repo}/contributors?per_page=12`;
  
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }
    
    const data = await response.json();
    const contributors = data.map(c => ({
      username: c.login,
      avatar: c.avatar_url,
      contributions: c.contributions,
      profile: c.html_url
    }));
    
    // Cache the data
    setCachedData(`${communityConfig.cacheKeyPrefix}-contributors`, contributors);
    return contributors;
  } catch (error) {
    console.error('Failed to fetch contributors:', error);
    return [];
  }
}

/**
 * Format number with k suffix for thousands
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return num.toString();
}

/**
 * Format date as relative time
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted relative time
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return '今天';
  } else if (diffDays === 1) {
    return '昨天';
  } else if (diffDays < 7) {
    return `${diffDays} 天前`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks} 周前`;
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return `${months} 个月前`;
  } else {
    const years = Math.floor(diffDays / 365);
    return `${years} 年前`;
  }
}

/**
 * Create stat card HTML
 * @param {string} icon - Emoji icon
 * @param {string} value - Stat value
 * @param {string} label - Stat label
 * @returns {string} HTML string
 */
function createStatCard(icon, value, label) {
  return `
    <div class="stat-card">
      <div class="stat-icon">${icon}</div>
      <div class="stat-value">${value}</div>
      <div class="stat-label">${label}</div>
    </div>
  `;
}

/**
 * Create loading skeleton
 * @returns {string} HTML for loading skeleton
 */
function createLoadingSkeleton() {
  return `
    <div class="stats-loading">
      <div class="skeleton skeleton-text"></div>
      <div class="skeleton skeleton-text"></div>
      <div class="skeleton skeleton-text"></div>
    </div>
  `;
}

/**
 * Display community statistics
 */
async function displayCommunityStats() {
  const container = document.getElementById('community-stats-container');
  
  if (!container) {
    return;
  }
  
  // Display loading state
  container.innerHTML = createLoadingSkeleton();
  
  try {
    // Fetch stats and contributors in parallel
    const [stats, contributors] = await Promise.all([
      fetchGitHubStats(),
      fetchContributors()
    ]);
    
    if (!stats) {
      container.innerHTML = '<p>无法加载社区统计数据</p>';
      return;
    }
    
    // Build stats cards
    const statsHTML = `
      <div class="stats-grid">
        ${createStatCard('⭐', formatNumber(stats.stars), 'Stars')}
        ${createStatCard('🍴', formatNumber(stats.forks), 'Forks')}
        ${createStatCard('👥', contributors.length, '贡献者')}
        ${createStatCard('📝', formatNumber(stats.openIssues), 'Open Issues')}
      </div>
    `;
    
    // Build contributors list
    const contributorsHTML = contributors.length > 0 ? `
      <div class="contributors-section">
        <h3>🌟 贡献者</h3>
        <div class="contributors-list">
          ${contributors.slice(0, 12).map(c => `
            <a href="${c.profile}" target="_blank" rel="noopener" title="${c.username} (${c.contributions} 次贡献)">
              <img src="${c.avatar}" alt="${c.username}" class="contributor-avatar" loading="lazy">
            </a>
          `).join('')}
        </div>
        <p class="contributors-count">
          共有 <strong>${contributors.length}</strong> 位贡献者参与了本项目
        </p>
      </div>
    ` : '';
    
    // Build activity info
    const activityHTML = `
      <div class="activity-section">
        <h3>📊 项目活动</h3>
        <div class="activity-item">
          <span class="activity-icon">🔄</span>
          <div class="activity-content">
            <div class="activity-title">最后更新</div>
            <div class="activity-time">${formatDate(stats.lastUpdate)}</div>
          </div>
        </div>
        <div class="activity-item">
          <span class="activity-icon">💻</span>
          <div class="activity-content">
            <div class="activity-title">主要语言</div>
            <div class="activity-time">${stats.language || 'Markdown'}</div>
          </div>
        </div>
      </div>
    `;
    
    // Build call to action
    const ctaHTML = `
      <div class="community-cta">
        <h3>🚀 加入我们</h3>
        <p>
          欢迎参与医疗器械嵌入式软件知识体系的建设！无论是内容贡献、问题反馈还是功能建议，
          我们都非常欢迎您的参与。
        </p>
        <a href="https://github.com/${communityConfig.repo}" class="cta-button" target="_blank" rel="noopener">
          <span>⭐</span>
          <span>访问 GitHub 仓库</span>
        </a>
      </div>
    `;
    
    // Combine all content
    container.innerHTML = statsHTML + contributorsHTML + activityHTML + ctaHTML;
    
  } catch (error) {
    console.error('Failed to display community stats:', error);
    container.innerHTML = '<p>加载社区统计时出错，请稍后再试</p>';
  }
}

/**
 * Create community stats container
 * @returns {HTMLElement} Container element
 */
function createCommunityStatsContainer() {
  const container = document.createElement('div');
  container.className = 'community-stats';
  container.innerHTML = `
    <h2>🌐 社区统计</h2>
    <div id="community-stats-container">
      ${createLoadingSkeleton()}
    </div>
  `;
  return container;
}

/**
 * Insert community stats into homepage
 */
function insertCommunityStats() {
  // Only display on homepage
  const isHomePage = window.location.pathname.match(/\/(index\.html)?$/) || 
                     window.location.pathname.match(/\/zh\/(index\.html)?$/);
  
  if (!isHomePage) {
    return;
  }
  
  // Find insertion point (at the end of main content area)
  const mainContent = document.querySelector('.md-content__inner');
  
  if (!mainContent) {
    console.warn('Main content area not found');
    return;
  }
  
  // Check if stats already exist
  if (document.querySelector('.community-stats')) {
    return;
  }
  
  // Create and insert community stats container
  const statsContainer = createCommunityStatsContainer();
  mainContent.appendChild(statsContainer);
  
  // Load statistics data
  displayCommunityStats();
}

/**
 * Initialize community statistics
 */
function initCommunityStats() {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertCommunityStats);
  } else {
    insertCommunityStats();
  }
}

// Initialize
initCommunityStats();

// Handle Material for MkDocs instant navigation
document.addEventListener('DOMContentLoaded', () => {
  const observer = new MutationObserver(() => {
    const isHomePage = window.location.pathname.match(/\/(index\.html)?$/) || 
                       window.location.pathname.match(/\/zh\/(index\.html)?$/);
    const statsExists = document.querySelector('.community-stats');
    
    if (isHomePage && !statsExists) {
      insertCommunityStats();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});
