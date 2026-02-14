import sys
from langchain.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain.vectorstores import FAISS
from typing import List
import logging


logger = logging.getLogger(__name__)

class RetrievalOptimizationModule:
    def __init__(self, index_vectorstore: FAISS, chunks: List[Document]):
        #初始化检索优化模块
        self.index_vectorstore = index_vectorstore
        self.chunks = chunks
        #检索器成员变量
        self.setup_retrieval()
        
    def setup_retrieval(self,vector_topk: int = 5, bm25_topk: int = 5):
        #设置检索器
        logger.info("正在初始化检索器")
        #边界条件检查
        if self.index_vectorstore is None:
            raise ValueError("索引尚未构建，无法初始化检索器")
        if not self.chunks:
            raise ValueError("输入的文档块列表不能为空")
        
        #向量检索器
        self.vector_retrieval = self.index_vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": vector_topk}
        )

        #BM25检索器  
        self.bm25_retrieval = BM25Retriever.from_documents(
            self.chunks,
            k=bm25_topk
        )

        logger.info("检索器设置完成")

    def hybrid_search(self,query: str, top_k: int = 3) -> List[Document]:
        '''
        混合检索方法，结合向量检索和BM25检索
        Args:
        query: 用户查询字符串
        top_k: 返回的文档数量
        '''
        logger.info(f"正在执行混合检索，查询: {query}")
        #向量检索结果
        vector_results = self.vector_retrieval.invoke(query)
        #BM25检索结果
        bm25_results = self.bm25_retrieval.invoke(query)

        #使用rrk算法进行重排
        rrk_reranked_results = self._rrk_rerank(vector_results, bm25_results)
        
        logger.info(f"混合检索完成，返回 {len(rrk_reranked_results)} 条结果")
        return rrk_reranked_results[:top_k]
    
    def _rrk_rerank(self, vector_results: List[Document], bm25_results: List[Document], k: int = 60) -> List[Document]:
        '''
        RRK重排算法，将向量检索和BM25检索结果进行融合
        
        Args:
        vector_results: 向量检索结果列表
        bm25_results: BM25检索结果列表
        k: RRF算法中的k值
        
        Returns:融合重排后的文档列表
        '''
        logger.info("正在进行RRK重排")
        doc_scores = {}
        doc_objects = {}

        #统计向量检索结果的得分
        for rank, doc in enumerate(vector_results):
            rrf_score = 1.0 / (k + rank + 1)
            doc_id = hash(doc.page_content)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            doc_objects[doc_id] = doc

        #统计BM25检索结果的得分
        for rank, doc in enumerate(bm25_results):
            rrf_score = 1.0 / (k + rank + 1)
            doc_id = hash(doc.page_content)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            doc_objects[doc_id] = doc

        #根据得分进行融合重排
        reranked_docs = []
        sorted_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
        for doc_id, final_score in sorted_docs:
            if doc_id in doc_objects:
                doc = doc_objects[doc_id]
                doc.metadata['rrf_score'] = final_score
                reranked_docs.append(doc)
        logger.info(f"RRK重排完成:向量检索{len(vector_results)}个文档，BM25检索{len(bm25_results)}个文档，重排后{len(reranked_docs)}个文档")
        return reranked_docs
    
if __name__ == "__main__":
    from pathlib import Path
    import sys
    logging.basicConfig(level=logging.INFO,
                    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #通过相对路径加载rag模块
    sys.path.append(str(Path(__file__).parent.parent))
    from rag_modules.index_construction import IndexConstructionModule
    #数据准备(加载食谱数据集)
    from rag_modules.data_preparation import DataPreparationModule
    data_module = DataPreparationModule(data_path="./Cook-RAG/data")
    data_module.load_documents()
    mock_chunks = data_module.chunk_documents()

    '''
    mock_chunks = [
        Document(page_content="今天应该吃龙虾", metadata={"source": "文档1"}),
        Document(page_content="西红柿鸡蛋怎么做", metadata={"source": "文档2"}),
        Document(page_content="这是第三段文本内容", metadata={"source": "文档3"}),
    ]    
    '''
    # 构造模拟的文档块

    # 初始化索引构建模块
    index_module = IndexConstructionModule(index_path="./Cook-RAG/index_vectorstore")
    vectorstore = index_module.load_index()
    if vectorstore is None:
        logger.warning("索引加载失败，正在构建新索引")
        # 构建索引
        vectorstore = index_module.build_index(mock_chunks)
    # 初始化检索优化模块
    retrieval_module = RetrievalOptimizationModule(
        index_vectorstore=vectorstore,
        chunks=mock_chunks
    )
    # 执行混合检索
    hybrid_results = retrieval_module.hybrid_search("有什么用西红柿做的菜品", top_k=5)
    
    print("混合检索结果:")
    for doc in hybrid_results:
        print(f"内容: {doc.page_content}, 来源: {doc.metadata.get('source')}, RRF得分: {doc.metadata.get('rrf_score')}")