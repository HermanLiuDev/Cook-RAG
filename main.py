#导入配置文件
from config import DEFAULT_CONFIG, RAGconfig
#添加必要的模块导入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from rag_modules import DataPreparationModule

#导入环境变量
from dotenv import load_dotenv
load_dotenv()




#配置日志记录
import logging

logging.basicConfig(level=logging.INFO,
                    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger(__name__)

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

    def init_system(self):
        '''
        初始化系统模块
        
        '''
        #加载数据处理模块
        self.data_model = DataPreparationModule(self.config.data_path)

        #加载索引模块

        #加载检索模块

        #加载生成模块
        pass

    def bulid_knowledge_database(self):
        '''
        构建知识库

        '''
        #获取文档

        #处理文档和切块

        #构建索引

        #初始化检索模块

        #数据库统计信息
        pass

    def answer_question(self, question: str):
        '''
        回答用户问题

        Args:
        question: 用户输入的问题

        Returns:
        answer: 系统生成的回答
        '''

        #用户问题与处理


        #实施检索


        #生成回答


        #返回结果
        pass

    def run_interactive(self):
        '''
        运行交互式问答系统
        '''
        print("😊欢迎使用食谱检索系统！")
        print("该系统致力于解决今天吃什么的难题🥗")

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
