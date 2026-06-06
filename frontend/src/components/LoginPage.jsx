import { useState } from 'react';
import { motion } from 'motion/react';
import { BookOpenText, KeyRound, LogIn, UserRound } from 'lucide-react';
import { login } from '../api/authApi';
import { Button } from './ui/button';
import { Input } from './ui/input';

function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('请输入用户名和密码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login(username, password);
      if (result.authenticated) {
        onLoginSuccess(result.user);
      }
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (detail) {
        setError(detail);
      } else if (err.code === 'ERR_NETWORK') {
        setError('无法连接到后端服务，请确认 FastAPI 已启动');
      } else {
        setError('登录失败，请重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="login-card"
      >
        <div className="login-visual">
          <div className="brand-lockup">
            <div className="brand-mark">
              <BookOpenText className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold leading-none">Novel2Script</h1>
              <p className="mt-1.5 text-sm text-teal-100">AI 小说转结构化剧本</p>
            </div>
          </div>

          <div className="mt-16 max-w-md">
            <p className="text-sm font-semibold uppercase text-amber-200">Script Studio</p>
            <p className="mt-4 text-4xl font-semibold leading-tight">
              从章节到分场，
              <br />
              把故事铺成可改稿的 YAML。
            </p>
          </div>

          <div className="absolute bottom-16 left-8 right-8 z-10 grid gap-2 text-sm text-teal-50/85">
            <div className="flex items-center justify-between rounded-md border border-white/15 bg-white/10 px-3 py-2">
              <span>characters</span>
              <span className="text-amber-200">ready</span>
            </div>
            <div className="flex items-center justify-between rounded-md border border-white/15 bg-white/10 px-3 py-2">
              <span>scenes</span>
              <span className="text-amber-200">structured</span>
            </div>
          </div>
        </div>

        <div className="login-form-panel">
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-semibold text-foreground">Novel2Script</h1>
            <p className="mt-1 text-sm text-muted-foreground">登录后进入剧本工作台</p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="username" className="text-sm font-medium text-foreground">
                用户名
              </label>
              <div className="relative">
                <UserRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="username"
                  type="text"
                  placeholder="用户名"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  disabled={loading}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="password" className="text-sm font-medium text-foreground">
                密码
              </label>
              <div className="relative">
                <KeyRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  disabled={loading}
                  className="pl-9"
                />
              </div>
            </div>

            {error && (
              <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-destructive" role="alert">
                {error}
              </p>
            )}

            <Button type="submit" loading={loading} className="w-full">
              <LogIn className="h-4 w-4" />
              {loading ? '登录中…' : '登录'}
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}

export default LoginPage;
