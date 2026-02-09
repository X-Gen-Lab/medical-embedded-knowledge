#!/usr/bin/env python3
"""
学习路径渲染脚本
Learning Path Rendering Script

此脚本用于解析YAML格式的学习路径配置文件，并生成Markdown格式的学习路径页面。
This script parses YAML learning path configuration files and generates Markdown learning path pages.

用法 / Usage:
    python scripts/render_learning_paths.py
    python scripts/render_learning_paths.py --validate path.yaml
    python scripts/render_learning_paths.py --path path.yaml --output output.md
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class LearningPathRenderer:
    """学习路径渲染器"""
    
    def __init__(self, docs_dir: str = "docs"):
        """
        初始化渲染器
        
        Args:
            docs_dir: 文档根目录路径
        """
        self.docs_dir = Path(docs_dir)
        self.learning_paths_dir = self.docs_dir / "learning-paths"
        
    def load_config(self, config_path: Path) -> Dict[str, Any]:
        """
        加载YAML配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML格式错误
        """
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def validate_config(self, config: Dict[str, Any], skip_file_check: bool = False) -> List[str]:
        """
        验证配置文件的有效性
        
        Args:
            config: 配置字典
            skip_file_check: 是否跳过文件存在性检查
            
        Returns:
            错误列表，如果为空则验证通过
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['path_id', 'title', 'description', 'estimated_total_time', 
                          'difficulty', 'target_role', 'stages']
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查难度级别
        if 'difficulty' in config:
            valid_difficulties = ['基础', '中级', '高级']
            if config['difficulty'] not in valid_difficulties:
                errors.append(f"无效的难度级别: {config['difficulty']}")
        
        # 检查阶段配置
        if 'stages' in config:
            if not isinstance(config['stages'], list) or len(config['stages']) == 0:
                errors.append("stages必须是非空列表")
            else:
                for i, stage in enumerate(config['stages'], 1):
                    if 'stage' not in stage:
                        errors.append(f"阶段{i}缺少stage字段")
                    elif stage['stage'] != i:
                        errors.append(f"阶段编号不连续: 期望{i}, 实际{stage['stage']}")
                    
                    if 'title' not in stage:
                        errors.append(f"阶段{i}缺少title字段")
                    
                    if 'modules' not in stage:
                        errors.append(f"阶段{i}缺少modules字段")
                    elif not isinstance(stage['modules'], list):
                        errors.append(f"阶段{i}的modules必须是列表")
                    else:
                        for j, module in enumerate(stage['modules'], 1):
                            if 'id' not in module:
                                errors.append(f"阶段{i}模块{j}缺少id字段")
                            elif not skip_file_check and not self._module_exists(module['id']):
                                errors.append(f"阶段{i}模块{j}指向不存在的文件: {module['id']}")
                            
                            if 'required' not in module:
                                errors.append(f"阶段{i}模块{j}缺少required字段")
        
        # 检查检查点配置
        if 'checkpoints' in config:
            if not isinstance(config['checkpoints'], list):
                errors.append("checkpoints必须是列表")
            else:
                for i, checkpoint in enumerate(config['checkpoints'], 1):
                    if 'after_stage' not in checkpoint:
                        errors.append(f"检查点{i}缺少after_stage字段")
                    if 'assessment' not in checkpoint:
                        errors.append(f"检查点{i}缺少assessment字段")
        
        return errors
    
    def _module_exists(self, module_id: str) -> bool:
        """
        检查模块文件是否存在
        
        Args:
            module_id: 模块ID（相对路径，不含.md扩展名）
            
        Returns:
            文件是否存在
        """
        module_path = self.docs_dir / f"{module_id}.md"
        return module_path.exists()
    
    def render_markdown(self, config: Dict[str, Any]) -> str:
        """
        将配置渲染为Markdown格式
        
        Args:
            config: 配置字典
            
        Returns:
            Markdown文本
        """
        md = []
        
        # Front Matter
        md.append("---")
        md.append(f"title: \"{config['title']}\"")
        if 'title_en' in config:
            md.append(f"title_en: \"{config['title_en']}\"")
        md.append(f"description: \"{config['description']}\"")
        md.append(f"path_id: \"{config['path_id']}\"")
        md.append(f"difficulty: \"{config['difficulty']}\"")
        md.append(f"estimated_total_time: \"{config['estimated_total_time']}\"")
        md.append(f"target_role: \"{config['target_role']}\"")
        md.append("---")
        md.append("")
        
        # 标题
        md.append(f"# {config['title']}")
        md.append("")
        
        # 描述
        md.append("## 概述")
        md.append("")
        md.append(config['description'])
        md.append("")
        
        # 基本信息
        md.append("## 基本信息")
        md.append("")
        md.append(f"- **目标角色**: {config['target_role']}")
        md.append(f"- **难度级别**: {config['difficulty']}")
        md.append(f"- **预计总学习时间**: {config['estimated_total_time']}")
        md.append("")
        
        # 前置要求
        if 'prerequisites' in config and config['prerequisites']:
            md.append("## 前置要求")
            md.append("")
            for prereq in config['prerequisites']:
                md.append(f"- {prereq}")
            md.append("")
        
        # 学习目标
        if 'learning_objectives' in config and config['learning_objectives']:
            md.append("## 学习目标")
            md.append("")
            md.append("完成本学习路径后，你将能够：")
            md.append("")
            for objective in config['learning_objectives']:
                md.append(f"- {objective}")
            md.append("")
        
        # 学习阶段
        md.append("## 学习阶段")
        md.append("")
        
        for stage in config['stages']:
            stage_num = stage['stage']
            stage_title = stage['title']
            stage_desc = stage.get('description', '')
            stage_time = stage.get('estimated_time', '')
            
            md.append(f"### 阶段 {stage_num}: {stage_title}")
            md.append("")
            
            if stage_desc:
                md.append(f"**描述**: {stage_desc}")
                md.append("")
            
            if stage_time:
                md.append(f"**预计学习时间**: {stage_time}")
                md.append("")
            
            # 模块列表
            md.append("#### 知识模块")
            md.append("")
            
            for module in stage['modules']:
                module_id = module['id']
                module_title = module.get('title', module_id.split('/')[-1])
                module_required = module['required']
                module_time = module.get('estimated_time', '')
                
                # 构建模块链接
                module_link = f"/{module_id}/"
                
                # 必修/选修标识
                badge = "🔴 必修" if module_required else "🔵 选修"
                
                # 时间标识
                time_str = f" ({module_time})" if module_time else ""
                
                md.append(f"- {badge} [{module_title}]({module_link}){time_str}")
            
            md.append("")
            
            # 检查点（如果有）
            checkpoints = [cp for cp in config.get('checkpoints', []) 
                          if cp.get('after_stage') == stage_num]
            if checkpoints:
                for checkpoint in checkpoints:
                    cp_title = checkpoint.get('title', '检查点')
                    cp_assessment = checkpoint.get('assessment', '')
                    cp_score = checkpoint.get('required_score')
                    
                    md.append(f"#### ✅ {cp_title}")
                    md.append("")
                    md.append(f"**评估方式**: {cp_assessment}")
                    if cp_score:
                        md.append(f"**要求分数**: {cp_score}分")
                    md.append("")
        
        # 推荐资源
        if 'recommended_resources' in config and config['recommended_resources']:
            md.append("## 推荐资源")
            md.append("")
            
            # 按类型分组
            resources_by_type = {}
            for resource in config['recommended_resources']:
                res_type = resource.get('type', 'other')
                if res_type not in resources_by_type:
                    resources_by_type[res_type] = []
                resources_by_type[res_type].append(resource)
            
            type_names = {
                'book': '📚 书籍',
                'course': '🎓 在线课程',
                'tool': '🔧 工具',
                'standard': '📋 标准文档',
                'article': '📄 文章',
                'other': '🔗 其他资源'
            }
            
            for res_type, resources in resources_by_type.items():
                type_name = type_names.get(res_type, res_type)
                md.append(f"### {type_name}")
                md.append("")
                for resource in resources:
                    title = resource.get('title', '未命名资源')
                    url = resource.get('url', '#')
                    md.append(f"- [{title}]({url})")
                md.append("")
        
        # 元数据
        if 'metadata' in config:
            metadata = config['metadata']
            md.append("## 文档信息")
            md.append("")
            if 'version' in metadata:
                md.append(f"- **版本**: {metadata['version']}")
            if 'last_updated' in metadata:
                md.append(f"- **最后更新**: {metadata['last_updated']}")
            if 'author' in metadata:
                md.append(f"- **作者**: {metadata['author']}")
            if 'status' in metadata:
                status_map = {'active': '活跃', 'draft': '草稿', 'archived': '已归档'}
                status = status_map.get(metadata['status'], metadata['status'])
                md.append(f"- **状态**: {status}")
            md.append("")
        
        # 页脚
        md.append("---")
        md.append("")
        md.append("!!! tip \"学习建议\"")
        md.append("    - 建议按照阶段顺序学习，确保知识体系的连贯性")
        md.append("    - 必修模块是核心内容，必须完成")
        md.append("    - 选修模块可根据个人兴趣和实际需求选择")
        md.append("    - 在每个检查点进行自我评估，确保学习效果")
        md.append("")
        
        return "\n".join(md)
    
    def render_all_paths(self, skip_file_check: bool = False) -> Dict[str, str]:
        """
        渲染所有学习路径配置文件
        
        Args:
            skip_file_check: 是否跳过文件存在性检查
            
        Returns:
            字典，键为路径ID，值为渲染后的Markdown文本
        """
        results = {}
        
        # 查找所有YAML配置文件
        yaml_files = list(self.learning_paths_dir.glob("*-path.yaml"))
        
        for yaml_file in yaml_files:
            try:
                config = self.load_config(yaml_file)
                
                # 验证配置
                errors = self.validate_config(config, skip_file_check=skip_file_check)
                if errors:
                    print(f"⚠️  配置文件 {yaml_file.name} 验证失败:")
                    for error in errors:
                        print(f"   - {error}")
                    if not skip_file_check:
                        continue
                    print("   继续渲染（跳过文件检查）...")
                
                # 渲染Markdown
                markdown = self.render_markdown(config)
                path_id = config['path_id']
                results[path_id] = markdown
                
                # 保存到文件
                output_file = self.learning_paths_dir / f"{path_id}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                
                print(f"✅ 成功渲染: {yaml_file.name} -> {output_file.name}")
                
            except Exception as e:
                print(f"❌ 处理 {yaml_file.name} 时出错: {str(e)}")
        
        return results
    
    def generate_index(self, paths: Dict[str, Dict[str, Any]]) -> str:
        """
        生成学习路径索引页面
        
        Args:
            paths: 路径配置字典
            
        Returns:
            索引页面的Markdown文本
        """
        md = []
        
        md.append("---")
        md.append("title: \"学习路径\"")
        md.append("description: \"为不同角色定制的系统化学习路径\"")
        md.append("---")
        md.append("")
        
        md.append("# 学习路径")
        md.append("")
        md.append("本知识体系为不同角色提供了定制化的学习路径，帮助你系统地掌握医疗器械嵌入式软件开发所需的知识和技能。")
        md.append("")
        
        md.append("## 可用学习路径")
        md.append("")
        
        # 按角色分组
        for path_id, config in paths.items():
            title = config['title']
            description = config['description']
            difficulty = config['difficulty']
            time = config['estimated_total_time']
            target_role = config['target_role']
            
            # 难度图标
            difficulty_icons = {
                '基础': '🟢',
                '中级': '🟡',
                '高级': '🔴'
            }
            difficulty_icon = difficulty_icons.get(difficulty, '⚪')
            
            md.append(f"### {difficulty_icon} [{title}]({path_id}/)")
            md.append("")
            md.append(f"**目标角色**: {target_role}")
            md.append("")
            md.append(f"**难度**: {difficulty} | **预计时间**: {time}")
            md.append("")
            md.append(description)
            md.append("")
            md.append(f"[开始学习 →]({path_id}/)")
            md.append("")
            md.append("---")
            md.append("")
        
        md.append("## 如何选择学习路径")
        md.append("")
        md.append("根据你的职业角色和学习目标选择合适的学习路径：")
        md.append("")
        md.append("- **嵌入式软件工程师**: 如果你负责医疗器械的软件开发和实现")
        md.append("- **质量保证工程师**: 如果你负责质量管理、测试和合规性验证")
        md.append("- **系统架构师**: 如果你负责系统设计、架构决策和技术选型")
        md.append("- **监管事务专员**: 如果你负责法规合规、认证申报和技术文档")
        md.append("")
        
        md.append("## 学习建议")
        md.append("")
        md.append("!!! tip \"学习提示\"")
        md.append("    - 每个学习路径都经过精心设计，建议按照推荐顺序学习")
        md.append("    - 必修模块是核心内容，选修模块可根据实际需求选择")
        md.append("    - 在关键节点设有检查点，帮助你评估学习效果")
        md.append("    - 可以根据实际情况调整学习节奏，但建议完成所有必修内容")
        md.append("")
        
        return "\n".join(md)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='学习路径渲染脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 渲染所有学习路径
  python scripts/render_learning_paths.py
  
  # 验证单个配置文件
  python scripts/render_learning_paths.py --validate docs/learning-paths/embedded-engineer-path.yaml
  
  # 渲染单个配置文件到指定输出
  python scripts/render_learning_paths.py --path docs/learning-paths/embedded-engineer-path.yaml --output output.md
        """
    )
    
    parser.add_argument(
        '--validate',
        metavar='FILE',
        help='验证指定的配置文件'
    )
    
    parser.add_argument(
        '--path',
        metavar='FILE',
        help='渲染指定的配置文件'
    )
    
    parser.add_argument(
        '--output',
        metavar='FILE',
        help='输出文件路径（与--path一起使用）'
    )
    
    parser.add_argument(
        '--docs-dir',
        default='docs',
        help='文档根目录路径（默认: docs）'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='跳过模块文件存在性验证（用于开发阶段）'
    )
    
    args = parser.parse_args()
    
    renderer = LearningPathRenderer(docs_dir=args.docs_dir)
    
    # 验证模式
    if args.validate:
        config_path = Path(args.validate)
        try:
            config = renderer.load_config(config_path)
            errors = renderer.validate_config(config)
            
            if errors:
                print(f"❌ 配置文件验证失败: {config_path}")
                for error in errors:
                    print(f"   - {error}")
                sys.exit(1)
            else:
                print(f"✅ 配置文件验证通过: {config_path}")
                sys.exit(0)
        except Exception as e:
            print(f"❌ 验证失败: {str(e)}")
            sys.exit(1)
    
    # 单文件渲染模式
    elif args.path:
        config_path = Path(args.path)
        try:
            config = renderer.load_config(config_path)
            
            # 验证配置
            errors = renderer.validate_config(config)
            if errors:
                print(f"⚠️  配置文件存在问题:")
                for error in errors:
                    print(f"   - {error}")
                print("\n继续渲染...")
            
            # 渲染
            markdown = renderer.render_markdown(config)
            
            # 输出
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"✅ 已保存到: {output_path}")
            else:
                print(markdown)
            
        except Exception as e:
            print(f"❌ 渲染失败: {str(e)}")
            sys.exit(1)
    
    # 批量渲染模式（默认）
    else:
        print("🚀 开始渲染所有学习路径...")
        print()
        
        try:
            # 渲染所有路径
            results = renderer.render_all_paths(skip_file_check=args.skip_validation)
            
            if not results:
                print("⚠️  未找到任何学习路径配置文件")
                sys.exit(1)
            
            print()
            print(f"✅ 成功渲染 {len(results)} 个学习路径")
            
            # 生成索引页面
            print()
            print("📝 生成索引页面...")
            
            # 加载所有配置
            configs = {}
            for yaml_file in renderer.learning_paths_dir.glob("*-path.yaml"):
                try:
                    config = renderer.load_config(yaml_file)
                    configs[config['path_id']] = config
                except:
                    pass
            
            index_md = renderer.generate_index(configs)
            index_file = renderer.learning_paths_dir / "index.md"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_md)
            
            print(f"✅ 索引页面已保存: {index_file}")
            print()
            print("🎉 所有任务完成!")
            
        except Exception as e:
            print(f"❌ 批量渲染失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
