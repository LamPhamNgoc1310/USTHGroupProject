const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');

module.exports = {
  entry: './src/main.js',
  module: {
    rules: require('./webpack.rules'),
  },
  externals: {
    'electron-reload': 'commonjs electron-reload',
  },
  devServer: {
    historyApiFallback: true
  },
  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        { from: 'src/neco.png', to: 'dist/neco.png' },
        { from: 'src/preload.js', to: 'dist/preload.js' },
      ],
    }),
    
    // Add HtmlWebpackPlugin for injecting the content security policy
    new HtmlWebpackPlugin({
      template: './src/index.html',
      inject: true,
      meta: {
        'Content-Security-Policy': {
          'http-equiv': 'Content-Security-Policy',
          'content': "default-src 'self' 'unsafe-eval' 'unsafe-inline' http://localhost:* ws://localhost:*;",
        },
      },
    }),

    new webpack.DefinePlugin({
      'process.env.PYTHON_SCRIPT_PATH': JSON.stringify(
        path.resolve(__dirname, '..', '..', 'demo v2 (cnn + mediapipe)', 'App_v1', 'main.py')
      ),
    }),
  ],
};
