#!/usr/bin/env python
#coding:utf8
#get domain ID:instanceId

import httplib,time 
import random,sys
import hashlib,base64,hmac
from json import dumps

#获取instanceIds,可多域名获取，返回一个字典，域名：instanceId
def get_instanceIds(method,domains,secretid,secretkey,api_url):
    uri = "/v1/domains/query_instance_id?domains=%s" %(domains)
    req = _get_SigAndHeaders(method,secretid,secretkey,uri = uri,body = "")
    response = _Http_connect(api_url,method,uri,headers = req['headers'],body = "")
    if response.reason != "OK":
        print response.status,response.reason
        sys.exit()
    return eval(response.read())['instanceIds']

#绑定ip和端口，一次绑定一个域名一个ip一个端口，返回response
def Bind_Domains_CvmPorts(method,secretid,secretkey,body,uri,api_url):
    body = dumps(body) if isinstance(body,dict) else body
    req = _get_SigAndHeaders(method,secretid,secretkey,body,uri)
    response = _Http_connect(api_url,method,uri,body,req['headers'])
    return response

#获取域名绑定信息，一次获取一个域名的信息。返回response
def Get_Domains_info(method,secretid,secretkey,uri,api_url):
    req =  _get_SigAndHeaders(method,secretid,secretkey,uri = uri,body = "")
    response = _Http_connect(api_url,method,uri,headers = req['headers'],body = "")
    if response.reason != "OK":
        print response.status,response.reason
        sys.exit()
    return response

#使用Http连接远程方法
def _Http_connect(api_url,method,uri,body,headers):
    try:
        httpClient = httplib.HTTPConnection(api_url, 80, timeout=30)
        httpClient.request(method = method, url = uri,body = body,headers = headers)
        response = httpClient.getresponse()
        if httpClient:
            httpClient.close()
        return response
    except Exception,e:
        print e
        if httpClient:
            httpClient.close()
        sys.exit()

#生成签名和headers的方法，返回字典。
def _get_SigAndHeaders(method,secretid,secretkey,body,uri):
    result={}
    nonce = random.randint(0,2**32-1)
    timestamp = int(time.time())
    body = dumps(body) if isinstance(body,dict) else body
    arr2sig = ['body=' + body,'method=' + method,'uri=' + uri,'x-txc-cloud-secretid=' + secretid,'x-txc-cloud-nonce=' + str(nonce),'x-txc-cloud-timestamp=' + str(timestamp)]
    arr2str = "&".join(arr2sig)
    result['sig'] = hmac.new(secretkey,arr2str,hashlib.sha1).digest().encode('base64').rstrip()
    result['headers'] = {
           "Content-type":"application/json;charset=utf-8",
           "x-txc-cloud-secretid":secretid,
           "x-txc-cloud-nonce":nonce,
           "x-txc-cloud-timestamp":timestamp,
           "x-txc-cloud-signature":result['sig'],
          }
    return result

if __name__ == "__main__":
    domains = "s580.app1104541964.qqopenapp.com"
    secretid="AKIDkIghdJ0j2dHksZ4cyr6jfZted9QGeOok"
    secretkey="utwcEKxXjnprcfTdLfOl3OCT1wTcjDLg"
    api_url   = "api.yun.qq.com"
    #response是HTTPResponse对象
    instanceIds = get_instanceIds('GET',domains,secretid,secretkey,api_url)
    print instanceIds
    uri = '/v1/domains/%s' %(instanceIds[domains])
    response = Get_Domains_info('GET',secretid,secretkey,uri,api_url)
    data = eval(response.read())
    print data['instanceInfo']['domain'],data['instanceInfo']['devicesList'][0]['lanIp'],data['instanceInfo']['devicesList'][0]['port'],data['httpCode']


