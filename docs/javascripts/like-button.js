/**
 * 点赞按钮功能实现
 * Like Button Implementation
 * 
 * 需求 16.5, 16.6, 23.1, 23.2, 23.3 - 点赞功能和 LocalStorage 存储
 * 需求 16.7, 23.5, 23.8 - 状态恢复和防抖动
 */

// 防抖动计时器
let debounceTimer = null;

/**
 * 切换点赞状态（带防抖动）
 * Toggle like status with debounce
 */
function toggleLike() {
  // 防抖动：如果正在防抖动期间，忽略点击
  if (debounceTimer) {
    return;
  }
  
  const pageKey = 'like_' + window.location.pathname;
  const isLiked = localStorage.getItem(pageKey) === 'true';
  
  if (isLiked) {
    // 取消点赞
    localStorage.removeItem(pageKey);
    updateLikeButton(false);
  } else {
    // 点赞
    localStorage.setItem(pageKey, 'true');
    updateLikeButton(true);
    
    // 添加动画效果
    const button = document.getElementById('like-button');
    if (button) {
      button.classList.add('liked-animation');
      setTimeout(() => {
        button.classList.remove('liked-animation');
      }, 600);
    }
  }
  
  // 设置 300ms 的防抖动期
  debounceTimer = setTimeout(() => {
    debounceTimer = null;
  }, 300);
}

/**
 * 更新点赞按钮显示状态
 * Update like button display state
 * @param {boolean} isLiked - 是否已点赞
 */
function updateLikeButton(isLiked) {
  const icon = document.getElementById('like-icon');
  const text = document.getElementById('like-text');
  const button = document.getElementById('like-button');
  
  if (!icon || !text || !button) return;
  
  if (isLiked) {
    // 已点赞状态 - 实心心形图标
    icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.27 2 8.5 2 5.41 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.08C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.41 22 8.5c0 3.77-3.4 6.86-8.55 11.53L12 21.35z"/></svg>';
    text.textContent = '已点赞';
    button.classList.add('liked');
  } else {
    // 未点赞状态 - 空心心形图标
    icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12.1 18.55l-.1.1-.11-.1C7.14 14.24 4 11.39 4 8.5 4 6.5 5.5 5 7.5 5c1.54 0 3.04 1 3.57 2.36h1.86C13.46 6 14.96 5 16.5 5c2 0 3.5 1.5 3.5 3.5 0 2.89-3.14 5.74-7.9 10.05M16.5 3c-1.74 0-3.41.81-4.5 2.08C10.91 3.81 9.24 3 7.5 3 4.42 3 2 5.41 2 8.5c0 3.77 3.4 6.86 8.55 11.53L12 21.35l1.45-1.32C18.6 15.36 22 12.27 22 8.5 22 5.41 19.58 3 16.5 3z"/></svg>';
    text.textContent = '内容有用';
    button.classList.remove('liked');
  }
}

/**
 * 页面加载时恢复点赞状态
 * Restore like status on page load
 * 需求 23.5 - 页面加载时检查 LocalStorage 并恢复点赞状态
 */
document.addEventListener('DOMContentLoaded', function() {
  const pageKey = 'like_' + window.location.pathname;
  const isLiked = localStorage.getItem(pageKey) === 'true';
  updateLikeButton(isLiked);
});
