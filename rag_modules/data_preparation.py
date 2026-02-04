
from langchain_core.documents import Document
from typing import List,Dict,Any
import logging
logging.getLogger(__name__)

from pathlib import Path

class DataPreparationModule:
    '''
    数据准备模块:根据数据路径加载文档和切块
    '''
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
                documents.append(doc)

            except Exception as e:
                logging.error(f"加载文档 {md_file} 出错: {e}")

        self.documents = documents
        logging.info(f"已加载 {len(documents)} 个文档")

        return documents


    def chunk_documents(self)-> List[Document]:
        '''
        切块文档

        Returns:
        chunks: 切块后的文档列表
        '''
        #实现文档切块逻辑
        pass

    def _markdown_split_helper(self)-> List[Document]:
        '''
        辅助函数:根据Markdown语法切分文本

        Args:
        text: 输入的Markdown文本

        Returns:
        chunks: 切分后的文本段列表
        '''
        #实现Markdown文本切分逻辑
        pass

    def get_statistics(self)-> Dict[str,Any]:
        '''
        获取数据统计信息

        Returns:
        stats: 数据统计信息字典
        '''
        stats = {
            "文档数量": len(self.documents),
            "切块数量": len(self.chunks)
        }
        return stats
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    data_path = "D:/Cursor-Project/Cook-RAG/data/cook"
    data_module = DataPreparationModule(data_path)
    data_module.load_documents()