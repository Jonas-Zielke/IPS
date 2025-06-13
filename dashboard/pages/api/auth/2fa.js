import speakeasy from "speakeasy";
import QRCode from "qrcode";
import { getSecret, setSecret } from "../../../utils/secretStore";

export default (req, res) => {
  const { token, secret, userId } = req.body || {};

  if (req.method === "POST") {
    const verified = speakeasy.totp.verify({
      secret,
      encoding: "base32",
      token,
    });

    if (verified && userId) {
      setSecret(userId, secret); // Persist the secret after verification
    }

    res.status(200).json({ verified });
  } else {
    const userId = req.query.userId;
    const existing = getSecret(userId);
    if (existing) {
      // User already has a secret, don't generate a new one
      res.status(200).json({ secret: existing, data_url: null });
    } else {
      // Generate a new secret
      const secret = speakeasy.generateSecret({ length: 20 });
      QRCode.toDataURL(secret.otpauth_url, (err, data_url) => {
        res.status(200).json({ secret: secret.base32, data_url });
      });
    }
  }
};
