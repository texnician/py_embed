#include "idb_cmd.h"

const HWSQLCmd HWSQLCmd::Null = HWSQLCmd(NULL);


HWDBResult::HWDBResult()
    : has_error_(false), result_(0)
{}

bool HWDBResult::HasError() const
{
    return has_error_;
}

HWDBResult& HWDBResult::SetError()
{
    has_error_ = true;
    return *this;
}

HWDBResult& HWDBResult::SetResult(int result)
{
    result_ = result;
    return *this;
}

HWDBResult& HWDBResult::SetSubResult(const char* task, int result)
{
    sub_result_map_[task] = result;
    return *this;
}

int HWDBResult::GetSubResult(const char* task) const
{
    SubResultMap::const_iterator it = sub_result_map_.find(task);
    return it != sub_result_map_.end() ? it->second : 0;
}

HWSQLCmd::HWSQLCmd(const char* sql)
    : sql_(sql)
{}

bool HWSQLCmd::IsNull() const
{
    return sql_.empty();
}

HWSQLCmd& HWSQLCmd::SetSubCmd(const char* task, const HWSQLCmd& other)
{
    sub_map_[task] = other;
    return *this;
}

#if defined(_CXX0X_)
HWSQLCmd& HWSQLCmd::SetSubCmd(const char* task, HWSQLCmd&& other)
{
    sub_map_[task] = std::move(other);
    return *this;
}
#endif


const HWSQLCmd& HWSQLCmd::GetSubCmd(const char* task) const
{
    SubMap::const_iterator it =  sub_map_.find(task);
    if (it != sub_map_.end()) {
        return it->second;
    }
    else {
        return Null;
    }
}

HWSQLCmd& HWSQLCmd::GetSubCmd(const char* task)
{
    return sub_map_[task];
}

int HWSQLCmd::Execute(IHWDBEnv* p_env) const
{
    if (!IsNull()) {
        int ret = p_env->Execute(sql_.c_str());
        if (ret >= 0) {
            for(SubMap::const_iterator it = sub_map_.begin();
                it != sub_map_.end(); ++it)
            {
                 (it->second.Execute(p_env) >= 0);
            }
        }
        return ret;
    }
    return 0;
}

RecordSetPtr HWSQLCmd::ExecuteRs(IHWDBEnv* p_env) const
{
    if (!IsNull()) {
        return p_env->ExecuteRs(sql_.c_str());
    }
    else {
        return NULL;
    }
}
