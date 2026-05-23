const { spawn } = require('child_process');

console.log('\x1b[33m⚡ Starting Cloudflare Development Tunnel...\x1b[0m');

// Make sure cloudflared-linux-amd64 has executable permissions
try {
  const chmod = spawn('chmod', ['+x', './cloudflared-linux-amd64']);
  chmod.on('close', () => {
    startTunnel();
  });
} catch (err) {
  startTunnel();
}

function startTunnel() {
  const child = spawn('./cloudflared-linux-amd64', ['tunnel', '--url', 'http://localhost:5000']);

  child.stdout.on('data', (data) => {
    process.stdout.write(data);
  });

  child.stderr.on('data', (data) => {
    const line = data.toString();
    const match = line.match(/(https:\/\/[a-z0-9-]+\.trycloudflare\.com)/i);
    if (match) {
      const url = match[1];
      console.log('\n\x1b[32m============================================================\x1b[0m');
      console.log(`\x1b[32;1m✨ Cloudflare Development Tunnel Active ✨\x1b[0m`);
      console.log(`\x1b[36m🔗 Tunnel URL:\x1b[0m \x1b[4;34m${url}\x1b[0m`);
      console.log('\x1b[32m============================================================\x1b[0m\n');
    } else {
      process.stderr.write(data);
    }
  });

  child.on('close', (code) => {
    console.log(`\x1b[31mTunnel process exited with code ${code}\x1b[0m`);
  });
}
