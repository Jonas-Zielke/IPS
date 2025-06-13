import fs from 'fs';
import path from 'path';

const secretsFile = path.join(process.cwd(), 'dashboard', 'userSecrets.json');
let secrets = {};

function loadFromDisk() {
  if (fs.existsSync(secretsFile)) {
    try {
      const raw = fs.readFileSync(secretsFile, 'utf-8');
      secrets = JSON.parse(raw);
    } catch {
      secrets = {};
    }
  }
}

function saveToDisk() {
  try {
    fs.writeFileSync(secretsFile, JSON.stringify(secrets, null, 2));
  } catch {
    // ignore write errors
  }
}

loadFromDisk();

export function getSecret(userId) {
  return secrets[userId];
}

export function setSecret(userId, secret) {
  secrets[userId] = secret;
  saveToDisk();
}
