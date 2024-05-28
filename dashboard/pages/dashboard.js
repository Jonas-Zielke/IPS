"use client";

import { useSession, signOut } from "next-auth/react";

export default function DashboardPage() {
  const { data: session } = useSession();

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="flex justify-between items-center p-4 bg-white shadow">
        <h1 className="text-2xl">Dashboard</h1>
        <button
          onClick={() => signOut()}
          className="p-2 bg-red-500 text-white rounded"
        >
          Sign Out
        </button>
      </div>
      <div className="p-4">
        <h2 className="text-xl">Welcome, {session.user.name}</h2>
        {/* Your dashboard content */}
      </div>
    </div>
  );
}
