const { defineConfig } = require('@vue/cli-service');
const webpack = require('webpack');

module.exports = defineConfig({
  transpileDependencies: true,
  pwa: {
    name: 'FFYouTube',
    themeColor: '#00D5CB',
    msTileColor: '#1B1B1B',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black-translucent',
    iconPaths: {
      faviconSVG: null,
      favicon32: 'img/icons/favicon-32x32.png',
      favicon16: 'img/icons/favicon-16x16.png',
      appleTouchIcon: 'img/icons/apple-touch-icon.png',
      maskIcon: 'img/icons/safari-pinned-tab.svg',
      msTileImage: 'img/icons/msapplication-icon-144x144.png',
    },
    manifestOptions: {
      id: '/',
      name: 'FFYouTube',
      short_name: 'FFYouTube',
      description: 'A clean, distraction-free way to watch YouTube videos.',
      lang: 'en',
      dir: 'ltr',
      start_url: '/#/',
      scope: '/',
      display: 'standalone',
      display_override: ['window-controls-overlay', 'standalone', 'minimal-ui'],
      orientation: 'any',
      background_color: '#1B1B1B',
      theme_color: '#00D5CB',
      categories: ['entertainment', 'video', 'utilities'],
      prefer_related_applications: false,
      icons: [
        {
          src: '/img/icons/android-chrome-192x192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: '/img/icons/android-chrome-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: '/img/icons/android-chrome-maskable-192x192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'maskable',
        },
        {
          src: '/img/icons/android-chrome-maskable-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable',
        },
      ],
      shortcuts: [
        {
          name: 'Choose a video',
          short_name: 'Open video',
          description: 'Paste a YouTube link and start watching.',
          url: '/#/',
          icons: [
            {
              src: '/img/icons/android-chrome-192x192.png',
              sizes: '192x192',
              type: 'image/png',
            },
          ],
        },
      ],
    },
    workboxOptions: {
      cleanupOutdatedCaches: true,
      navigateFallback: '/index.html',
      navigateFallbackDenylist: [
        /^\/api\//,
        /^\/auth\//,
        /^\/proxy\//,
      ],
    },
  },
  css: {
    loaderOptions: {
      scss: {
        additionalData: '@import "@/assets/variables.scss";',
      },
    },
  },
  devServer: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: 'all',
    proxy: {
      '/auth/': {
        target: 'https://id.xho.st/',
        changeOrigin: true,
        pathRewrite: { '^/auth': '' },
      },
      '/api/': {
        target: 'http://localhost:8090/api/',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
      },
      '/proxy/': {
        target: 'http://localhost:8090/proxy/',
        changeOrigin: true,
        pathRewrite: { '^/proxy': '' },
      },
    },
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
      }),
    ],
    module: {
      rules: [
        {
          test: /\.ya?ml$/,
          use: 'yaml-loader',
        },
      ],
    },
  },
});
