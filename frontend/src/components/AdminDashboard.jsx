import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Database,
  FileText,
  Loader2,
  RefreshCw,
  ShieldCheck,
  UsersRound,
} from 'lucide-react';
import {
  fetchAdminGenerations,
  fetchAdminStats,
  fetchAdminUsers,
  updateAdminUser,
} from '../api/adminApi';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { getApiErrorMessage } from '../lib/apiError';

const statItems = [
  { key: 'user_count', label: '用户总数', icon: UsersRound },
  { key: 'active_user_count', label: '启用用户', icon: ShieldCheck },
  { key: 'project_count', label: '项目数', icon: FileText },
  { key: 'generation_count', label: '生成次数', icon: Activity },
  { key: 'generated_script_count', label: '缓存剧本', icon: Database },
  { key: 'mock_generation_count', label: 'Mock 次数', icon: RefreshCw },
];

function AdminDashboard({ toast }) {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingUserId, setSavingUserId] = useState(null);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [statsData, usersData, generationsData] = await Promise.all([
        fetchAdminStats(),
        fetchAdminUsers(),
        fetchAdminGenerations(80),
      ]);
      setStats(statsData);
      setUsers(usersData.users || []);
      setRecords(generationsData.records || []);
    } catch (error) {
      toast.error(getApiErrorMessage(error, '管理后台数据加载失败'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const latestRecord = records[0];
  const mockRate = useMemo(() => {
    if (!stats?.generation_count) {
      return '0%';
    }
    return `${Math.round((stats.mock_generation_count / stats.generation_count) * 100)}%`;
  }, [stats]);

  const handleUserPatch = async (user, patch) => {
    setSavingUserId(user.id);
    try {
      const updated = await updateAdminUser(user.id, patch);
      setUsers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      toast.success('用户状态已更新');
    } catch (error) {
      toast.error(getApiErrorMessage(error, '用户更新失败'));
    } finally {
      setSavingUserId(null);
    }
  };

  if (loading && !stats) {
    return (
      <main className="admin-shell">
        <div className="admin-loading">
          <Loader2 className="h-7 w-7 animate-spin" />
          <span>正在加载管理后台</span>
        </div>
      </main>
    );
  }

  return (
    <main className="admin-shell">
      <section className="admin-hero">
        <div>
          <p className="workflow-kicker">Admin console</p>
          <h2>系统管理后台</h2>
          <p>查看用户、生成记录和系统运行数据。</p>
        </div>
        <Button variant="outline" onClick={loadAdminData} loading={loading}>
          <RefreshCw className="h-4 w-4" />
          刷新数据
        </Button>
      </section>

      <section className="admin-stats-grid">
        {statItems.map((item) => {
          const Icon = item.icon;
          return (
            <div className="admin-stat-card" key={item.key}>
              <span>
                <Icon className="h-4 w-4" />
              </span>
              <p>{item.label}</p>
              <strong>{stats?.[item.key] ?? 0}</strong>
            </div>
          );
        })}
      </section>

      <section className="admin-insight-grid">
        <div className="admin-panel">
          <div className="admin-panel-head">
            <div>
              <h3>用户管理</h3>
              <p>管理账号角色与启用状态。</p>
            </div>
            <Badge variant="secondary">{users.length} 个用户</Badge>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>用户</th>
                  <th>角色</th>
                  <th>状态</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id || user.username}>
                    <td>
                      <strong>{user.display_name || user.username}</strong>
                      <span>{user.username}</span>
                    </td>
                    <td>
                      <select
                        value={user.role}
                        disabled={savingUserId === user.id}
                        onChange={(event) => handleUserPatch(user, { role: event.target.value })}
                      >
                        <option value="admin">admin</option>
                        <option value="author">author</option>
                      </select>
                    </td>
                    <td>
                      <Badge variant={user.status === 'active' ? 'success' : 'warning'}>
                        {user.status === 'active' ? '启用' : '禁用'}
                      </Badge>
                    </td>
                    <td>{user.created_at || '-'}</td>
                    <td>
                      <Button
                        variant="outline"
                        size="sm"
                        loading={savingUserId === user.id}
                        onClick={() =>
                          handleUserPatch(user, {
                            status: user.status === 'active' ? 'disabled' : 'active',
                          })
                        }
                      >
                        {user.status === 'active' ? '禁用' : '启用'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="admin-side-panel">
          <h3>运行概览</h3>
          <div>
            <span>Mock 占比</span>
            <strong>{mockRate}</strong>
          </div>
          <div>
            <span>最新生成</span>
            <strong>{latestRecord?.project_title || '暂无记录'}</strong>
          </div>
          <div>
            <span>最新模型</span>
            <strong>{latestRecord?.model_name || '-'}</strong>
          </div>
        </aside>
      </section>

      <section className="admin-panel">
        <div className="admin-panel-head">
          <div>
            <h3>生成记录管理</h3>
            <p>查看最近生成的剧本、缓存键、模型和来源。</p>
          </div>
          <Badge variant="secondary">{records.length} 条记录</Badge>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>项目</th>
                <th>章节</th>
                <th>模型</th>
                <th>来源</th>
                <th>YAML</th>
                <th>生成时间</th>
                <th>缓存键</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.cache_key}>
                  <td>
                    <strong>{record.project_title || '未命名项目'}</strong>
                    <span>Project #{record.project_id || '-'}</span>
                  </td>
                  <td>{record.chapter_count}</td>
                  <td>{record.model_name || '-'}</td>
                  <td>
                    <Badge variant={record.used_mock ? 'warning' : 'success'}>
                      {record.used_mock ? 'Mock' : 'DeepSeek'}
                    </Badge>
                  </td>
                  <td>{record.yaml_line_count} 行</td>
                  <td>{record.created_at || '-'}</td>
                  <td>
                    <code>{record.cache_key.slice(0, 12)}...</code>
                  </td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr>
                  <td colSpan="7" className="admin-empty">
                    暂无生成记录
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

export default AdminDashboard;
