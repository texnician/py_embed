#ifndef _MTD_LIB_H_
#define _MTD_LIB_H_

#if defined(MTD_LIB_DLL_BUILD)
#define MTD_API __declspec(dllexport)
#elif defined(MTD_LIB_DLL)
#define MTD_API __declspec(dllimport)
#else
#define MTD_API
#endif

#include <vector>
#include <string>

#if defined(__cplusplus)
#endif

std::vector<std::string> MTD_API GetStringVec();

const std::vector<std::string> MTD_API GetConstStringVec();

std::vector<int> MTD_API GetIntVec();

std::vector<int> MTD_API GetConstIntVec();

#if defined(__cplusplus)
#endif
#endif 
