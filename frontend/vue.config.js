module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_URL || 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api/v1'
        }
      }
    },
    port: 8081
  },
  css: {
    loaderOptions: {
      sass: {
        additionalData: `
          @import "@/assets/css/variables.scss";
        `
      }
    }
  },
  configureWebpack: {
    performance: {
      hints: process.env.NODE_ENV === 'production' ? "warning" : false
    }
  },
  pwa: {
    name: 'Centro Cultural Banreservas',
    themeColor: '#512da8',
    msTileColor: '#512da8',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black-translucent',
    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      exclude: [/\.map$/, /_redirects/, /_headers/],
      skipWaiting: true
    },
    manifestOptions: {
      display: 'standalone',
      background_color: '#ffffff',
      icons: [
        {
          src: './img/icons/android-chrome-192x192.png',
          sizes: '192x192',
          type: 'image/png'
        },
        {
          src: './img/icons/android-chrome-512x512.png',
          sizes: '512x512',
          type: 'image/png'
        }
      ]
    }
  },
  lintOnSave: false
}; 