import {defineConfig} from 'vite';
export default defineConfig({
  esbuild:{jsx:'automatic'},
  server:{proxy:{'/api':{target:'http://127.0.0.1:5000',changeOrigin:false}}},
  build:{rollupOptions:{onwarn(warning,warn){if(warning.code==='MODULE_LEVEL_DIRECTIVE')return;warn(warning)}}}
});
