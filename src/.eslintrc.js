const globals = require("globals");

module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "standard-with-typescript",
    "prettier"
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: "module",
  },
  plugins: [
    "react",
    "@typescript-eslint",
    "prettier"
  ],
  rules: {
    "prettier/prettier": ["error", { "endOfLine": "auto" }],
  },
  globals: globals.browser
};