import type { Config } from 'jest'
import nextJest from 'next/jest.js'

const createJestConfig = nextJest({ dir: './' })

const config: Config = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
}

// createJestConfig returns an async function; wrap it so we can override
// transformIgnorePatterns AFTER next/jest has set its own defaults.
const jestConfig = createJestConfig(config)

export default async () => {
  const cfg = await jestConfig()
  cfg.transformIgnorePatterns = [
    'node_modules/(?!(bail|baseline-browser-mapping|ccount|character-entities|character-entities-html4|character-entities-legacy|character-reference-invalid|comma-separated-tokens|decode-named-character-reference|devlop|entities|escape-string-regexp|estree-util-is-identifier-name|get-package-type|hast-util-to-jsx-runtime|hast-util-whitespace|html-url-attributes|is-alphabetical|is-alphanumerical|is-decimal|is-hexadecimal|is-plain-obj|longest-streak|markdown-table|mdast-util-find-and-replace|mdast-util-from-markdown|mdast-util-gfm|mdast-util-gfm-autolink-literal|mdast-util-gfm-footnote|mdast-util-gfm-strikethrough|mdast-util-gfm-table|mdast-util-gfm-task-list-item|mdast-util-mdx-expression|mdast-util-mdx-jsx|mdast-util-mdxjs-esm|mdast-util-phrasing|mdast-util-to-hast|mdast-util-to-markdown|mdast-util-to-string|micromark|micromark-core-commonmark|micromark-extension-gfm|micromark-extension-gfm-autolink-literal|micromark-extension-gfm-footnote|micromark-extension-gfm-strikethrough|micromark-extension-gfm-table|micromark-extension-gfm-tagfilter|micromark-extension-gfm-task-list-item|micromark-factory-destination|micromark-factory-label|micromark-factory-space|micromark-factory-title|micromark-factory-whitespace|micromark-util-character|micromark-util-chunked|micromark-util-classify-character|micromark-util-combine-extensions|micromark-util-decode-numeric-character-reference|micromark-util-decode-string|micromark-util-encode|micromark-util-html-tag-name|micromark-util-normalize-identifier|micromark-util-resolve-all|micromark-util-sanitize-uri|micromark-util-subtokenize|micromark-util-symbol|micromark-util-types|nanoid|parse-entities|parse5|property-information|react-markdown|remark-gfm|remark-parse|remark-rehype|remark-stringify|space-separated-tokens|stringify-entities|trim-lines|trough|unified|unist-util-is|unist-util-position|unist-util-stringify-position|unist-util-visit|unist-util-visit-parents|vfile|vfile-message|zwitch)/)',
  ]
  return cfg
}
