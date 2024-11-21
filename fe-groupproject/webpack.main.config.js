const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  /**
   * This is the main entry point for your application, it's the first file
   * that runs in the main process.
   */
  entry: './src/main.js',
  // Put your normal webpack config below here
  module: {
    rules: require('./webpack.rules'),
  },
  externals: {
    'electron-reload': 'commonjs electron-reload'
  },  
  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        { from: 'src/neco.png', to: 'dist/neco.png' },  // Adjust the path according to your structure
        { from: 'src/preload.js', to: 'dist/preload.js' },  // Adjust the path according to your structure
      ],
    }),
  ],
};
