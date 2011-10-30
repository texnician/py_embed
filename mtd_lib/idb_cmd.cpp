#include "idb_cmd.h"

const HWSQLCmd HWSQLCmd::Null = HWSQLCmd(NULL);

const HWDBResult HWDBResult::NoError = HWDBResult();

const HWDBRecordSet HWDBRecordSet::Empty = HWDBRecordSet();

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

HWDBRecordSet::HWDBRecordSet()
    : cursor_(NULL)
{}

bool HWDBRecordSet::IsEmpty() const
{
    if (cursor_ == NULL) {
        bool is_all_sub_empty = true;
        for (SubRecordSetMap::const_iterator it = sub_rs_map_.begin();
             it != sub_rs_map_.end(); ++it)
        {
            if (!it->second.IsEmpty()) {
                is_all_sub_empty = false;
                break;
            }
        }
        return is_all_sub_empty;
    }
    else {
        return false;
    }
}

HWDBRecordSet& HWDBRecordSet::SetCursor(const IHWDBCursorPtr& cursor)
{
    cursor_ = cursor;
    return *this;
}

#if defined(_CXX0X_)    
HWDBRecordSet& HWDBRecordSet::SetCursor(IHWDBCursorPtr&& cursor)
{
    cursor_ = std::move(cursor);
    return *this;
}
#endif

IHWDBCursorPtr HWDBRecordSet::GetCursor() const
{
    return cursor_;
}

HWDBRecordSet& HWDBRecordSet::SetSubRecordSet(const char* task, const HWDBRecordSet& rs)
{
    if (!SetSubResult(task, rs).HasError())
        sub_rs_map_[task] = rs;
    return *this;
}

#if defined(_CXX0X_)
HWDBRecordSet& HWDBRecordSet::SetSubRecordSet(const char* task, HWDBRecordSet&& rs)
{
    if (!SetSubResult(task, std::move(rs)).HasError())
        sub_rs_map_[task] = std::move(rs);
    return *this;
}
#endif

const HWDBRecordSet& HWDBRecordSet::GetSubRecordSet(const char* task) const
{
    SubRecordSetMap::const_iterator it = sub_rs_map_.find(task);
    return it != sub_rs_map_.end() ? it->second : Empty;
}

HWSQLCmd::HWSQLCmd(const char* sql)
    : sql_(sql == NULL ? "" : sql)
{}

bool HWSQLCmd::IsNull() const
{
    return sql_.empty();
}

HWSQLCmd& HWSQLCmd::SetSQL(const char* sql)
{
    sql_ = sql;
    return *this;
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
            for (SubMap::const_iterator it = sub_map_.begin();
                it != sub_map_.end(); ++it)
            {
                if (result.SetSubResult(it->first.c_str(), it->second.Execute(p_env)).HasError()) {
                    return result;
                }
            }
        }
    }
    return result;
}

HWDBRecordSet HWSQLCmd::ExecuteRs(IHWDBEnv* p_env) const
{
    if (!IsNull()) {
        IHWDBCursorPtr p_cursor;
        int result = p_env->ExecuteRs(sql_.c_str(), p_cursor);
        HWDBRecordSet rs;
        if (!rs.SetCursor(p_cursor).SetResult(result).HasError()) {
            for (SubMap::const_iterator it = sub_map_.begin();
                 it != sub_map_.end(); ++it) {
                if (rs.SetSubRecordSet(it->first.c_str(), it->second.ExecuteRs(p_env)).HasError()) {
                    return rs;
                }
            }
        }
        return rs;
    }
    else {
        return HWDBRecordSet();
    }
}

HWSQLCmd& HWSQLCmd::Reset()
{
    sql_ = (char*)NULL;
    sub_map_.clear();
    return *this;
}

std::string HWSQLCmd::DumpSQL(const HWDBResult& result, const char* name, int level) const
{
    #define MAX_SQL_LEN 2048
    #define SNPRINTF _snprintf

    int idx = 0;
    char buf[MAX_SQL_LEN];

    // If first level, print header
    if (level == 0) {
        idx = SNPRINTF(buf, MAX_SQL_LEN, "\n======== HWSQLCmd Dump ==========\n");
    }
    // print indent
    for (int i = 0; i < level*2; ++i) {
        idx = SNPRINTF(buf+idx, MAX_SQL_LEN-idx, "%c", ' ');
    }
    // print conent
    idx = SNPRINTF(buf+idx, MAX_SQL_LEN-idx, "%s:%d: %s\n",
                   name == NULL ? "root" : name, result.GetResult(), sql_.c_str());
    // print sub cmds
    for (SubMap::const_iterator it = sub_map_.begin(); it != sub_map_.end(); ++it) {
        idx = SNPRINTF(buf+idx, MAX_SQL_LEN-idx, "%s",
                       it->second.DumpSQL(result.GetSubResult(it->first.c_str()),
                                          it->first.c_str(),
                                          level+1).c_str());
    }
    // If first level, print foot
    if (level == 0) {
        idx = SNPRINTF(buf+idx, MAX_SQL_LEN-idx, "%s",
                       "==== HWSQLCmd Dump ends here ====\n");
    }
    return buf;
}
