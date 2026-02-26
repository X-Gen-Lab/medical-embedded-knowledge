/**
 * Giscus 主题同步脚本 (Giscus Theme Synchronization Script)
 * 需求 19.3 - 确保评论区主题与网站主题切换同步
 * 
 * 功能：
 * - 监听 Material 主题切换事件
 * - 通过 postMessage API 同步 Giscus iframe 主题
 * - 支持亮色/暗色主题自动切换
 */

(function() {
  'use strict';

  /**
   * 获取当前主题配色方案
   * @returns {string} 'light' 或 'dark'
   */
  function getCurrentTheme() {
    const scheme = document.body.getAttribute('data-md-color-scheme');
    return scheme === 'slate' ? 'dark' : 'light';
  }

  /**
   * 向 Giscus iframe 发送主题更新消息
   * @param {string} theme - 主题名称 ('light' 或 'dark')
   */
  function updateGiscusTheme(theme) {
    const iframe = document.querySelector('iframe.giscus-frame');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(
        {
          giscus: {
            setConfig: {
              theme: theme
            }
          }
        },
        'https://giscus.app'
      );
      console.log(`Giscus theme updated to: ${theme}`);
    }
  }

  /**
   * 初始化主题同步
   */
  function initThemeSync() {
    // 等待 DOM 完全加载
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initThemeSync);
      return;
    }

    // 使用 MutationObserver 监听主题切换
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
          const theme = getCurrentTheme();
          // 延迟一小段时间确保 iframe 已加载
          setTimeout(function() {
            updateGiscusTheme(theme);
          }, 100);
        }
      });
    });

    // 开始观察 body 元素的属性变化
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['data-md-color-scheme']
    });

    // 初始化时设置一次主题（确保页面加载时主题正确）
    setTimeout(function() {
      const theme = getCurrentTheme();
      updateGiscusTheme(theme);
    }, 1000); // 等待 Giscus iframe 加载

    console.log('Giscus theme synchronization initialized');
  }

  // 启动主题同步
  initThemeSync();
})();
