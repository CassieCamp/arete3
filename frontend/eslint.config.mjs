import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Literal[value=/^#[0-9a-fA-F]/]",
          message: "Use CSS custom properties instead of hardcoded hex colors"
        },
        {
          selector: "Literal[value=/^rgb\\(/]",
          message: "Use CSS custom properties instead of rgb() functions"
        },
        {
          selector: "Literal[value=/^hsl\\(/]",
          message: "Use CSS custom properties instead of hsl() functions"
        },
        {
          selector: "CallExpression[callee.type='MemberExpression'][callee.property.name='filter'][callee.object.name=/.*NAVIGATION$/]",
          message: "Do not use .filter() on navigation arrays. Use getMainNavigationForRole() or getMenuNavigationForRole() instead to prevent role leakage."
        },
        {
          selector: "CallExpression[callee.type='MemberExpression'][callee.property.name='filter'] > MemberExpression[object.name='MAIN_NAVIGATION']",
          message: "Do not filter MAIN_NAVIGATION directly. Use getMainNavigationForRole() to prevent role leakage."
        },
        {
          selector: "CallExpression[callee.type='MemberExpression'][callee.property.name='filter'] > MemberExpression[object.name='MENU_NAVIGATION']",
          message: "Do not filter MENU_NAVIGATION directly. Use getMenuNavigationForRole() to prevent role leakage."
        }
      ]
    }
  }
];

export default eslintConfig;
