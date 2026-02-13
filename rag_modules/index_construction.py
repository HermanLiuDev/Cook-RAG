import logging 
import os
from pathlib import Path
from langchain_core.documents import Document
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

logger = logging.getLogger(__name__)

class IndexConstructionModule:
    
    def __init__(self, model_name='BAAI/bge-small-zh-v1.5', index_path='./index_vectorstore'):
        #初始化索引构建模块
        self.model_name = model_name
        self.index_path = index_path
        self.embedding_model = None
        self.index_vectorstore = None
        self.setup_embedding_model()
    
    def setup_embedding_model(self):
        #设置嵌入模型
        logger.info(f"正在加载嵌入模型: {self.model_name}")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        logger.info("嵌入模型加载完成")

    def build_index(self, chunks: List[Document]) -> FAISS:
        '''       
        构建索引
        Args:
        chunks: 输入的文档块列表
        '''
        logger.info("正在构建索引")
        if not chunks:
            raise ValueError("输入的文档块列表不能为空")

        self.index_vectorstore = FAISS.from_documents(
            chunks, 
            self.embedding_model
            )
        logger.info("索引构建完成")
        return self.index_vectorstore

    def add_documents_to_index(self, new_chunks: List[Document]):
        '''
        向现有索引添加新文档块
        Args:
        new_chunks: 新增的文档块列表
        '''
        if self.index_vectorstore is None:
            raise ValueError("索引尚未构建，无法添加新文档块")
        
        logger.info(f"正在向索引添加 {len(new_chunks)} 个新文档块")
        self.index_vectorstore.add_documents(new_chunks)
        logger.info("新文档块添加完成")

    def save_index(self):
        '''
        保存索引到指定路径
        Args:
        index_save_path: 索引保存的路径
        '''
        if self.index_vectorstore is None:
            logger.warning("索引尚未构建，无法保存")
        
        self.index_vectorstore.save_local(self.index_path)
        logger.info(f"索引已保存到 {self.index_path}")
        

    def load_index(self):
        '''
        从指定路径加载索引
        Args:
        index_path: 索引加载的路径
        '''
        #确定嵌入模型初始化
        if not self.embedding_model:
            self.setup_embedding_model()
        #确定索引路径存在
        if not Path(self.index_path).exists():
            logger.error(f"索引路径 {self.index_path} 不存在，请检查路径是否正确")
            return None

        logger.info(f"正在从 {self.index_path} 加载索引")
        try:
            self.index_vectorstore = FAISS.load_local(
                self.index_path, 
                self.embedding_model,
                allow_dangerous_deserialization=True
                )
            logger.info("索引加载完成")
        except Exception as e:
            logger.error(f"加载索引失败: {e},请重新构建新索引")
            return None

        return self.index_vectorstore
   

    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        '''
        执行相似度搜索
        Args:
        query: 搜索查询
        top_k: 返回的最相似文档数量
        '''
        if not self.index_vectorstore:
            logger.error("索引尚未加载或构建，无法执行相似度搜索")
            return
        return self.index_vectorstore.similarity_search(query, k=top_k)

if __name__ == "__main__":
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  
    logging.basicConfig(level=logging.INFO,
                    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # 构造模拟的文档块
    mock_chunks = [
    Document(page_content="今天应该吃龙虾", metadata={"source": "文档1"}),
    Document(page_content="西红柿鸡蛋怎么做", metadata={"source": "文档2"}),
    Document(page_content="这是第三段文本内容", metadata={"source": "文档3"}),
    ]
    # 初始化索引构建模块
    index_module = IndexConstructionModule()
    # 构建索引
    index_module.build_index(mock_chunks)
    # 执行相似度搜索    
    search_results = index_module.similarity_search("龙虾", top_k=2)

    print("相似度搜索结果:")
    for doc in search_results:
        print(f"文档内容: {doc.page_content}, 元数据: {doc.metadata}")