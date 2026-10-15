import {defineConfig} from 'vitest/config';
export default defineConfig({test:{environment:'jsdom',include:['tests/*.test.jsx','tests/*.test.js'],testTimeout:60000,setupFiles:['./tests/dom-setup.js']}});
