import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import ChatInterface from './components/ChatInterface';
import AdminDashboard from './components/AdminDashboard';
import CacheViewer from './components/CacheViewer';
import Login from './components/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import { MessageSquare, Settings, LayoutDashboard, Cpu, Database, LogOut } from 'lucide-react';
import { clsx } from 'clsx';

const NavLink = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={clsx(
        "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden",
        isActive
          ? "text-white bg-white/10 shadow-lg shadow-primary/10"
          : "text-gray-400 hover:text-white hover:bg-white/5"
      )}
    >
      {isActive && (
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-r-full" />
      )}
      <Icon size={20} className={clsx("transition-transform duration-300 group-hover:scale-110", isActive ? "text-primary" : "text-gray-500 group-hover:text-gray-300")} />
      <span className="font-medium z-10">{label}</span>
    </Link>
  );
};

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { userRole, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(userRole)) {
    // Redirect to appropriate home page based on role
    return <Navigate to={userRole === 'admin' ? '/admin' : '/'} replace />;
  }

  return children;
};

const Layout = () => {
  const { userRole, logout } = useAuth();
  const location = useLocation();

  // Don't show layout on login page
  if (location.pathname === '/login') {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
      </Routes>
    );
  }

  return (
    <div className="flex h-screen bg-background text-gray-100 font-sans overflow-hidden relative selection:bg-primary/30">
      {/* Noise Overlay */}
      <div className="absolute inset-0 bg-noise pointer-events-none z-50 opacity-20 mix-blend-overlay" />
      {/* Background Ambient Glow */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[120px] pointer-events-none opacity-50" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-accent/20 rounded-full blur-[120px] pointer-events-none opacity-50" />

      {/* Sidebar */}
      <aside className="w-72 glass border-r-0 z-20 flex flex-col relative">
        <div className="p-8 pb-4">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
              <Cpu className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-heading font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-gray-400 tracking-tight">
                PocketLLM
              </h1>
              <p className="text-[10px] uppercase tracking-wider text-gray-500 font-semibold">Local Inference</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-6">
          {userRole === 'user' && (
            <NavLink to="/" icon={MessageSquare} label="Chat" />
          )}
          {userRole === 'admin' && (
            <>
              <NavLink to="/admin" icon={LayoutDashboard} label="Dashboard" />
              <NavLink to="/cache" icon={Database} label="Cache" />
            </>
          )}
        </nav>

        <div className="px-4 pb-2">
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-300 group"
          >
            <LogOut size={20} className="transition-transform duration-300 group-hover:scale-110" />
            <span className="font-medium">Logout</span>
          </button>
        </div>

        <div className="p-4 m-4 mt-2 rounded-2xl bg-gradient-to-br from-gray-900/50 to-black/50 border border-white/5 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <div className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-500 animate-ping opacity-75"></div>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-300">System Online</p>
              <p className="text-[10px] text-gray-500">v1.0.0 • {userRole === 'admin' ? 'Admin Mode' : 'User Mode'}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        <header className="h-20 flex-none flex items-center justify-between px-8 border-b border-white/5 bg-background/50 backdrop-blur-sm z-20">
          <div>
            <h2 className="text-xl font-heading font-medium text-white/90 tracking-tight">
              {userRole === 'admin' ? 'System Administration' : 'Workspace'}
            </h2>
            <p className="text-xs text-gray-500">
              {userRole === 'admin' ? 'Monitor performance and manage resources' : 'Manage your local models and sessions'}
            </p>
          </div>
          <div className="flex items-center gap-4">
          </div>
        </header>

        <div className="flex-1 min-h-0 relative">
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm">
            <Routes>
              <Route path="/" element={
                <ProtectedRoute allowedRoles={['user']}>
                  <ChatInterface />
                </ProtectedRoute>
              } />
              <Route path="/admin" element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="/cache" element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <CacheViewer />
                </ProtectedRoute>
              } />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </div>
      </main>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<Layout />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;

