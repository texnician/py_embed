// mtd_test.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "mtd_lib.h"
#include <stdint.h>

int _tmain(int argc, _TCHAR* argv[])
{
	int64_t a = 111111;

    auto x = strtoul("4294967295", (char **)NULL, 10);
    
	{
		std::vector<int> vci(GetConstIntVec());
	}
	{
		std::vector<int> vi(GetIntVec());
	}
	{
		std::vector<std::string> v2 = GetConstStringVec();
	}
	{
		std::vector<std::string> v1 = GetStringVec();
	}
	return 0;
}
