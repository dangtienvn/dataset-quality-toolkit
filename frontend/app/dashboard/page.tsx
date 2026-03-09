"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import AuthGuard from "@/components/AuthGuard";
import api from "@/lib/api";

interface DashboardData {
  tenant: { name: string; plan: string };
  users: { total: number };
  ai_usage: { total_calls: number; total_input_tokens: number; total_output_tokens: number; total_cost: string };
  subscription: { status: string };
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 bg-gray-800 rounded-lg w-64" />
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-gray-900 rounded-2xl border border-gray-800" />
        ))}
      </div>
      <div className="h-40 bg-gray-900 rounded-2xl border border-gray-800" />
    </div>
  );
}

function PlanBadge({ plan }: { plan: string }) {
  const colors: Record<string, string> = {
    free: "bg-gray-700 text-gray-300",
    starter: "bg-violet-500/20 text-violet-300",
    pro: "bg-indigo-500/20 text-indigo-300",
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[plan] || colors.free}`}>
      {plan}
    </span>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    api.get("/api/v1/admin/dashboard").then((res) => setData(res.data)).catch(() => {});
  }, []);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-950">
        <Navbar />
        <main className="max-w-6xl mx-auto px-6 py-10">
          {!data ? (
            <Skeleton />
          ) : (
            <>
              <h1 className="text-2xl font-bold mb-8">Welcome back 👋</h1>

              {/* Stat cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
                <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                  <p className="text-sm text-gray-400 mb-1">Plan</p>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-bold capitalize">{data.tenant.plan}</span>
                    <PlanBadge plan={data.tenant.plan} />
                  </div>
                </div>
                <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                  <p className="text-sm text-gray-400 mb-1">Total AI Calls</p>
                  <span className="text-2xl font-bold">{data.ai_usage.total_calls}</span>
                </div>
                <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                  <p className="text-sm text-gray-400 mb-1">Users</p>
                  <span className="text-2xl font-bold">{data.users.total}</span>
                </div>
              </div>

              {/* Quick Actions */}
              <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link
                  href="/chat"
                  className="flex items-center gap-4 bg-gray-900 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-colors group"
                >
                  <span className="text-2xl">🤖</span>
                  <div>
                    <p className="font-medium group-hover:text-violet-400 transition-colors">
                      AI Chat
                    </p>
                    <p className="text-sm text-gray-500">Start a conversation with AI</p>
                  </div>
                </Link>
                <button
                  onClick={() => {
                    api.get("/api/v1/gdpr/export").then((res) => {
                      const blob = new Blob([JSON.stringify(res.data, null, 2)], {
                        type: "application/json",
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = "gdpr-export.json";
                      a.click();
                      URL.revokeObjectURL(url);
                    });
                  }}
                  className="flex items-center gap-4 bg-gray-900 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-colors group text-left"
                >
                  <span className="text-2xl">🛡️</span>
                  <div>
                    <p className="font-medium group-hover:text-violet-400 transition-colors">
                      GDPR Export
                    </p>
                    <p className="text-sm text-gray-500">Download your data</p>
                  </div>
                </button>
              </div>
            </>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}
