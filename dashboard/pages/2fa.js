"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";

export default function TwoFactorAuthPage() {
  const { data: session } = useSession();
  const [secret, setSecret] = useState("");
  const [qrCode, setQrCode] = useState("");
  const [token, setToken] = useState("");
  const [verified, setVerified] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (session && session.user) {
      fetch(`/api/auth/2fa?userId=${session.user.id}`)
        .then((res) => res.json())
        .then((data) => {
          setSecret(data.secret);
          setQrCode(data.data_url);
        });
    }
  }, [session]);

  const verifyToken = async () => {
    const res = await fetch("/api/auth/2fa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, secret, userId: session.user.id }),
    });
    const data = await res.json();
    if (data.verified) {
      setVerified(true);
      router.push("/dashboard");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-96">
        <h2 className="text-2xl mb-4">Two-Factor Authentication</h2>
        {qrCode && (
          <div className="mb-4">
            <img src={qrCode} alt="QR Code" />
          </div>
        )}
        <div className="mb-4">
          <label className="block mb-1">Token</label>
          <input
            type="text"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          />
        </div>
        <button
          onClick={verifyToken}
          className="w-full p-2 bg-blue-500 text-white rounded"
        >
          Verify
        </button>
        {verified && <div className="mt-4 text-green-600">Token verified!</div>}
      </div>
    </div>
  );
}
