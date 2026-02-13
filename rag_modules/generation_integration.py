import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import strOutputParser
from typing import List
from langchain.core.document import Document
import logging
logger = logging.getLogger(__name__)

class GenerationIntegrationModule:
    def __init__(self, model_name:str='kimi-k2-0711-preview',temperature:float=0.1,max_tokens:int=2048):
        #初始化生成集成模块
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = None
        self.setup_llm()

    def setup_llm(self):
        #初始化大模型
        logger.info(f"正在初始化大模型: {self.model_name}")
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError("环境变量 MOONSHOT_API_KEY 未设置，请设置后重试")
        
        self.llm = MoonshotChat(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            moonshot_api_key=api_key  # 使用环境变量中的Moonshot API Key
        )
        logger.info("大模型初始化完成")
    
    def generate_basic_answer(self, query: str, context_docs: List[Document]) -> str:
        '''
        生成基本答案
        Args: 
        query: 用户查询字符串
        context_docs: 上下文文档列表
        Returns:
        生成的答案字符串
        '''
        logger.info(f"正在生成基本答案，查询: {query}")
        #构建提示词模板
        prompt = ChatPromptTemplate.from_templates('''
        你是一位专业的烹饪助手，拥有米其林三星主厨能力。应根据以下食谱信息回答用户的问题：
        
        用户的问题：{query}
        
        相关食谱信息：
        {context}
        
        请根据上述信息提供详细且专业的回答。如果信息不足，请如实说明。
        
        回答：''')

        #构建上下文字符串
        context = self._build_context(context_docs)

        #构建链式组件
        chain = (
            {"question": RunnablePassthrough(lambda: query), "context": lambda _: context}
            | prompt
            | self.llm
            | strOutputParser()
        )

        #大模型生成答案
        response = chain.invoke(
            query=query,
            context=context
        )

        return response

    def _build_context(self, context_docs: List[Document]) -> str:
        '''
        构建上下文字符串
        Args:
        context_docs: 上下文文档列表
        Returns:构建好的上下文字符串
        '''
        context_parts = []
        metadata_info = ''
        context_length = 0
        #检查上下文文档列表是否为空
        if not context_docs:
            logger.warning("上下文文档列表为空，生成答案可能不准确")
            return ""
        #组合元数据信息
        for i, doc in enumerate(context_docs,1):
            #提取菜品名称、菜品难度等元数据信息
            metadata_info = f"食谱 {i}:"
            #菜品名称
            if 'dish_name' in doc.metadata:
                dish_name = doc.metadata['dish_name']
                metadata_info += f" |菜品名称: {dish_name};"
            #菜品分类
            if 'category' in doc.metadata:
                dish_category = doc.metadata['category']
                metadata_info += f" |菜品分类: {dish_category};"
            #菜品难度
            if 'difficulty' in doc.metadata:
                dish_difficulty = doc.metadata['difficulty']
                metadata_info += f" |菜品难度: {dish_difficulty};"

            context_doc = f"{metadata_info}\n{doc.page_content}"
            context_parts.append(context_doc)
            context_length += len(context_doc)
            if context_length > 2048: #控制上下文长度，避免超过模型限制
                break

        #组合文档内容与元数据信息
        return '\n'+'='*50+'\n'.join(context_parts)