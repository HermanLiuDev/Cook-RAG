import os
#导入配置文件
from config import DEFAULT_CONFIG, RAGconfig
#添加必要的模块导入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rag_modules import (
    DataPreparationModule,
    IndexConstructionModule,
    RetrievalOptimizationModule,
    GenerationIntegrationModule
)

#导入环境变量
from dotenv import load_dotenv
load_dotenv()

#配置日志记录
import logging

logging.basicConfig(level=logging.INFO,
                    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReceiptRAGSystem:
    '''
    食谱检索系统
    '''

    def __init__(self, config: RAGconfig = None):
        '''
        系统变量初始化
        
        Args：
        config: 配置文件

        '''
        #加载配置文件
        self.config = config or DEFAULT_CONFIG
        
        #初始化数据处理、检索构建、检索优化和答案生成模块
        self.data_model = None
        self.index_model = None
        self.retrieval_model = None
        self.generation_model = None

        #检查数据文件路径
        if not Path(self.config.data_path).exists():
            raise FileNotFoundError(f"数据文件路径 {self.config.data_path} 不存在，请检查路径是否正确")

        #检查大模型api key设置
        if not os.getenv("MOONSHOT_API_KEY"):
            raise ValueError("环境变量 MOONSHOT_API_KEY 未设置，请设置后重试")
        
    def init_system(self):
        '''
        初始化系统模块
        
        '''
        logger.info("📚正在初始化系统核心模块，含：数据处理、索引构建、答案生成模块")
        #初始化数据处理模块
        self.data_model = DataPreparationModule(self.config.data_path)

        #初始化索引模块
        logger.info("正在初始化索引构建模块")
        self.index_model = IndexConstructionModule(
            model_name=self.config.embedding_model,
            index_path=self.config.index_path
            )

        #初始化生成模块
        logger.info("正在初始化生成模块")
        self.generation_model = GenerationIntegrationModule(
            model_name=self.config.llm_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        logger.info("✅系统核心模块初始化完成")

    def bulid_knowledge_database(self):
        '''
        构建知识库

        '''
        logger.info("📚正在构建知识库")
        vectorstore = self.index_model.load_index()
        if vectorstore is not None:
            logger.info("📚使用本地索引，跳过索引构建")
            #可以优化
            #获取文档
            self.data_model.load_documents()

            #处理文档和切块
            chunks = self.data_model.chunk_documents()
        else:
            #获取文档
            self.data_model.load_documents()

            #处理文档和切块
            chunks = self.data_model.chunk_documents()

            #构建索引
            vectorstore = self.index_model.build_index(chunks)

            #保存索引
            self.index_model.save_index()
        
        #初始化检索模块
        self.retrieval_model = RetrievalOptimizationModule(
            index_vectorstore=vectorstore,
            chunks=chunks
        )

        #数据库统计信息
        stats = self.data_model.get_statistics()
        print(f'📊数据库统计信息:\n {stats}')

        logger.info("✅知识库构建完成")


    def answer_question(self, question: str):
        '''
        回答用户问题

        Args:
        question: 用户输入的问题

        Returns:
        answer: 系统生成的回答
        '''
        #判断相关模块是否加载
        if self.retrieval_model is None or self.generation_model is None:
            raise ValueError("系统模块未完全初始化，请先初始化系统模块")

        #用户问题与处理
        print(f"🔍正在检索相关信息以回答问题: {question}")

        #实施检索
        relevant_chunks = self.retrieval_model.hybrid_search(question, top_k=self.config.top_k)

        #显示检索到的子块信息
        if relevant_chunks:
            chunk_info = []
        for chunk in relevant_chunks:
            dish_name = chunk.metadata.get('dish_name', '未知菜品')
            # 尝试从内容中提取章节标题
            content_preview = chunk.page_content[:100].strip()

            logger.info(f"检索到的文档块预览: {content_preview}\n")
            
            if content_preview.startswith('#'):
                # 如果是标题开头，提取标题（仅取第一行）
                title_end = content_preview.find('\n') if '\n' in content_preview else len(content_preview)
                section_title = content_preview[:title_end].replace('#', '').strip()
                chunk_info.append(f"{dish_name}({section_title})")
            else:
                chunk_info.append(f"{dish_name}(内容片段)")

            print(f"找到 {len(relevant_chunks)} 个相关文档块: {', '.join(chunk_info)}")
        else:
            print(f"找到 {len(relevant_chunks)} 个相关文档块")

        #生成回答
        answer = self.generation_model.generate_basic_answer(question, relevant_chunks)
        #返回结果
        return answer

    def run_interactive(self):
        '''
        运行交互式问答系统
        '''
        print("😊欢迎使用食谱检索系统！")
        print("该系统致力于解决今天吃什么的难题🥗")

        #初始化系统
        self.init_system()
        #构建知识库
        self.bulid_knowledge_database()

        while True:
            try:
                user_input = input("请输入您的问题（输入 '退出' 结束）： ").strip()
                
                if user_input.lower() in ['退出', 'exit', 'quit']:
                    print("感谢使用，再见！👋")
                    break

                answer = self.answer_question(user_input)
                print(f"系统回答：{answer}")

            except KeyboardInterrupt:
                print("\n感谢使用，再见！👋")
                break
            except Exception as e:
                logging.error(f"交互式问答系统出错: {e}")
                print(f"系统错误： {e}")


def main():
    #主函数
    try:
        #创建rag系统
        rag_system = ReceiptRAGSystem()
        #运行系统
        rag_system.run_interactive()

    except Exception as e:
        logging.error(f"系统运行出错: {e}")
        print(f"系统错误： {e}")
    

if __name__ == "__main__":
    main()
