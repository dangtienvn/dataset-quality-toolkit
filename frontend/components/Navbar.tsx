"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-950/80 backdrop-blur-lg">
      <div className="flex items-center justify-between px-6 py-3 max-w-7xl mx-auto">
        <div className="flex items-center gap-8">
          <Link
            href="/dashboard"
            className="text-lg font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent"
          >
            AI SaaS
          </Link>
          <div className="flex gap-1">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 text-sm text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/chat"
              className="px-3 py-1.5 text-sm text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              Chat
            </Link>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-1.5 text-sm border border-gray-700 rounded-lg text-gray-400 hover:text-white hover:border-gray-500 transition-colors"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
