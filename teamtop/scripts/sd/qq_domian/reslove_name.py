#!/usr/bin/env python 
#coding:utf8

import sys,time
import http_connect
import argparse

##############变量设定###############
api_url   = "api.yun.qq.com"    ##云端api地址
domain_base = ""  #域名
secretid  = ""   #id
secretkey = ""  #key
lanIps    = ""  #绑定的ip
port      = 80  #端口


#颜色
red = "\033[40;31m %s \033[0m"
green = "\033[40;32m %s \033[0m"


def Parser_args():
    parse = argparse.ArgumentParser()
    help = "Use this argument to specify the file you want./这个参数用来设置要解析的域名文件。注：第一列为区ID即可。"
    parse.add_argument("-f","--file",help=help)

    help = "Use this argument to specify the schedule you want./这个参数用来设置执行的动作，如：reslove,status"
    parse.add_argument("-s","--schedule",help=help)

    args = parse.parse_args()
    return args

#域名列表
def create_domain_name_list(file):
    domain_list = []
    with open(file) as f:
        for line in f.readlines():
            num = line.strip().split()
            if len(num) != 0:
                domain_list.append('s%s.%s'%(num[0],domain_base))
    return domain_list


#域名解析并检查。
def relove_check_domain(domain_list,instanceIds):
    for domain in domain_list:
        print "========开始绑定域名%s ========" %(domain)
        uri = "/v1/domains/%s/cvm_bind" %(instanceIds[domain])
        body = {
        "lanIps":lanIps.split(","),
        "port":port,
        }
        response = http_connect.Bind_Domains_CvmPorts('POST',secretid = secretid,secretkey = secretkey,body = body,uri = uri,api_url = api_url)
        # result = response.status if response.status == "OK" else response.reason
        if response.status == 200:print domain + ":" + green %(response.status)
        if response.status != 200:print domain + ":" + red %(response.status) + red %(response.reason)
        check_domain(domain_list = domain.split(),instanceIds = instanceIds)
        print "此处sleep 15秒，开平接口频率问题。"
        time.sleep(15)

#检查域名解析
def check_domain(domain_list,instanceIds):
    for domain in domain_list:
        uri = "/v1/domains/%s" %(instanceIds[domain])
        Doinfo_response = http_connect.Get_Domains_info('GET',secretid = secretid,secretkey = secretkey,uri = uri,api_url = api_url)
        Domian_Bind_info = eval(Doinfo_response.read())
        print "检查域名%s 解析情况：" %domain
        print Domian_Bind_info['instanceInfo']['domain'],Domian_Bind_info['instanceInfo']['devicesList'],
        if Domian_Bind_info['httpCode'] == 200:print green %(Domian_Bind_info['httpCode'])
        else:print red %(Domian_Bind_info['httpCode'])


if __name__ == "__main__":
    args = Parser_args()   #获取参数
    if len(sys.argv) != 5:
        print "%s --help 查看详细说明。"%(sys.argv[0])
        sys.exit("参数错误。")
    domain_list = create_domain_name_list(args.file)   #生成域名列表
    domains = ",".join(domain_list)
    instanceIds = http_connect.get_instanceIds('GET',domains,secretid,secretkey,api_url)
    if args.schedule == "reslove":
        relove_check_domain(domain_list,instanceIds)
    elif args.schedule == "status":
        check_domain(domain_list,instanceIds)
