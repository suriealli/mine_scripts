/*我是UTF8无签名编码 */

//#ifdef WIN
//#define WIN32_LEAN_AND_MEAN
//#include "vld.h"
//#endif
#include "ComplexServer.h"

int main(int argc, char* argv[])
{
	// 初始化进程信息
	GEProcess::Instance()->Main(argc, argv);
	// 初始化Python虚拟机
	GEPython::InitPython();

	ComplexServer::New();
	ComplexServer::Instance()->Init(argc, argv);
	ComplexServer::Delete();

	// 结束Python虚拟机
	GEPython::FinalPython();

	return 0;
}

