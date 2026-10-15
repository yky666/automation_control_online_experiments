import {defineConfig} from 'vite';
export default defineConfig({base:process.env.VITE_BASE_PATH||'/',server:{port:5173,proxy:{'/api':'http://127.0.0.1:8765','/sources':'http://127.0.0.1:8765'}},build:{outDir:'dist',rollupOptions:{output:{manualChunks:{plotly:['plotly.js-dist-min'],math:['katex']}}}}});
