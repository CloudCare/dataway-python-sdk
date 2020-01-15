# dataway-python-sdk

&emsp;dataway-pythonn-sdk 是用 Python 开发的包，用于数据进行适配以行协议格式写入 DataWay 中，方便用户专注于自己业务逻辑开发，不需要数据有效性检查以及行协议格式的转换等。另外本 SDK 还支持从 NSQ 消费消息。

dwadapter 包其文件主要如下：

- transport.py：负责数据的发送。TransportMixinBase基类定义发送数据接口。HttpTransportMixin子类以HTTP发送行协议数据到 DataWay ；TcpTransportMixin与UdpTransportMixin子类分别以TCP与UDP发送行协议数据到dataway，但是它们暂未实现，留将来扩展使用。  
- agent.py：负责从NSQ取出消息，其中NsqAgent类是对第三方库pynsq的封装。  
- check.py：负责在行协议转换之前对数据类型有效性进行检查，即tags与fields等是否符合规范。  
- adapater.py：负责行协议转换等。DatawayBase基类与其子类DatawayAdapter实现WriteMetrics，WriteKeyEvent与WriteFlow等接口。DatawayHttpAdapter仅仅继承了DatawayAdapter与HttpTransportMixin类，并无其它逻辑；DatawayTcpAdapter，DatawayUdpAdapter类似。  


# 接口说明
&emsp;本 SDK 提供3个接口用于把数据写入 DataWay 中，分别是WriteMetrics，WriteKeyEvent，WriteFlow。  
&emsp;WriteMetrics用于将常规的tags与fields写入 DataWay中，表名由measurement参数指定。
```
     def WriteMetrics(self, measurement, timestamp, fields, tags=None):
        """
        :param measurement: 必需；字符串类型
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param fields: 必需；字典，key为字符串类型，value为字符串，整型，浮点型或者布尔型之一
        :param tags: 非必需；字典，key与value均为字符串类型
        :return: 成功返回True，失败返回False
        """
```

&emsp;WriteKeyEvent写入事件信息到 DataWay 中，表名固定为keyevent。source最终合并于tags参数中，title, des，link最终合并于fields参数中。
```
    def WriteKeyEvent(self, title, timestamp, des=None, link=None, source=None, tags=None):
        """
        :param title: 必需；字符串类型
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param des: 非必需；字符串类型
        :param link: 非必需；字符串类型
        :param source: 非必需；字符串类型
        :param tags: 非必需；字典，key与value均为字符串类型
        :return: 成功返回True，失败返回False
        """
```
&emsp;WriteFlow写入流程信息到 DataWay 中，表名固定为flow。traceid, name, parent, flowtype最终与tags参数合并；duration最终与fields参数合并。
```
    def WriteFlow(self, traceid, name, parent, flowtype, duration, timestamp, tags=None, fields=None):
        """
        :param traceid: 必需；字符串类型
        :param name: 必需；字符串类型
        :param parent: 必需；字符串类型
        :param flowtype: 必需；字符串类型
        :param duration: 必需；整型，毫秒单位
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param tags: 非必需；字典，key与value均为字符串类型
        :param fields: 非必需；字典，key为字符串类型，value为字符串，整型，浮点型或者布尔型之一
        :return: 成功返回True，失败返回False
        """    
```
  
# SDK 使用

&emsp;安装，使用
> python setup.py bdist_wheel
  
在dist目录生成.whl文件,然后使用pip install生成的.whl文件即可。
> pip install  dwadapter-0.0.1-py3-none-any.whl

使用方式1：NSQ+DataWay，从NSQ中取出消息进行处理，最后写入 DataWay 中。

```
from dwadapter.adapater import DatawayHttpAdapter
from dwadapter.agent import NsqAgent


class MyHandler(DatawayHttpAdapter):
    def hander(self, msg):
		# 取出消息
        # body = msg.body

		# 业务处理 process(body)

		# 根据业务需要，使用如下接口之一将数据写入 DataWay
        # self.WriteMetrics(measurement, timestamp, fields, tags=None)
        # self.WriteKeyEvent(title, timestamp, des=None, link=None, source=None, tags=None)
		# self.WriteFlow(traceid, name, parent, flowtype, duration, timestamp, tags=None, fields=None)
 

if __name__ == "__main__":
    # 必须以关键字参数初始化NsqAgent
    agent = NsqAgent(nsq_url = "127.0.0.1:4161",  # nsq地址
                     topic   = "test",            # 消费的topic名称
                     channel = "test_process",	  # 消费的channel名称
                     handler =  MyHandler(dataway_url="http://10.100.64.106:19528/v1/write/metrics") # 自定义消息处理逻辑
                     )
    agent.start()
```  


使用方式2：DataWay，不需要从NSQ中取出消息，数据直接写入 DataWay 中。


```
from dwadapter.adapater import DatawayHttpAdapter

if __name__ == "__main__":
	# 必须以关键字参数初始化DatawayHttpAdapter
    adapter = DatawayHttpAdapter(dataway_url="http://10.100.64.106:19528/v1/write/metrics")
    tags = {"city":"sh"}
    fields = {
        "float" : 1.2,
        "int" : 2,
        "str" : "abc",
        "bool": True
    }
    for i in range(1000):
        adapter.WriteMetrics(measurement="DatawayTest", tags=tags, fields=fields, timestamp=None)
		# 根据业务需要，使用如下接口之一将数据写入 DataWay
        # adapter.WriteMetrics(measurement, timestamp, fields, tags=None)
        # adapter.WriteKeyEvent(title, timestamp, des=None, link=None, source=None, tags=None)
		# adapter.WriteFlow(traceid, name, parent, flowtype, duration, timestamp, tags=None, fields=None)
```
