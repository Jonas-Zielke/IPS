import speakeasy from "speakeasy";
import QRCode from "qrcode";

const userSecrets = {};

export default (req, res) => {
  const { token, secret, userId } = req.body;

  if (req.method === "POST") {
    const verified = speakeasy.totp.verify({
      secret,
      encoding: "base32",
      token,
    });

    if (verified && userId) {
      userSecrets[userId] = secret; // Save the secret after verification
    }

    res.status(200).json({ verified });
  } else {
    const userId = req.query.userId;
    if (userSecrets[userId]) {
      // User already has a secret, don't generate a new one
      res.status(200).json({ secret: userSecrets[userId], data_url: null });
    } else {
      // Generate a new secret
      const secret = speakeasy.generateSecret({ length: 20 });
      QRCode.toDataURL(secret.otpauth_url, (err, data_url) => {
        res.status(200).json({ secret: secret.base32, data_url });
      });
    }
  }
};
