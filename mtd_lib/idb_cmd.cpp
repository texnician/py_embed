#include "idb_cmd.h"

const HWSQLCmd HWSQLCmd::Null = HWSQLCmd(NULL);

const HWDBResult HWDBResult::NoError = HWDBResult();

HWDBResult::HWDBResult()
    : has_error_(false), result_(0)
{}

bool HWDBResult::HasError() const
{
    return has_error_;
}

HWDBResult& HWDBResult::SetResult(int result)
{
    result_ = result;
    if (result < 0) {
        has_error_ = true;
    }
    return *this;
}

HWDBResult& HWDBResult::SetSubResult(const char* task, const HWDBResult& result)
{
    sub_result_map_[task] = result;
    if (result.HasError()) {
        has_error_ = true;
    }
    return *this;
}

#if defined(_CXX0X_)
HWDBResult& HWDBResult::SetSubResult(const char* task, HWDBResult&& result)
{
    sub_result_map_[task] = std::move(result);
    if (result.HasError()) {
        has_error_ = true;
    }
    return *this;
}
#endif

const HWDBResult& HWDBResult::GetSubResult(const char* task) const
{
    SubResultMap::const_iterator it = sub_result_map_.find(task);
    return it != sub_result_map_.end() ? it->second : NoError;
}

int HWDBResult::GetResult() const
{
    return result_;
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
    return it != sub_map_.end() ? it->second : Null;
}

HWSQLCmd& HWSQLCmd::GetSubCmd(const char* task)
{
    return sub_map_[task];
}

HWDBResult HWSQLCmd::Execute(IHWDBEnv* p_env) const
{
    HWDBResult result;
    if (!IsNull()) {
        result.SetResult(p_env->Execute(sql_.c_str()));
        if (!result.HasError()) {
            for(SubMap::const_iterator it = sub_map_.begin();
                it != sub_map_.end(); ++it)
            {
                result.SetSubResult(it->first.c_str(), it->second.Execute(p_env));
                if (result.HasError()) {
                    return result;
                }
            }
        }
    }
    return result;
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
