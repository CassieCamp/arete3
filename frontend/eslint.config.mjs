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
        }
      ]
    }
  }
];

export default eslintConfig;
