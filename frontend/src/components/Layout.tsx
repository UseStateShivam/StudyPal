import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  LayoutDashboard,
  FolderOpen,
  Layers,
  Search,
  HelpCircle,
  TrendingUp,
  Sparkles,
  LogOut
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const userStr = localStorage.getItem('studypal_user');
  const user = userStr ? JSON.parse(userStr) : null;

  const handleLogout = () => {
    localStorage.removeItem('studypal_token');
    localStorage.removeItem('studypal_user');
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Courses & Notes', path: '/courses', icon: FolderOpen },
    { label: 'Topic Explorer', path: '/topics', icon: Layers },
    { label: 'Search Notes', path: '/search', icon: Search },
    { label: 'Practice Quiz', path: '/quiz', icon: HelpCircle },
    { label: 'Mastery Progress', path: '/progress', icon: TrendingUp },
    { label: 'Revision Plan', path: '/recommendations', icon: Sparkles },
  ];

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col md:flex-row text-slate-100">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo / Header */}
          <div className="h-16 flex items-center px-6 border-b border-slate-800">
            <BookOpen className="w-6 h-6 text-sky-400 mr-2.5" />
            <span className="font-bold text-lg text-white tracking-tight">StudyPal</span>
            <span className="ml-2 px-1.5 py-0.5 text-[10px] uppercase font-bold tracking-wider bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded">
              ML v1.0
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3.5 py-2.5 rounded-xl text-sm font-medium transition ${
                    isActive
                      ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/30'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`
                }
              >
                <item.icon className="w-4 h-4 mr-3 shrink-0" />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* User profile & Logout */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center justify-between">
            <div className="truncate mr-2">
              <p className="text-xs font-semibold text-white truncate">{user?.display_name || 'Student'}</p>
              <p className="text-[11px] text-slate-500 truncate">{user?.email || 'demo@studypal.edu'}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-6 md:p-8">
        <div className="max-w-6xl mx-auto">{children}</div>
      </main>
    </div>
  );
};
