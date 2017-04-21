# api-mock
----
### 简介
> api-mock是一个支持录制和模拟各种http协议接口的mock服务器。
api-mock服务在record模式时可记录所有请求的数据，并用于mock模式下。
在mock模式下，api-mock服务可模拟一组静态的数据，也可以通过api控制其动态修改接口和数据。
通过api-mock可以模拟整个业务流程中的所有http接口，以达到简化测试代码和提高稳定性的目的。
在手工测试中也可以通过api-mock模拟一些不好在测试环境或线上环境模拟的数据。
 
### 注意 
> 使用api-mock后客户端完全和后端api服务器分离。api服务器相关的缺陷将不会被测到。可使用接口测试工具继续完成api接口服务的测试工作，以保障客户端质量。



## 使用说明
(详细使用文档请参阅 [api-mock使用指南](https://wiki.sankuai.com/pages/viewpage.action?pageId=835829655))

### 安装
1. 准备环境

    * python3.6
                
            brew install python3

2. setup

        git clone ssh://git@git.sankuai.com/~zhaoye05/api-mock.git
        cd api-mock
        sh setup.sh
        
3. setup device

    * 启动代理
            
            sh proxy.sh
       
    * 将被测设备的代理地址设为代理启动时日志中输出的地址
    * 被测设备上用浏览器打开 http://mitm.it, 选择对应操作系统安装证书
    
    
### 使用

* Record模式

    1. 启动代理
        
            sh proxy.sh
        
    2. 启动mock-server record模式
    
            sh record.sh
    
    >此模式下，不会模拟任何数据。所有请求最终都会发向原始目标服务器。
    其中经过mock服务的请求会被录制到mock/record目录下
    
* Mock模式

    1. 启动代理
    
            sh proxy.sh
            
    2. 启动mock
    
            sh mock.sh


# api-mock
# api-mock
