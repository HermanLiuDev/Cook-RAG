import logging

class ReceiptRAGSystem:
    #加载配置文件


    #初始化各模块


    #加载索引与系统就绪


    #用户问题与处理


    #实施检索


    #生成回答


    #返回结果




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
