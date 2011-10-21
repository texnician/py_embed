#include "mtd_lib.h"

std::vector<std::string> GetStringVec()
{
    std::vector<std::string> v;
    v.push_back("aa");
    v.push_back("bb");
    v.push_back("cc");
    return v;
}

const std::vector<std::string> GetConstStringVec()
{
    std::vector<std::string> v;
    v.push_back("11");
    v.push_back("22");
    v.push_back("33");
    return v;
}

std::vector<int> GetIntVec()
{
	std::vector<int> v;

	v.push_back(1);
	v.push_back(2);

	return v;
}

std::vector<int> MTD_API GetConstIntVec()
{
	std::vector<int> v;
	v.push_back(3);
	v.push_back(4);
	return v;
}