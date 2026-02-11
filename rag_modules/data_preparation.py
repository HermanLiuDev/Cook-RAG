
import uuid
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from typing import List,Dict,Any
import logging
logging.getLogger(__name__)

from pathlib import Path

class DataPreparationModule:
    '''
    数据准备模块:根据数据路径加载文档和切块
    '''
    # 统一维护的分类与难度配置，供外部复用，避免关键词重复定义
    CATEGORY_MAPPING = {
        'meat_dish': '荤菜',
        'vegetable_dish': '素菜',
        'soup': '汤品',
        'dessert': '甜品',
        'breakfast': '早餐',
        'staple': '主食',
        'aquatic': '水产',
        'condiment': '调料',
        'drink': '饮品'
    }
    CATEGORY_LABELS = list(set(CATEGORY_MAPPING.values()))
    DIFFICULTY_LABELS = ['非常简单', '简单', '中等', '困难', '非常困难']

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents: List[Document] = []
        self.chunks: List[Document] = []

    def load_documents(self)-> List[Document]:
        '''
        加载文档

        Returns:
        documents: 加载的文档列表
        '''
        logging.info(f"正在加载文档 from {self.data_path}")
        documents = []
        path_obj = Path(self.data_path)

        #实现文档加载逻辑
        for md_file in path_obj.rglob("*.md"):
            try:
                # 读取Markdown文件内容
                with open(md_file, "r" , encoding="utf-8") as f:
                    content = f.read()
            
                # 创建Document对象
                doc = Document(
                                page_content=content,
                                metadata={
                                   "source": str(md_file)
                                }
                )
                # 增强文档元数据
                self._enhance_metadata(doc)
                documents.append(doc)

            except Exception as e:
                logging.error(f"加载文档 {md_file} 出错: {e}")

        self.documents = documents
        logging.info(f"已加载 {len(documents)} 个文档")

        return documents

    def _enhance_metadata(self, doc: Document):
        """
        增强文档元数据
        
        Args:
            doc: 需要增强元数据的文档
        """
        file_path = Path(doc.metadata.get('source', ''))
        path_parts = file_path.parts
        
        # 提取菜品分类
        doc.metadata['category'] = '其他'
        for key, value in self.CATEGORY_MAPPING.items():
            if key in path_parts:
                doc.metadata['category'] = value
                break
        
        # 提取菜品名称
        doc.metadata['dish_name'] = file_path.stem

        # 分析难度等级
        content = doc.page_content
        if '★★★★★' in content:
            doc.metadata['difficulty'] = '非常困难'
        elif '★★★★' in content:
            doc.metadata['difficulty'] = '困难'
        elif '★★★' in content:
            doc.metadata['difficulty'] = '中等'
        elif '★★' in content:
            doc.metadata['difficulty'] = '简单'
        elif '★' in content:
            doc.metadata['difficulty'] = '非常简单'
        else:
            doc.metadata['difficulty'] = '未知'

    @classmethod
    def get_supported_categories(cls) -> List[str]:
        """对外提供支持的分类标签列表"""
        return cls.CATEGORY_LABELS

    @classmethod
    def get_supported_difficulties(cls) -> List[str]:
        """对外提供支持的难度标签列表"""
        return cls.DIFFICULTY_LABELS

    def chunk_documents(self)-> List[Document]:
        '''
        切块文档

        Returns:
        chunks: 切块后的文档列表
        '''
        #实现文档切块逻辑
        logging.info("正在进行文档切块...")

        if not self.documents:
            raise ValueError("没有文档可供切块，请先加载文档")

        #执行分割器
        chunks = self._markdown_split_helper()
        #添加分块的元数据
        for i,chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = uuid.uuid4() #为每个切块生成唯一ID
            chunk.metadata['batch_index'] = i #继承菜品名称
            chunk.metadata['chunk_size'] = len(chunk.page_content) #记录切块大小
        self.chunks = chunks
        logging.info(f"切块完成，生成 {len(chunks)} 个切块")

        return chunks


    def _markdown_split_helper(self)-> List[Document]:
        '''
        辅助函数:根据Markdown语法切分文本

        Args:
        text: 输入的Markdown文本

        Returns:
        chunks: 切分后的文本段列表
        '''
        #实现Markdown文本切分逻辑


        #markdown切分标题定义
        headers_to_split_on = [
            ("#","一级标题"), #菜品名称
            ("##","二级标题"), #原材料、计算、操作
            ("###","三级标题"), #简易版本
        ]

        #定义分割器
        markdown_spliter = MarkdownHeaderTextSplitter(
                                headers_to_split_on = headers_to_split_on,
                                strip_headers=False#保留标题
                            )
        all_chunks = []
        
        for doc in self.documents:
            try:
                #判断doc是否存在标题
                content_preview = doc.page_content[:200]  #预览前200字符
                has_hearder = any(line.strip().startswith('#') for line in content_preview.split('\n'))
                
                #如果没有标题，记录日志并跳过切分
                if not has_hearder:
                    logging.warning(f"文档 {doc.metadata.get('dish_name', '未知')} 可能缺少标题，跳过Markdown切分")
                    all_chunks.append(doc)
                    continue

                #执行切分
                md_chunks = markdown_spliter.split_text(doc.page_content)
                logging.debug(f"文档 {doc.metadata.get('dish_name', '未知')} 切分成 {len(md_chunks)} 块")

                #集成切分结果
                all_chunks.extend(md_chunks)
            
            #其他问题，报错添加整个文档
            except Exception as e:
                logging.error(f"切分文档 {doc.metadata.get('dish_name', '未知')} 出错: {e}")
                all_chunks.append(doc)

        return all_chunks

    def get_statistics(self)-> Dict[str,Any]:
        '''
        获取数据统计信息

        Returns:
        stats: 数据统计信息字典
        '''
        category_counts = {}
        difficulty_counts = {}
        for doc in self.documents:
            category = doc.metadata.get('category', '未知')
            category_counts[category] = category_counts.get(category, 0) + 1
            difficulty = doc.metadata.get('difficulty', '未知')
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        stats = {
            "文档数量": len(self.documents),
            "切块数量": len(self.chunks),
            "菜品类别分布": category_counts,
            "难度分布": difficulty_counts,
            "分块平均长度": sum(chunk.metadata['chunk_size'] for chunk in self.chunks) / len(self.chunks) if self.chunks else 0
        }
        return stats
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    data_path = "/root/autodl-tmp/Cook-RAG/data/cook"
    data_module = DataPreparationModule(data_path)
    data_module.load_documents()
    data_module.chunk_documents()
    stats = data_module.get_statistics()
    for key, value in stats.items():
        logging.info(f"{key}: {value}")