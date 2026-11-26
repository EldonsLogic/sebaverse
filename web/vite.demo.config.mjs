import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

const webRoot = fileURLToPath(new URL('.', import.meta.url));
const allowedPrefixes = ['/demo/', '/src/demo/', '/brand/', '/@vite/', '/@id/', '/node_modules/'];

export default defineConfig({
  root: webRoot,
  envDir: false,
  envPrefix: 'SEBAVERSE_DEMO_PUBLIC_',
  plugins: [{
    name: 'sebaverse-loopback-demo-only',
    configResolved(config) {
      if (config.command !== 'serve' || config.mode !== 'demonstration' || config.server.host !== '127.0.0.1' || config.server.port !== 5174 || config.server.proxy) {
        throw new Error('The teaching demo requires its dedicated loopback-only development invocation.');
      }
    },
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const path = (request.url || '').split('?')[0];
        if (path === '/' || path === '/demo') {
          response.writeHead(302, { Location: '/demo/index.html' });
          response.end();
          return;
        }
        if (!allowedPrefixes.some(prefix => path.startsWith(prefix))) {
          response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
          response.end('Local demonstration only.');
          return;
        }
        if (path === '/demo/') request.url = '/demo/index.html';
        next();
      });
    },
  }],
  server: {
    host: '127.0.0.1',
    port: 5174,
    strictPort: true,
    cors: false,
    allowedHosts: ['127.0.0.1'],
    fs: { strict: true, allow: [webRoot] },
    hmr: { host: '127.0.0.1', port: 5174 },
    headers: {
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      'Content-Security-Policy': "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; font-src 'self'; connect-src 'self' ws://127.0.0.1:5174; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
    },
  },
  // The default production config remains the sole application build entry.
});
