import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { BookOpenText, KeyRound, LogIn, RefreshCw, ShieldCheck, UserPlus, UserRound } from 'lucide-react';
import { getCaptcha, login, register } from '../api/authApi';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { getApiErrorMessage } from '../lib/apiError';

function LoginPage({ onLoginSuccess }) {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [captcha, setCaptcha] = useState(null);
  const [captchaCode, setCaptchaCode] = useState('');
  const [captchaLoading, setCaptchaLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadCaptcha = async () => {
    setCaptchaLoading(true);
    try {
      const data = await getCaptcha();
      setCaptcha(data);
      setCaptchaCode('');
    } catch (err) {
      setError('验证码加载失败，请确认后端和 Redis 已启动');
    } finally {
      setCaptchaLoading(false);
    }
  };

  useEffect(() => {
    loadCaptcha();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('请输入用户名和密码');
      return;
    }
    if (mode === 'register' && password.length < 6) {
      setError('注册密码至少需要 6 位');
      return;
    }
    if (!captcha?.captcha_id || !captchaCode.trim()) {
      setError('请输入验证码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result =
        mode === 'login'
          ? await login(username.trim(), password, captcha.captcha_id, captchaCode.trim())
          : await register(
              username.trim(),
              password,
              displayName.trim(),
              captcha.captcha_id,
              captchaCode.trim(),
            );
      if (result.authenticated) {
        onLoginSuccess(result.user);
      }
    } catch (err) {
      if (err.code === 'ERR_NETWORK') {
        setError('无法连接到后端服务，请确认 FastAPI 已启动');
      } else {
        setError(getApiErrorMessage(err, mode === 'login' ? '登录失败，请重试' : '注册失败，请重试'));
      }
      loadCaptcha();
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setError('');
    setPassword('');
    setCaptchaCode('');
    loadCaptcha();
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
            <p className="mt-1 text-sm text-muted-foreground">
              {mode === 'login' ? '登录后进入剧本工作台' : '注册账号后开始创作'}
            </p>
          </div>

          <div className="mb-5 grid grid-cols-2 gap-2 rounded-md border border-border bg-muted/50 p-1">
            <button
              type="button"
              onClick={() => switchMode('login')}
              className={`h-9 rounded-md text-sm font-medium transition-colors ${
                mode === 'login'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              登录
            </button>
            <button
              type="button"
              onClick={() => switchMode('register')}
              className={`h-9 rounded-md text-sm font-medium transition-colors ${
                mode === 'register'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              注册
            </button>
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

            {mode === 'register' && (
              <div className="flex flex-col gap-1.5">
                <label htmlFor="displayName" className="text-sm font-medium text-foreground">
                  显示名称
                </label>
                <div className="relative">
                  <UserPlus className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="displayName"
                    type="text"
                    placeholder="可选"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    autoComplete="name"
                    disabled={loading}
                    className="pl-9"
                  />
                </div>
              </div>
            )}

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

            <div className="flex flex-col gap-1.5">
              <label htmlFor="captcha" className="text-sm font-medium text-foreground">
                验证码
              </label>
              <div className="grid grid-cols-[1fr_auto_auto] gap-2">
                <div className="relative">
                  <ShieldCheck className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="captcha"
                    type="text"
                    placeholder="输入验证码"
                    value={captchaCode}
                    onChange={(e) => setCaptchaCode(e.target.value)}
                    autoComplete="off"
                    disabled={loading || captchaLoading}
                    className="pl-9 uppercase"
                  />
                </div>
                <div className="flex h-9 w-[120px] items-center justify-center overflow-hidden rounded-md border border-border bg-cyan-50">
                  {captcha?.image ? (
                    <img src={captcha.image} alt="验证码" className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-xs text-muted-foreground">加载中</span>
                  )}
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  loading={captchaLoading}
                  onClick={loadCaptcha}
                  disabled={loading}
                  aria-label="刷新验证码"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">验证码有效期 1 分钟。</p>
            </div>

            {error && (
              <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-destructive" role="alert">
                {error}
              </p>
            )}

            <Button type="submit" loading={loading} className="w-full">
              {mode === 'login' ? <LogIn className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
              {loading ? (mode === 'login' ? '登录中…' : '注册中…') : mode === 'login' ? '登录' : '注册并登录'}
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}

export default LoginPage;
