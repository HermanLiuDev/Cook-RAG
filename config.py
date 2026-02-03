
from dataclasses import dataclass
from typing import Dict,Any


@dataclass
class RAGconfig:
    # 配置文件类
    data_path: str = "../data"
    index_path: str = "../vectordatabase"

    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    llm_model: str = "kimi-k2-0711-preview"
    
    #配置最大检索数量
    top_k: int = 3

    #配置生成参数
    temperature: float = 0.1
    max_tokens: int = 2048


    def __post_init__(self):
        #添加对初始化变量的进一步处理
        pass

    @classmethod
    def from_dict(cls, config_dict: Dict[str,Any])-> 'RAGconfig':
        '''从字典配置实例'''
        return cls(**config_dict)
    
    def to_dict(self)-> Dict[str,Any]:
        '''转化为字典'''
        config_dict = {
            "data_path": self.data_path,
            "index_path": self.index_path,
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model,
            "top_k": self.top_k
        }
        return config_dict

DEFAULT_CONFIG = RAGconfig()